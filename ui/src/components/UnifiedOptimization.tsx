import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import {
  Play,
  AlertCircle,
  CheckCircle2,
  Clock,
  Zap,
  Waves,
} from "lucide-react";

interface MotorParams {
  motor_type: string;
  rated_power: number;
  rated_voltage: number;
  rated_current: number;
  max_temp: number;
  motor_diameter: number;
  motor_length: number;
}

interface CFDParams {
  dragMax: number;
  pressureDropMax: number;
  velocityUniformityMin: number;
  inletVelocity: number;
  maxIterations: number;
  allowSeparation: boolean;
}

interface DesignPreview {
  length: number;
  width: number;
  height: number;
  curvature: number;
  inlet_size: number;
  outlet_size: number;
  angle_deg: number;
  edge_radius: number;
}

interface CFDResult {
  status: "PASS" | "MAX_ITERATIONS_REACHED" | "FAILED";
  iteration_count: number;
  final_parameters?: Partial<DesignPreview> & {
    n_fins?: number;
    s?: number;
    t_tip?: number;
    taper_angle?: number;
    geometry_type?: string;
    alloy?: string;
  };
  final_design?: {
    parameters?: Partial<DesignPreview> & {
      n_fins?: number;
      s?: number;
      t_tip?: number;
      taper_angle?: number;
      geometry_type?: string;
      alloy?: string;
    };
  };
  final_metrics?: {
    drag_coefficient: number;
    pressure_drop: number;
    velocity_uniformity: number;
    turbulence_separation: boolean;
  };
  iterations?: Array<{
    k: number;
    design_parameters: DesignPreview;
    changes: string[];
    cfd_results: {
      drag_coefficient: number;
      pressure_drop: number;
      velocity_uniformity: number;
    };
    validation: {
      pass: boolean;
      failed_checks: string[];
    };
  }>;
}

interface UnifiedOptimizationProps {
  apiBaseUrls: string[];
}

interface RecommendResult {
  valid?: boolean;
  geometry?: string;
  alloy?: string;
  number_of_fins?: number;
  parameters?: {
    N?: number;
    n?: number;
    H?: number;
    h?: number;
    s?: number;
    t_base?: number;
    tb?: number;
    type?: string;
    t_tip?: number;
    taper_angle?: number;
  };
  parameters_mm?: {
    N?: number;
    H?: number;
    s?: number;
    t_base?: number;
    t_tip?: number;
  };
  temperature?: number;
  thermal_resistance?: number;
  mass?: number;
  alloy_properties?: {
    thermal_conductivity: number;
    density: number;
    cost_per_kg: number;
  };
}

export function UnifiedOptimization({ apiBaseUrls }: UnifiedOptimizationProps) {
  // Motor Parameters
  const [motorData, setMotorData] = useState<MotorParams>({
    motor_type: "Servo",
    rated_power: 1200,
    rated_voltage: 72,
    rated_current: 16.7,
    max_temp: 95,
    motor_diameter: 65,
    motor_length: 110,
  });

  // CFD Parameters
  const [cfdParams, setCFDParams] = useState<CFDParams>({
    dragMax: 0.19,
    pressureDropMax: 140,
    velocityUniformityMin: 0.82,
    inletVelocity: 13,
    maxIterations: 20,
    allowSeparation: false,
  });

  const [results, setResults] = useState<CFDResult | null>(null);
  const [recommendResults, setRecommendResults] =
    useState<RecommendResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showIterations, setShowIterations] = useState(false);
  const [visibleIterationCount, setVisibleIterationCount] = useState(20);

  const postToFirstAvailableBaseUrl = async (
    path: string,
    payload: unknown,
    signal: AbortSignal,
  ): Promise<Response | null> => {
    for (const baseUrl of apiBaseUrls) {
      try {
        const response = await fetch(`${baseUrl}${path}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
          signal,
        });
        if (response.ok) {
          return response;
        }
      } catch {
        // Continue trying next backend URL.
      }
    }
    return null;
  };

  const handleMotorChange = (field: keyof MotorParams, value: any) => {
    setMotorData((prev) => ({ ...prev, [field]: value }));
  };

  const handleCFDChange = (field: keyof CFDParams, value: any) => {
    setCFDParams((prev) => ({ ...prev, [field]: value }));
  };

  const handleRunOptimization = async () => {
    setLoading(true);
    setError(null);
    setResults(null);
    setRecommendResults(null);

    try {
      const controller = new AbortController();
      const timeoutId = window.setTimeout(() => controller.abort(), 300000);

      const payload = {
        motor: motorData,
        drag_max: cfdParams.dragMax,
        pressure_drop_max: cfdParams.pressureDropMax,
        velocity_uniformity_min: cfdParams.velocityUniformityMin,
        inlet_velocity: cfdParams.inletVelocity,
        max_iterations: cfdParams.maxIterations,
        allow_separation: cfdParams.allowSeparation,
        history_limit: 30,
      };

      const recommendPayload = {
        motor: {
          ...motorData,
          motor_diameter: motorData.motor_diameter / 1000, // Convert mm to m
          motor_length: motorData.motor_length / 1000, // Convert mm to m
        },
        environment: {
          ambient_temp: 25,
          airflow_type: "Forced",
          air_velocity: cfdParams.inletVelocity,
        },
        constraints: {
          max_height: 0.1,
          min_fin_thickness: 0.001,
          max_weight: null,
        },
        preferred_alloy: null,
      };

      const [cfdResponse, recommendResponse] = await Promise.all([
        postToFirstAvailableBaseUrl(
          "/cfd-optimize/",
          payload,
          controller.signal,
        ),
        postToFirstAvailableBaseUrl(
          "/recommend/",
          recommendPayload,
          controller.signal,
        ),
      ]);

      window.clearTimeout(timeoutId);

      if (!cfdResponse) {
        throw new Error("CFD optimization failed");
      }

      const data = (await cfdResponse.json()) as CFDResult;
      setResults(data);
      setShowIterations(true);
      setVisibleIterationCount(20);

      if (recommendResponse) {
        const recommendData =
          (await recommendResponse.json()) as RecommendResult;
        setRecommendResults(recommendData);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">
          Unified Heat Sink Optimizer
        </h2>
        <p className="text-slate-400">
          Configure motor and CFD parameters, then run optimization and review
          results
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        <motion.div
          initial={{ opacity: 0, x: -16 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4 }}
          className="lg:col-span-3"
        >
          <Card className="bg-slate-800 border-slate-700 lg:sticky lg:top-4">
            <CardHeader className="pb-3">
              <CardTitle className="text-white text-lg flex items-center gap-2">
                <Zap className="w-5 h-5" />
                <Waves className="w-5 h-5" />
                Configuration
              </CardTitle>
              <CardDescription className="text-slate-400">
                Vertical configuration panel on the left
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="space-y-3">
                <p className="text-slate-300 text-xs font-semibold uppercase tracking-wide">
                  Motor
                </p>
                <div>
                  <Label htmlFor="power" className="text-slate-300 text-xs">
                    Power (W)
                  </Label>
                  <Input
                    id="power"
                    type="number"
                    value={motorData.rated_power}
                    onChange={(e) =>
                      handleMotorChange(
                        "rated_power",
                        parseFloat(e.target.value),
                      )
                    }
                    className="bg-slate-700 border-slate-600 text-white text-sm"
                  />
                </div>
                <div>
                  <Label htmlFor="voltage" className="text-slate-300 text-xs">
                    Voltage (V)
                  </Label>
                  <Input
                    id="voltage"
                    type="number"
                    value={motorData.rated_voltage}
                    onChange={(e) =>
                      handleMotorChange(
                        "rated_voltage",
                        parseFloat(e.target.value),
                      )
                    }
                    className="bg-slate-700 border-slate-600 text-white text-sm"
                  />
                </div>
                <div>
                  <Label htmlFor="current" className="text-slate-300 text-xs">
                    Current (A)
                  </Label>
                  <Input
                    id="current"
                    type="number"
                    value={motorData.rated_current}
                    onChange={(e) =>
                      handleMotorChange(
                        "rated_current",
                        parseFloat(e.target.value),
                      )
                    }
                    className="bg-slate-700 border-slate-600 text-white text-sm"
                  />
                </div>
                <div>
                  <Label htmlFor="max-temp" className="text-slate-300 text-xs">
                    Max Temp (°C)
                  </Label>
                  <Input
                    id="max-temp"
                    type="number"
                    value={motorData.max_temp}
                    onChange={(e) =>
                      handleMotorChange("max_temp", parseFloat(e.target.value))
                    }
                    className="bg-slate-700 border-slate-600 text-white text-sm"
                  />
                </div>
                <div>
                  <Label htmlFor="motor-dia" className="text-slate-300 text-xs">
                    Diameter (mm)
                  </Label>
                  <Input
                    id="motor-dia"
                    type="number"
                    value={motorData.motor_diameter}
                    onChange={(e) =>
                      handleMotorChange(
                        "motor_diameter",
                        parseFloat(e.target.value),
                      )
                    }
                    className="bg-slate-700 border-slate-600 text-white text-sm"
                  />
                </div>
                <div>
                  <Label htmlFor="motor-len" className="text-slate-300 text-xs">
                    Length (mm)
                  </Label>
                  <Input
                    id="motor-len"
                    type="number"
                    value={motorData.motor_length}
                    onChange={(e) =>
                      handleMotorChange(
                        "motor_length",
                        parseFloat(e.target.value),
                      )
                    }
                    className="bg-slate-700 border-slate-600 text-white text-sm"
                  />
                </div>
              </div>

              <div className="space-y-3">
                <p className="text-slate-300 text-xs font-semibold uppercase tracking-wide">
                  CFD
                </p>
                <div>
                  <Label htmlFor="drag-max" className="text-slate-300 text-xs">
                    Max Drag
                  </Label>
                  <Input
                    id="drag-max"
                    type="number"
                    min={0.1}
                    max={0.3}
                    step={0.01}
                    value={cfdParams.dragMax}
                    onChange={(e) =>
                      handleCFDChange("dragMax", parseFloat(e.target.value))
                    }
                    className="bg-slate-700 border-slate-600 text-white text-sm"
                  />
                </div>
                <div>
                  <Label
                    htmlFor="pressure-drop"
                    className="text-slate-300 text-xs"
                  >
                    Max Pressure Drop
                  </Label>
                  <Input
                    id="pressure-drop"
                    type="number"
                    min={80}
                    max={200}
                    step={5}
                    value={cfdParams.pressureDropMax}
                    onChange={(e) =>
                      handleCFDChange(
                        "pressureDropMax",
                        parseFloat(e.target.value),
                      )
                    }
                    className="bg-slate-700 border-slate-600 text-white text-sm"
                  />
                </div>
                <div>
                  <Label
                    htmlFor="velocity-uniformity"
                    className="text-slate-300 text-xs"
                  >
                    Min Velocity Uniformity
                  </Label>
                  <Input
                    id="velocity-uniformity"
                    type="number"
                    min={0.7}
                    max={0.95}
                    step={0.01}
                    value={cfdParams.velocityUniformityMin}
                    onChange={(e) =>
                      handleCFDChange(
                        "velocityUniformityMin",
                        parseFloat(e.target.value),
                      )
                    }
                    className="bg-slate-700 border-slate-600 text-white text-sm"
                  />
                </div>
                <div>
                  <Label
                    htmlFor="inlet-velocity"
                    className="text-slate-300 text-xs"
                  >
                    Inlet Velocity (m/s)
                  </Label>
                  <Input
                    id="inlet-velocity"
                    type="number"
                    value={cfdParams.inletVelocity}
                    onChange={(e) =>
                      handleCFDChange(
                        "inletVelocity",
                        parseFloat(e.target.value),
                      )
                    }
                    className="bg-slate-700 border-slate-600 text-white text-sm"
                  />
                </div>
                <div>
                  <Label
                    htmlFor="max-iterations"
                    className="text-slate-300 text-xs"
                  >
                    Max Iterations
                  </Label>
                  <Input
                    id="max-iterations"
                    type="number"
                    value={cfdParams.maxIterations}
                    onChange={(e) =>
                      handleCFDChange("maxIterations", parseInt(e.target.value))
                    }
                    className="bg-slate-700 border-slate-600 text-white text-sm"
                  />
                </div>

                <div className="flex items-center gap-2 pt-1">
                  <input
                    id="allow-separation"
                    type="checkbox"
                    checked={cfdParams.allowSeparation}
                    onChange={() =>
                      handleCFDChange(
                        "allowSeparation",
                        !cfdParams.allowSeparation,
                      )
                    }
                    className="rounded border-slate-600 bg-slate-700"
                  />
                  <Label
                    htmlFor="allow-separation"
                    className="text-slate-300 text-xs cursor-pointer"
                  >
                    Allow Turbulence Separation
                  </Label>
                </div>
              </div>

              <Button
                onClick={handleRunOptimization}
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white"
              >
                <Play className="w-4 h-4 mr-2" />
                {loading ? "Running..." : "Run Optimization"}
              </Button>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="lg:col-span-9 space-y-6 min-w-0"
        >
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <Card className="bg-red-900/20 border-red-700">
                  <CardContent className="pt-6 flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-red-400">Error</p>
                      <p className="text-red-300 text-sm">{error}</p>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {results && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <Card className="bg-slate-800 border-slate-700">
                  <CardHeader>
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <CardTitle className="text-white flex items-center gap-2">
                        {results.status === "PASS" ? (
                          <>
                            <CheckCircle2 className="w-5 h-5 text-green-500" />
                            Optimization Passed
                          </>
                        ) : (
                          <>
                            <Clock className="w-5 h-5 text-yellow-500" />
                            Max Iterations Reached
                          </>
                        )}
                      </CardTitle>
                      <span className="text-slate-400 text-sm">
                        {results.iteration_count} iterations
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4 w-full max-w-full overflow-x-hidden">
                    {(() => {
                      type AnalysisParams = Partial<DesignPreview> & {
                        n_fins?: number;
                        s?: number;
                        t_tip?: number;
                        taper_angle?: number;
                        geometry_type?: string;
                        alloy?: string;
                      };

                      const finalDesignParams: AnalysisParams | undefined =
                        (results.final_parameters as
                          | AnalysisParams
                          | undefined) ||
                        (results.final_design?.parameters as
                          | AnalysisParams
                          | undefined) ||
                        (results.iterations && results.iterations.length > 0
                          ? (results.iterations[results.iterations.length - 1]
                              .design_parameters as AnalysisParams)
                          : undefined);

                      if (!finalDesignParams) return null;

                      const validDesign =
                        recommendResults?.valid ?? results.status === "PASS";
                      const geometryType =
                        recommendResults?.geometry ||
                        recommendResults?.parameters?.type ||
                        finalDesignParams.geometry_type ||
                        (((finalDesignParams.angle_deg ?? 0) as number) > 0
                          ? "Trapezoidal"
                          : "Rectangular");
                      const finHeightMm =
                        recommendResults?.parameters_mm?.H !== undefined
                          ? recommendResults.parameters_mm.H
                          : recommendResults?.parameters?.h !== undefined
                            ? recommendResults.parameters.h * 1000
                            : recommendResults?.parameters?.H !== undefined
                              ? recommendResults.parameters.H * 1000
                              : ((finalDesignParams.height ?? 0) as number) *
                                1000;
                      const finSpacingMm =
                        recommendResults?.parameters_mm?.s !== undefined
                          ? recommendResults.parameters_mm.s
                          : recommendResults?.parameters?.s !== undefined
                            ? recommendResults.parameters.s * 1000
                            : finalDesignParams.s !== undefined
                              ? ((finalDesignParams.s ?? 0) as number) * 1000
                              : ((finalDesignParams.inlet_size ??
                                  0) as number) * 1000;
                      const tipThicknessMm =
                        recommendResults?.parameters_mm?.t_tip !== undefined
                          ? recommendResults.parameters_mm.t_tip
                          : recommendResults?.parameters?.t_tip !== undefined
                            ? recommendResults.parameters.t_tip * 1000
                            : finalDesignParams.t_tip !== undefined
                              ? ((finalDesignParams.t_tip ?? 0) as number) *
                                1000
                              : ((finalDesignParams.edge_radius ??
                                  0) as number) * 1000;
                      const taperAngle =
                        recommendResults?.parameters?.taper_angle !== undefined
                          ? recommendResults.parameters.taper_angle
                          : finalDesignParams.taper_angle !== undefined
                            ? ((finalDesignParams.taper_angle ?? 0) as number)
                            : ((finalDesignParams.angle_deg ?? 0) as number);
                      const numberOfFins =
                        recommendResults?.number_of_fins !== undefined
                          ? recommendResults.number_of_fins
                          : recommendResults?.parameters?.N !== undefined
                            ? recommendResults.parameters.N
                            : recommendResults?.parameters?.n !== undefined
                              ? recommendResults.parameters.n
                              : finalDesignParams.n_fins !== undefined
                                ? (finalDesignParams.n_fins as number)
                                : null;
                      const alloy =
                        recommendResults?.alloy ||
                        finalDesignParams.alloy ||
                        "6063-T5";

                      return (
                        <div className="rounded-lg border border-slate-700 bg-slate-900/30 p-4 space-y-4">
                          <div>
                            <p className="text-white text-2xl font-semibold leading-tight">
                              Analysis Results
                            </p>
                            <p className="text-slate-400 text-sm">
                              Recommended fin configurations based on your
                              parameters
                            </p>
                          </div>

                          <div className="bg-slate-700 p-4 rounded-lg">
                            <p className="text-white font-semibold">
                              Valid Design
                            </p>
                            <p className="text-slate-100 mt-1">
                              {validDesign ? "true" : "false"}
                            </p>
                          </div>

                          <div className="bg-slate-700 p-4 rounded-lg">
                            <p className="text-white font-semibold">Geometry</p>
                            <p className="text-slate-100 mt-1">
                              {geometryType}
                            </p>
                          </div>

                          <div className="bg-slate-700 p-4 rounded-lg">
                            <p className="text-white font-semibold mb-2">
                              Parameters
                            </p>
                            <div className="grid grid-cols-[1fr_auto] gap-x-4 gap-y-1 text-sm">
                              <p className="text-slate-300">Number of Fins:</p>
                              <p className="text-white font-semibold text-right">
                                {numberOfFins !== null
                                  ? numberOfFins.toFixed(3)
                                  : "N/A"}
                              </p>

                              <p className="text-slate-300">Fin Height:</p>
                              <p className="text-white font-semibold text-right">
                                {finHeightMm.toFixed(3)} mm
                              </p>

                              <p className="text-slate-300">Fin Spacing:</p>
                              <p className="text-white font-semibold text-right">
                                {finSpacingMm.toFixed(3)} mm
                              </p>

                              <p className="text-slate-300">Geometry Type:</p>
                              <p className="text-white font-semibold text-right">
                                {geometryType}
                              </p>

                              <p className="text-slate-300">Tip Thickness:</p>
                              <p className="text-white font-semibold text-right">
                                {tipThicknessMm.toFixed(3)} mm
                              </p>

                              <p className="text-slate-300">Taper Angle:</p>
                              <p className="text-white font-semibold text-right">
                                {taperAngle.toFixed(3)}
                              </p>
                            </div>
                          </div>

                          <div className="bg-slate-700 p-4 rounded-lg">
                            <p className="text-white font-semibold">
                              Material Alloy
                            </p>
                            <p className="text-slate-100 mt-1">{alloy}</p>
                          </div>
                        </div>
                      );
                    })()}

                    {results.final_metrics && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div className="bg-slate-700 p-3 rounded">
                          <p className="text-slate-400 text-xs">Drag</p>
                          <p className="text-white font-semibold">
                            {results.final_metrics.drag_coefficient.toFixed(3)}
                          </p>
                        </div>
                        <div className="bg-slate-700 p-3 rounded">
                          <p className="text-slate-400 text-xs">
                            Pressure Drop
                          </p>
                          <p className="text-white font-semibold">
                            {results.final_metrics.pressure_drop.toFixed(1)} Pa
                          </p>
                        </div>
                        <div className="bg-slate-700 p-3 rounded">
                          <p className="text-slate-400 text-xs">Uniformity</p>
                          <p className="text-white font-semibold">
                            {results.final_metrics.velocity_uniformity.toFixed(
                              3,
                            )}
                          </p>
                        </div>
                        <div className="bg-slate-700 p-3 rounded">
                          <p className="text-slate-400 text-xs">Separation</p>
                          <p className="text-white font-semibold">
                            {results.final_metrics.turbulence_separation
                              ? "Yes"
                              : "No"}
                          </p>
                        </div>
                      </div>
                    )}

                    {results.iterations && results.iterations.length > 0 && (
                      <div>
                        <Button
                          onClick={() => setShowIterations(!showIterations)}
                          variant="outline"
                          className="w-full"
                        >
                          {showIterations
                            ? "Hide Iterations"
                            : "Show All Iterations"}
                        </Button>

                        {showIterations && (
                          <div className="mt-3 max-h-64 overflow-y-auto overflow-x-hidden space-y-2">
                            {results.iterations
                              .slice(0, visibleIterationCount)
                              .map((iter) => (
                                <div
                                  key={iter.k}
                                  className="bg-slate-700 p-2 rounded text-sm"
                                >
                                  <div className="flex justify-between">
                                    <span className="text-white">
                                      Iteration {iter.k}
                                    </span>
                                    {iter.validation.pass ? (
                                      <CheckCircle2 className="w-4 h-4 text-green-500" />
                                    ) : (
                                      <AlertCircle className="w-4 h-4 text-red-500" />
                                    )}
                                  </div>
                                  <p className="text-slate-400 text-xs">
                                    Drag:{" "}
                                    {iter.cfd_results.drag_coefficient.toFixed(
                                      3,
                                    )}
                                  </p>
                                </div>
                              ))}

                            {results.iterations.length >
                              visibleIterationCount && (
                              <Button
                                variant="outline"
                                className="w-full"
                                onClick={() =>
                                  setVisibleIterationCount((prev) => prev + 20)
                                }
                              >
                                Load More Iterations
                              </Button>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  );
}
