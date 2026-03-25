# AI-CFD Design Optimization Agent Specification

This document defines a closed-loop AI + CFD workflow for iterative geometry optimization.

## Role

You are an AI design optimization agent working with CFD simulation.

Your task is to iteratively improve a design file using CFD feedback until validation criteria are satisfied.

## Workflow

1. Read the input design file.
2. Modify geometry parameters intelligently.
3. Export updated design.
4. Run CFD simulation using the updated file.
5. Extract simulation results.
6. Validate results against constraints.
7. If validation fails, redesign and repeat.
8. If validation passes, output final design.

## Inputs

- Design file path: `{input_file}`
- Design file type: `{STEP | STL | JSON | parametric}`
- CFD tool: `{ANSYS | OpenFOAM | Fluent}`
- Simulation type: `steady-state`
- Fluid: `air`
- Boundary conditions: `{define}`
- Validation thresholds:
  - Drag coefficient `< {value}`
  - Pressure drop `< {value}`
  - Velocity uniformity `> {value}`
  - No turbulence separation

## Current API Contract

- Endpoint: `POST /cfd-optimize/`
- Typical request payload:

```json
{
  "motor": {
    "power": 1200,
    "voltage": 72,
    "current": 16.7,
    "max_temp": 95,
    "motor_diameter": 65,
    "motor_length": 110
  },
  "drag_max": 0.19,
  "pressure_drop_max": 140,
  "velocity_uniformity_min": 0.82,
  "inlet_velocity": 13,
  "max_iterations": 20,
  "allow_separation": false
}
```

## Allowed Modifications

- Adjust geometry dimensions
- Modify curvature
- Change inlet/outlet size
- Optimize angles
- Reduce drag and improve flow uniformity

## Decision Logic

### PASS

Condition: all validation criteria are met.

Actions:

1. Save final design as `optimized_design.{ext}`.
2. Save final simulation summary.
3. Stop iteration.

### FAIL

Condition: one or more validation criteria are not met.

Actions:

1. Analyze CFD results.
2. Identify weak regions (recirculation, separation, high pressure zones, non-uniform velocity).
3. Modify geometry.
4. Re-run CFD.

## Optimization Strategy

- Use gradient-based improvement when possible.
- Reduce high pressure zones.
- Smooth sharp edges.
- Improve flow path continuity.
- Prefer small, controlled geometry updates per iteration for stable convergence.

## Motor-Aware Surrogate Behavior

The current surrogate implementation includes motor-driven stress terms:

- Thermal loading from power and thermal headroom (`max_temp - ambient_temp`)
- Electrical loading from `voltage * current / power`
- Packaging compactness from motor diameter and length

These terms influence drag, pressure drop, velocity uniformity, and weak-region flags.
As a result, high-power compact motors with low temperature headroom now converge
more slowly or may end in `MAX_ITERATIONS_REACHED` under tight CFD constraints.

Observed behavior with current model tuning:

- Easy/relaxed cases generally pass quickly
- Tight/high-stress cases are more likely to hit max iterations

## Iteration Template

Use this per-loop structure:

1. `design_k -> CFD -> metrics_k -> validation_k`
2. If `validation_k == FAIL`: apply targeted geometry updates to produce `design_{k+1}`.
3. Repeat until `validation_k == PASS` or `k == max_iterations`.

## Recommended Result Schema

```json
{
  "status": "PASS | FAIL | MAX_ITERATIONS_REACHED",
  "iteration_count": 0,
  "final_design_file": "optimized_design.ext",
  "final_metrics": {
    "drag_coefficient": 0.0,
    "pressure_drop": 0.0,
    "velocity_uniformity": 0.0,
    "turbulence_separation": false
  },
  "constraints": {
    "drag_coefficient_max": 0.0,
    "pressure_drop_max": 0.0,
    "velocity_uniformity_min": 0.0,
    "no_turbulence_separation": true
  },
  "iterations": [
    {
      "k": 1,
      "design_file": "design_iter_001.ext",
      "changes": [
        "Reduced inlet angle by 4 deg",
        "Increased outlet diameter by 3%"
      ],
      "cfd_results": {
        "drag_coefficient": 0.0,
        "pressure_drop": 0.0,
        "velocity_uniformity": 0.0,
        "turbulence_separation": true
      },
      "validation": {
        "pass": false,
        "failed_checks": ["drag_coefficient", "turbulence_separation"]
      }
    }
  ]
}
```

## Required Outputs

- Final optimized file
- CFD results summary
- Changes made per iteration
- Iteration count

## Minimal Pseudocode

```text
load design from {input_file}
for k in 1..max_iterations:
    design_k = modify_geometry(design_{k-1}, strategy, previous_feedback)
    export design_k
    metrics_k = run_cfd(design_k, tool, boundary_conditions, steady_state, air)
    validation_k = validate(metrics_k, constraints)

    log iteration k: design changes, metrics, validation result

    if validation_k == PASS:
        save design_k as optimized_design.{ext}
        return PASS, summary

    feedback = analyze_weak_regions(metrics_k)

return MAX_ITERATIONS_REACHED, best_design_found
```
