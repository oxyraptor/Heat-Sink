"""
Closed-loop AI + CFD optimization workflow.

This module provides an iterative optimization agent that:
1) reads a design file,
2) modifies geometry parameters,
3) exports each design iteration,
4) runs CFD (external command or surrogate),
5) validates results,
6) repeats until pass or max iterations.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


SUPPORTED_FILE_TYPES = {"step", "stl", "json", "parametric"}


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass
class ValidationCriteria:
    drag_coefficient_max: float
    pressure_drop_max: float
    velocity_uniformity_min: float
    no_turbulence_separation: bool = True


@dataclass
class OptimizationConfig:
    input_file: Path
    file_type: str
    cfd_tool: str
    simulation_type: str
    fluid: str
    boundary_conditions: Dict[str, Any]
    validation: ValidationCriteria
    motor_specs: Dict[str, Any] = field(default_factory=dict)
    max_iterations: int = 20
    output_dir: Path = Path(".")
    learning_rate: float = 0.15
    command_template: Optional[str] = None
    include_iterations_in_response: bool = True
    history_limit: int = 25


@dataclass
class CFDResult:
    drag_coefficient: float
    pressure_drop: float
    velocity_uniformity: float
    turbulence_separation: bool
    weak_regions: List[str]
    raw: Dict[str, Any]


class DesignIO:
    """Read/export design files and parameter payloads."""

    @staticmethod
    def infer_file_type(file_path: Path) -> str:
        ext = file_path.suffix.lower().lstrip(".")
        if ext in {"step", "stp"}:
            return "step"
        if ext == "stl":
            return "stl"
        if ext == "json":
            return "json"
        return "parametric"

    @staticmethod
    def default_parameters() -> Dict[str, float]:
        return {
            "length": 1.0,
            "width": 0.32,
            "height": 0.22,
            "curvature": 0.45,
            "inlet_size": 0.12,
            "outlet_size": 0.14,
            "angle_deg": 18.0,
            "edge_radius": 0.018,
        }

    def read_design(self, file_path: Path, file_type: str) -> Dict[str, Any]:
        design: Dict[str, Any] = {
            "source_file": str(file_path),
            "file_type": file_type,
            "parameters": self.default_parameters(),
            "metadata": {},
        }

        if file_type in {"json", "parametric"}:
            with file_path.open("r", encoding="utf-8") as f:
                payload = json.load(f)
            if "parameters" in payload:
                design["parameters"].update(payload["parameters"])
                design["metadata"] = payload.get("metadata", {})
            else:
                # Accept flat parametric JSON files.
                design["parameters"].update(payload)
        else:
            # STEP/STL do not carry easy editable params. Use sidecar if present.
            sidecar = file_path.with_suffix(file_path.suffix + ".json")
            if sidecar.exists():
                with sidecar.open("r", encoding="utf-8") as f:
                    payload = json.load(f)
                design["parameters"].update(payload.get("parameters", payload))

        return design

    def export_design(
        self,
        design: Dict[str, Any],
        export_path: Path,
        file_type: str,
        source_geometry_file: Optional[Path],
    ) -> None:
        export_path.parent.mkdir(parents=True, exist_ok=True)

        if file_type in {"json", "parametric"}:
            with export_path.open("w", encoding="utf-8") as f:
                json.dump(design, f, indent=2)
            return

        # For STEP/STL, keep the geometry file and emit sidecar params.
        if source_geometry_file is not None and source_geometry_file.exists():
            shutil.copy2(source_geometry_file, export_path)
        params_out = export_path.with_suffix(export_path.suffix + ".json")
        with params_out.open("w", encoding="utf-8") as f:
            json.dump({"parameters": design["parameters"]}, f, indent=2)


class BaseCFDSolver:
    def run(
        self,
        design_file: Path,
        params: Dict[str, float],
        config: OptimizationConfig,
        iteration: int,
    ) -> CFDResult:
        raise NotImplementedError


class SurrogateCFDSolver(BaseCFDSolver):
    """Fast deterministic surrogate used when external CFD is unavailable."""

    @staticmethod
    def evaluate_params(
        params: Dict[str, float],
        boundary_conditions: Dict[str, Any],
        motor_specs: Optional[Dict[str, Any]] = None,
    ) -> CFDResult:
        motor_specs = motor_specs or {}
        length = params["length"]
        width = params["width"]
        height = params["height"]
        curvature = params["curvature"]
        inlet_size = params["inlet_size"]
        outlet_size = params["outlet_size"]
        angle_deg = params["angle_deg"]
        edge_radius = params["edge_radius"]

        inlet_velocity = float(boundary_conditions.get("inlet_velocity", 15.0))
        ambient_temp = float(boundary_conditions.get("ambient_temp", 25.0))

        # Support either API payload keys (power/voltage/current) or backend keys (rated_*).
        rated_power = float(motor_specs.get("rated_power", motor_specs.get("power", 1000.0)))
        rated_voltage = float(motor_specs.get("rated_voltage", motor_specs.get("voltage", 48.0)))
        rated_current = float(motor_specs.get("rated_current", motor_specs.get("current", 25.0)))
        max_temp = float(motor_specs.get("max_temp", 100.0))

        raw_diameter = float(motor_specs.get("motor_diameter", 0.06))
        raw_length = float(motor_specs.get("motor_length", 0.12))
        # Accept either meters or millimeters.
        motor_diameter_m = raw_diameter / 1000.0 if raw_diameter > 1.0 else raw_diameter
        motor_length_m = raw_length / 1000.0 if raw_length > 1.0 else raw_length

        area_ratio = outlet_size / max(inlet_size, 1e-6)
        slenderness = length / max(width, 1e-6)
        blockage = height / max(width, 1e-6)
        sharpness = 1.0 / max(edge_radius, 1e-6)

        # Motor-induced flow stress: high power, low thermal headroom, compact motors are harder to cool.
        thermal_headroom = max(max_temp - ambient_temp, 5.0)
        heat_stress = _clamp((rated_power / thermal_headroom) / 28.0, 0.7, 3.5)
        compactness = _clamp(
            0.5 * (0.06 / max(motor_diameter_m, 0.02))
            + 0.5 * (0.12 / max(motor_length_m, 0.04)),
            0.6,
            2.8,
        )
        electrical_stress = _clamp(
            (rated_voltage * rated_current) / max(rated_power, 1.0),
            0.7,
            2.2,
        )
        motor_stress = _clamp(
            (0.58 * heat_stress) + (0.30 * compactness) + (0.12 * electrical_stress),
            0.75,
            3.2,
        )

        drag = (
            0.11
            + 0.018 * (angle_deg - 10.0) ** 2 / 100.0
            + 0.035 * max(0.0, 0.58 - curvature)
            + 0.03 * abs(area_ratio - 1.15)
            + 0.025 * max(0.0, blockage - 0.55)
            + 0.002 * (inlet_velocity / 10.0)
            + 0.00035 * sharpness
            + 0.010 * (motor_stress - 1.0)
        )

        pressure_drop = (
            45.0
            + 140.0 * max(0.0, 0.58 - inlet_size)
            + 110.0 * abs(area_ratio - 1.15)
            + 70.0 * max(0.0, blockage - 0.65)
            + 20.0 * max(0.0, slenderness - 3.0)
            + 0.8 * inlet_velocity
            + 22.0 * max(0.0, motor_stress - 1.0)
            + 10.0 * max(0.0, compactness - 1.0)
        )

        uniformity = (
            0.92
            - 0.018 * abs(angle_deg - 11.0)
            - 0.09 * max(0.0, 0.62 - curvature)
            - 0.06 * abs(area_ratio - 1.15)
            - 0.05 * max(0.0, blockage - 0.72)
            - 0.0007 * max(0.0, pressure_drop - 85.0)
            + 0.008 * min(edge_radius / 0.02, 1.5)
            - 0.030 * max(0.0, motor_stress - 1.0)
        )
        uniformity = _clamp(uniformity, 0.05, 0.99)

        separation = bool(
            angle_deg > 18.0
            or curvature < 0.40
            or area_ratio < 0.92
            or blockage > 0.88
            or (motor_stress > 1.8 and angle_deg > 14.0)
        )

        weak_regions: List[str] = []
        if drag > 0.18:
            weak_regions.append("high_drag_zone")
        if pressure_drop > 95.0:
            weak_regions.append("high_pressure_zone")
        if uniformity < 0.86:
            weak_regions.append("non_uniform_velocity")
        if motor_stress > 1.5:
            weak_regions.append("thermal_stress_zone")
        if separation:
            weak_regions.append("flow_separation")

        return CFDResult(
            drag_coefficient=float(drag),
            pressure_drop=float(pressure_drop),
            velocity_uniformity=float(uniformity),
            turbulence_separation=separation,
            weak_regions=weak_regions,
            raw={
                "area_ratio": area_ratio,
                "slenderness": slenderness,
                "blockage": blockage,
                "motor_stress": motor_stress,
                "heat_stress": heat_stress,
                "compactness": compactness,
            },
        )

    def run(
        self,
        design_file: Path,
        params: Dict[str, float],
        config: OptimizationConfig,
        iteration: int,
    ) -> CFDResult:
        _ = design_file
        _ = iteration
        return self.evaluate_params(params, config.boundary_conditions, config.motor_specs)


class CommandCFDSolver(BaseCFDSolver):
    """Run an external CFD command that writes metrics JSON to disk."""

    def __init__(self, command_template: str):
        self.command_template = command_template

    def run(
        self,
        design_file: Path,
        params: Dict[str, float],
        config: OptimizationConfig,
        iteration: int,
    ) -> CFDResult:
        output_json = config.output_dir / f"cfd_results_iter_{iteration:03d}.json"
        command = self.command_template.format(
            input=str(design_file),
            output=str(output_json),
            tool=config.cfd_tool,
            simulation_type=config.simulation_type,
            fluid=config.fluid,
        )

        env = {
            "CFD_BOUNDARY_CONDITIONS_JSON": json.dumps(config.boundary_conditions),
            "CFD_DESIGN_PARAMETERS_JSON": json.dumps(params),
        }
        completed = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            env={**os.environ, **env},
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"CFD command failed: {completed.stderr.strip() or completed.stdout.strip()}"
            )
        if not output_json.exists():
            raise RuntimeError(
                "CFD command completed but did not produce output JSON file"
            )

        with output_json.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        return CFDResult(
            drag_coefficient=float(payload["drag_coefficient"]),
            pressure_drop=float(payload["pressure_drop"]),
            velocity_uniformity=float(payload["velocity_uniformity"]),
            turbulence_separation=bool(payload["turbulence_separation"]),
            weak_regions=list(payload.get("weak_regions", [])),
            raw=payload,
        )


class CFDOptimizationAgent:
    def __init__(self, config: OptimizationConfig, solver: Optional[BaseCFDSolver] = None):
        self.config = config
        self.io = DesignIO()
        self.solver = solver or self._build_solver()
        self.bounds = {
            "length": (0.5, 1.6),
            "width": (0.18, 0.7),
            "height": (0.08, 0.45),
            "curvature": (0.2, 0.95),
            "inlet_size": (0.06, 0.28),
            "outlet_size": (0.06, 0.34),
            "angle_deg": (2.0, 28.0),
            "edge_radius": (0.002, 0.05),
        }

    def _build_solver(self) -> BaseCFDSolver:
        if self.config.command_template:
            return CommandCFDSolver(self.config.command_template)
        return SurrogateCFDSolver()

    def _validate(self, metrics: CFDResult) -> Tuple[bool, List[str]]:
        failed: List[str] = []
        if metrics.drag_coefficient >= self.config.validation.drag_coefficient_max:
            failed.append("drag_coefficient")
        if metrics.pressure_drop >= self.config.validation.pressure_drop_max:
            failed.append("pressure_drop")
        if metrics.velocity_uniformity <= self.config.validation.velocity_uniformity_min:
            failed.append("velocity_uniformity")
        if (
            self.config.validation.no_turbulence_separation
            and metrics.turbulence_separation
        ):
            failed.append("turbulence_separation")
        return (len(failed) == 0, failed)

    @staticmethod
    def _objective(metrics: CFDResult, validation: ValidationCriteria) -> float:
        return (
            max(0.0, metrics.drag_coefficient - validation.drag_coefficient_max) * 100.0
            + max(0.0, metrics.pressure_drop - validation.pressure_drop_max) / 10.0
            + max(0.0, validation.velocity_uniformity_min - metrics.velocity_uniformity) * 150.0
            + (30.0 if metrics.turbulence_separation else 0.0)
        )

    def _gradient_step(
        self,
        params: Dict[str, float],
        base_metrics: CFDResult,
    ) -> Dict[str, float]:
        if not isinstance(self.solver, SurrogateCFDSolver):
            return params.copy()

        new_params = params.copy()
        base_objective = self._objective(base_metrics, self.config.validation)
        eps_ratio = 0.03

        for name, (low, high) in self.bounds.items():
            step = max((high - low) * eps_ratio, 1e-4)
            p_plus = params.copy()
            p_minus = params.copy()
            p_plus[name] = _clamp(params[name] + step, low, high)
            p_minus[name] = _clamp(params[name] - step, low, high)

            m_plus = self.solver.evaluate_params(
                p_plus,
                self.config.boundary_conditions,
                self.config.motor_specs,
            )
            m_minus = self.solver.evaluate_params(
                p_minus,
                self.config.boundary_conditions,
                self.config.motor_specs,
            )

            obj_plus = self._objective(m_plus, self.config.validation)
            obj_minus = self._objective(m_minus, self.config.validation)
            grad = (obj_plus - obj_minus) / max(p_plus[name] - p_minus[name], 1e-9)

            scaled_update = -self.config.learning_rate * grad * (high - low) * 0.05
            candidate = params[name] + scaled_update
            new_params[name] = _clamp(candidate, low, high)

        if self._objective(base_metrics, self.config.validation) == 0.0 and base_objective == 0.0:
            return params.copy()
        return new_params

    def _heuristic_step(
        self,
        params: Dict[str, float],
        metrics: CFDResult,
    ) -> Tuple[Dict[str, float], List[str]]:
        updated = params.copy()
        changes: List[str] = []

        if metrics.drag_coefficient >= self.config.validation.drag_coefficient_max:
            updated["curvature"] += 0.05
            updated["edge_radius"] += 0.003
            updated["angle_deg"] -= 1.5
            changes.append("Increased curvature and edge radius to reduce drag")

        if metrics.pressure_drop >= self.config.validation.pressure_drop_max:
            updated["inlet_size"] += 0.01
            updated["outlet_size"] += 0.012
            updated["height"] -= 0.01
            changes.append("Adjusted inlet/outlet and reduced blockage to lower pressure drop")

        if metrics.velocity_uniformity <= self.config.validation.velocity_uniformity_min:
            updated["curvature"] += 0.04
            updated["angle_deg"] = 11.0
            updated["outlet_size"] = max(updated["outlet_size"], updated["inlet_size"] * 1.1)
            changes.append("Improved flow-path continuity for better velocity uniformity")

        if metrics.turbulence_separation:
            updated["angle_deg"] -= 2.5
            updated["curvature"] += 0.06
            changes.append("Reduced aggressive turning to suppress turbulence separation")

        if "high_pressure_zone" in metrics.weak_regions:
            updated["inlet_size"] += 0.008
            changes.append("Expanded inlet region to relieve local high pressure")

        if "non_uniform_velocity" in metrics.weak_regions:
            updated["outlet_size"] += 0.008
            changes.append("Expanded outlet region to improve velocity profile")

        for name, (low, high) in self.bounds.items():
            updated[name] = _clamp(updated[name], low, high)

        return updated, changes

    def _improve_design(
        self,
        params: Dict[str, float],
        metrics: CFDResult,
    ) -> Tuple[Dict[str, float], List[str]]:
        grad_params = self._gradient_step(params, metrics)
        next_params, notes = self._heuristic_step(grad_params, metrics)
        if not notes:
            notes = ["Applied conservative parameter smoothing update"]
            next_params["curvature"] = _clamp(next_params["curvature"] + 0.01, *self.bounds["curvature"])
            next_params["angle_deg"] = _clamp(next_params["angle_deg"] - 0.5, *self.bounds["angle_deg"])
        return next_params, notes

    @staticmethod
    def _has_parameter_change(
        old_params: Dict[str, float],
        new_params: Dict[str, float],
        tol: float = 1e-9,
    ) -> bool:
        for key, old_val in old_params.items():
            if abs(float(new_params.get(key, old_val)) - float(old_val)) > tol:
                return True
        return False

    def _plateau_escape_step(
        self,
        params: Dict[str, float],
        failed_checks: List[str],
        iteration: int,
    ) -> Dict[str, float]:
        escaped = params.copy()
        # Deterministic nudge magnitude to avoid random behavior while still escaping local plateaus.
        mag = 0.004 + (0.001 * (iteration % 3))

        if "pressure_drop" in failed_checks:
            escaped["inlet_size"] += mag * 2.0
            escaped["outlet_size"] += mag * 2.2
            escaped["height"] -= mag * 2.5
            escaped["width"] += mag * 2.0
        if "velocity_uniformity" in failed_checks:
            escaped["curvature"] += mag * 3.0
            escaped["angle_deg"] -= 1.2
            escaped["edge_radius"] += mag
        if "drag_coefficient" in failed_checks:
            escaped["angle_deg"] -= 0.9
            escaped["edge_radius"] += mag * 1.5
            escaped["curvature"] += mag * 1.8

        # Fallback nudge if failures are not specific or all variables are saturated.
        if not failed_checks:
            escaped["curvature"] += mag
            escaped["angle_deg"] -= 0.6
            escaped["length"] -= mag * 2.0

        for name, (low, high) in self.bounds.items():
            escaped[name] = _clamp(escaped[name], low, high)
        return escaped

    def run(self) -> Dict[str, Any]:
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        design = self.io.read_design(self.config.input_file, self.config.file_type)
        current_params = design["parameters"].copy()
        source_file = self.config.input_file
        ext = self.config.input_file.suffix.lstrip(".") or "json"

        history: List[Dict[str, Any]] = []
        best_entry: Optional[Dict[str, Any]] = None
        best_score = math.inf

        def response_iterations() -> Tuple[List[Dict[str, Any]], bool]:
            if not self.config.include_iterations_in_response:
                return [], bool(history)
            safe_limit = max(1, int(self.config.history_limit))
            if len(history) <= safe_limit:
                return history, False
            return history[-safe_limit:], True

        for k in range(1, self.config.max_iterations + 1):
            iter_name = f"design_iter_{k:03d}.{ext}"
            iter_file = self.config.output_dir / iter_name

            iter_design = {
                "parameters": current_params,
                "metadata": {
                    "iteration": k,
                    "simulation_type": self.config.simulation_type,
                    "fluid": self.config.fluid,
                    "cfd_tool": self.config.cfd_tool,
                },
            }
            self.io.export_design(
                iter_design,
                export_path=iter_file,
                file_type=self.config.file_type,
                source_geometry_file=source_file,
            )

            metrics = self.solver.run(iter_file, current_params, self.config, k)
            is_pass, failed_checks = self._validate(metrics)

            entry = {
                "k": k,
                "design_file": str(iter_file),
                "design_parameters": current_params.copy(),
                "changes": ["Initial design"] if k == 1 else [],
                "cfd_results": {
                    "drag_coefficient": metrics.drag_coefficient,
                    "pressure_drop": metrics.pressure_drop,
                    "velocity_uniformity": metrics.velocity_uniformity,
                    "turbulence_separation": metrics.turbulence_separation,
                    "weak_regions": metrics.weak_regions,
                },
                "validation": {
                    "pass": is_pass,
                    "failed_checks": failed_checks,
                },
            }

            score = self._objective(metrics, self.config.validation)
            if score < best_score:
                best_score = score
                best_entry = {
                    "entry": entry,
                    "params": current_params.copy(),
                    "metrics": metrics,
                }

            if is_pass:
                final_name = f"optimized_design.{ext}"
                final_file = self.config.output_dir / final_name
                self.io.export_design(
                    {"parameters": current_params, "metadata": {"status": "PASS"}},
                    export_path=final_file,
                    file_type=self.config.file_type,
                    source_geometry_file=source_file,
                )
                history.append(entry)
                returned_iterations, is_truncated = response_iterations()
                summary = {
                    "status": "PASS",
                    "iteration_count": k,
                    "final_design_file": str(final_file),
                    "final_parameters": current_params.copy(),
                    "final_metrics": entry["cfd_results"],
                    "constraints": {
                        "drag_coefficient_max": self.config.validation.drag_coefficient_max,
                        "pressure_drop_max": self.config.validation.pressure_drop_max,
                        "velocity_uniformity_min": self.config.validation.velocity_uniformity_min,
                        "no_turbulence_separation": self.config.validation.no_turbulence_separation,
                    },
                    "iterations": returned_iterations,
                    "iterations_returned": len(returned_iterations),
                    "iterations_truncated": is_truncated,
                }
                self._write_summary(summary)
                return summary

            next_params, notes = self._improve_design(current_params, metrics)
            if not self._has_parameter_change(current_params, next_params):
                next_params = self._plateau_escape_step(current_params, failed_checks, k)
                notes.append("Applied plateau-escape nudge to continue geometry updates")
            entry["changes"] = notes if k > 1 else entry["changes"] + notes
            history.append(entry)
            current_params = next_params

        # Max iterations reached: persist best known candidate.
        if best_entry is None:
            raise RuntimeError("Optimization failed before any iteration result was produced")

        final_name = f"optimized_design.{ext}"
        final_file = self.config.output_dir / final_name
        self.io.export_design(
            {"parameters": best_entry["params"], "metadata": {"status": "MAX_ITERATIONS_REACHED"}},
            export_path=final_file,
            file_type=self.config.file_type,
            source_geometry_file=source_file,
        )
        returned_iterations, is_truncated = response_iterations()
        summary = {
            "status": "MAX_ITERATIONS_REACHED",
            "iteration_count": self.config.max_iterations,
            "final_design_file": str(final_file),
            "final_parameters": best_entry["params"].copy(),
            "final_metrics": {
                "drag_coefficient": best_entry["metrics"].drag_coefficient,
                "pressure_drop": best_entry["metrics"].pressure_drop,
                "velocity_uniformity": best_entry["metrics"].velocity_uniformity,
                "turbulence_separation": best_entry["metrics"].turbulence_separation,
                "weak_regions": best_entry["metrics"].weak_regions,
            },
            "constraints": {
                "drag_coefficient_max": self.config.validation.drag_coefficient_max,
                "pressure_drop_max": self.config.validation.pressure_drop_max,
                "velocity_uniformity_min": self.config.validation.velocity_uniformity_min,
                "no_turbulence_separation": self.config.validation.no_turbulence_separation,
            },
            "iterations": returned_iterations,
            "iterations_returned": len(returned_iterations),
            "iterations_truncated": is_truncated,
        }
        self._write_summary(summary)
        return summary

    def _write_summary(self, summary: Dict[str, Any]) -> None:
        summary_path = self.config.output_dir / "cfd_optimization_summary.json"
        with summary_path.open("w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)


def _parse_boundary_conditions(raw: str) -> Dict[str, Any]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("Boundary conditions must be valid JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("Boundary conditions JSON must decode to an object")
    return payload


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AI-CFD closed-loop optimization")
    parser.add_argument("--input-file", required=True, help="Design file path")
    parser.add_argument(
        "--file-type",
        choices=sorted(SUPPORTED_FILE_TYPES),
        help="Input design type. If omitted, inferred from extension.",
    )
    parser.add_argument(
        "--cfd-tool",
        default="surrogate",
        help="CFD tool name (ANSYS/OpenFOAM/Fluent/surrogate/custom)",
    )
    parser.add_argument("--simulation-type", default="steady-state")
    parser.add_argument("--fluid", default="air")
    parser.add_argument(
        "--boundary-conditions",
        default='{"inlet_velocity": 15.0, "outlet_pressure": 0.0}',
        help="Boundary conditions as JSON object",
    )
    parser.add_argument("--drag-max", type=float, required=True)
    parser.add_argument("--pressure-drop-max", type=float, required=True)
    parser.add_argument("--velocity-uniformity-min", type=float, required=True)
    parser.add_argument("--allow-separation", action="store_true")
    parser.add_argument("--max-iterations", type=int, default=20)
    parser.add_argument("--learning-rate", type=float, default=0.15)
    parser.add_argument("--output-dir", default=".")
    parser.add_argument(
        "--command-template",
        help=(
            "External CFD command template. Supported placeholders: "
            "{input}, {output}, {tool}, {simulation_type}, {fluid}"
        ),
    )
    return parser


def run_from_args(args: argparse.Namespace) -> Dict[str, Any]:
    input_file = Path(args.input_file)
    if not input_file.exists():
        raise FileNotFoundError(f"Input design file not found: {input_file}")

    file_type = args.file_type or DesignIO.infer_file_type(input_file)
    if file_type not in SUPPORTED_FILE_TYPES:
        raise ValueError(f"Unsupported file type: {file_type}")

    boundary_conditions = _parse_boundary_conditions(args.boundary_conditions)
    validation = ValidationCriteria(
        drag_coefficient_max=args.drag_max,
        pressure_drop_max=args.pressure_drop_max,
        velocity_uniformity_min=args.velocity_uniformity_min,
        no_turbulence_separation=(not args.allow_separation),
    )
    config = OptimizationConfig(
        input_file=input_file,
        file_type=file_type,
        cfd_tool=args.cfd_tool,
        simulation_type=args.simulation_type,
        fluid=args.fluid,
        boundary_conditions=boundary_conditions,
        motor_specs={},
        validation=validation,
        max_iterations=args.max_iterations,
        output_dir=Path(args.output_dir),
        learning_rate=args.learning_rate,
        command_template=args.command_template,
    )

    agent = CFDOptimizationAgent(config=config)
    return agent.run()


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()
    summary = run_from_args(args)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
