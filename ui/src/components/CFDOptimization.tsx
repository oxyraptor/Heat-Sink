import { useState } from "react";
import { motion } from "framer-motion";
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Separator } from "./ui/separator";
import {
  BarChart3,
  Play,
  AlertCircle,
  CheckCircle2,
  Clock,
} from "lucide-react";

interface CFDParams {
  dragMax: number;
  pressureDropMax: number;
  velocityUniformityMin: number;
  inletVelocity: number;
  maxIterations: number;
  allowSeparation: boolean;
}

interface CFDResult {
  status: "PASS" | "MAX_ITERATIONS_REACHED" | "FAILED";
  iteration_count: number;
  final_design_file?: string;
  final_metrics?: {
    drag_coefficient: number;
    pressure_drop: number;
    velocity_uniformity: number;
    turbulence_separation: boolean;
    weak_regions: string[];
  };
  constraints?: {
    drag_coefficient_max: number;
    pressure_drop_max: number;
    velocity_uniformity_min: number;
    no_turbulence_separation: boolean;
  };
  iterations?: Array<{
    k: number;
    design_file: string;
    design_parameters?: {
      length: number;
      width: number;
      height: number;
      curvature: number;
      inlet_size: number;
      outlet_size: number;
      angle_deg: number;
      edge_radius: number;
    };
    changes: string[];
    cfd_results: {
      drag_coefficient: number;
      pressure_drop: number;
      velocity_uniformity: number;
      turbulence_separation: boolean;
      weak_regions: string[];
    };
    validation: {
      pass: boolean;
      failed_checks: string[];
    };
  }>;
}

interface CFDOptimizationProps {
  apiBaseUrls: string[];
}

export function CFDOptimization({ apiBaseUrls }: CFDOptimizationProps) {
  const [params, setParams] = useState<CFDParams>({
    dragMax: 0.17,
    pressureDropMax: 130,
    velocityUniformityMin: 0.84,
    inletVelocity: 14.0,
    maxIterations: 20,
    allowSeparation: false,
  });

  const [results, setResults] = useState<CFDResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [iterations, setIterations] = useState<CFDResult["iterations"]>([]);
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

  const handleParamChange = (field: keyof CFDParams, value: any) => {
    if (typeof params[field] === "boolean") {
      setParams((prev) => ({ ...prev, [field]: !prev[field] }));
    } else {
      setParams((prev) => ({ ...prev, [field]: value }));
    }
  };

  const handleRunOptimization = async () => {
    setLoading(true);
    setError(null);
    setResults(null);
    setIterations([]);
    setVisibleIterationCount(20);

    try {
      const controller = new AbortController();
      const timeoutId = window.setTimeout(() => controller.abort(), 300000); // 5 min timeout

      const payload = {
        drag_max: params.dragMax,
        pressure_drop_max: params.pressureDropMax,
        velocity_uniformity_min: params.velocityUniformityMin,
        inlet_velocity: params.inletVelocity,
        max_iterations: params.maxIterations,
        allow_separation: params.allowSeparation,
        history_limit: 50,
      };

      const response = await postToFirstAvailableBaseUrl(
        "/cfd-optimize/",
        payload,
        controller.signal,
      );

      window.clearTimeout(timeoutId);

      if (!response?.ok) {
        if (response?.status === 404) {
          throw new Error(
            "CFD optimization endpoint not available. Please ensure backend is running with CFD support.",
          );
        }
        const errorData = await response?.json().catch(() => ({}));
        throw new Error(
          errorData.detail ||
            "CFD optimization failed. Please check parameters.",
        );
      }

      const data = (await response.json()) as CFDResult;
      setResults(data);
      if (data.iterations) {
        setIterations(data.iterations);
      }
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") {
        setError(
          "Optimization timed out (5 min limit). Try reducing max iterations.",
        );
      } else {
        setError(err instanceof Error ? err.message : "An error occurred");
      }
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "PASS":
        return "text-green-400";
      case "MAX_ITERATIONS_REACHED":
        return "text-yellow-400";
      default:
        return "text-red-400";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "PASS":
        return <CheckCircle2 className="w-5 h-5 text-green-400" />;
      case "MAX_ITERATIONS_REACHED":
        return <Clock className="w-5 h-5 text-yellow-400" />;
      default:
        return <AlertCircle className="w-5 h-5 text-red-400" />;
    }
  };

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="bg-purple-600 p-2 rounded-lg">
            <BarChart3 className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-3xl font-bold text-white">
            CFD Optimization Loop
          </h2>
        </div>
        <p className="text-slate-400">
          Iteratively optimize design using CFD feedback until constraints are
          met
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Parameters Panel */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="lg:col-span-1"
        >
          <Card className="bg-slate-800 border-slate-700 shadow-2xl">
            <CardHeader className="pb-4">
              <CardTitle className="text-white">CFD Parameters</CardTitle>
              <CardDescription className="text-slate-400">
                Set validation criteria and solver options
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="drag-max" className="text-slate-300 text-sm">
                  Max Drag Coefficient
                </Label>
                <Input
                  id="drag-max"
                  type="number"
                  step="0.01"
                  value={params.dragMax}
                  onChange={(e) =>
                    handleParamChange("dragMax", parseFloat(e.target.value))
                  }
                  className="bg-slate-700 border-slate-600 text-white mt-1"
                />
              </div>

              <div>
                <Label
                  htmlFor="pressure-drop-max"
                  className="text-slate-300 text-sm"
                >
                  Max Pressure Drop (Pa)
                </Label>
                <Input
                  id="pressure-drop-max"
                  type="number"
                  value={params.pressureDropMax}
                  onChange={(e) =>
                    handleParamChange(
                      "pressureDropMax",
                      parseFloat(e.target.value),
                    )
                  }
                  className="bg-slate-700 border-slate-600 text-white mt-1"
                />
              </div>

              <div>
                <Label
                  htmlFor="velocity-uniformity-min"
                  className="text-slate-300 text-sm"
                >
                  Min Velocity Uniformity
                </Label>
                <Input
                  id="velocity-uniformity-min"
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={params.velocityUniformityMin}
                  onChange={(e) =>
                    handleParamChange(
                      "velocityUniformityMin",
                      parseFloat(e.target.value),
                    )
                  }
                  className="bg-slate-700 border-slate-600 text-white mt-1"
                />
              </div>

              <Separator className="bg-slate-700" />

              <div>
                <Label
                  htmlFor="inlet-velocity"
                  className="text-slate-300 text-sm"
                >
                  Inlet Velocity (m/s)
                </Label>
                <Input
                  id="inlet-velocity"
                  type="number"
                  step="0.5"
                  value={params.inletVelocity}
                  onChange={(e) =>
                    handleParamChange(
                      "inletVelocity",
                      parseFloat(e.target.value),
                    )
                  }
                  className="bg-slate-700 border-slate-600 text-white mt-1"
                />
              </div>

              <div>
                <Label
                  htmlFor="max-iterations"
                  className="text-slate-300 text-sm"
                >
                  Max Iterations
                </Label>
                <Input
                  id="max-iterations"
                  type="number"
                  value={params.maxIterations}
                  onChange={(e) =>
                    handleParamChange("maxIterations", parseInt(e.target.value))
                  }
                  className="bg-slate-700 border-slate-600 text-white mt-1"
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  id="allow-separation"
                  type="checkbox"
                  checked={params.allowSeparation}
                  onChange={() =>
                    handleParamChange(
                      "allowSeparation",
                      !params.allowSeparation,
                    )
                  }
                  className="rounded border-slate-600 bg-slate-700"
                />
                <Label
                  htmlFor="allow-separation"
                  className="text-slate-300 text-sm cursor-pointer"
                >
                  Allow Turbulence Separation
                </Label>
              </div>

              <Separator className="bg-slate-700" />

              <Button
                onClick={handleRunOptimization}
                disabled={loading}
                className="w-full bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white"
              >
                <Play className="w-4 h-4 mr-2" />
                {loading ? "Running Optimization..." : "Run Optimization"}
              </Button>
            </CardContent>
          </Card>
        </motion.div>

        {/* Results Panel */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="lg:col-span-2"
        >
          <Card className="bg-slate-800 border-slate-700 shadow-2xl">
            <CardHeader>
              <CardTitle className="text-white">Optimization Results</CardTitle>
              <CardDescription className="text-slate-400">
                {loading
                  ? "Running iterative optimization..."
                  : results
                    ? `Completed in ${results.iteration_count} iterations`
                    : "Results will appear here"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {error && (
                <div className="mb-4 p-4 bg-red-900/20 border border-red-700 rounded-lg">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                    <p className="text-red-200">{error}</p>
                  </div>
                </div>
              )}

              {results && (
                <Tabs defaultValue="summary" className="space-y-4">
                  <TabsList className="bg-slate-700 border-slate-600">
                    <TabsTrigger value="summary">Summary</TabsTrigger>
                    <TabsTrigger value="metrics">Metrics</TabsTrigger>
                    <TabsTrigger value="iterations">Iterations</TabsTrigger>
                  </TabsList>

                  <TabsContent value="summary" className="space-y-4">
                    <div className="flex items-center gap-3 p-4 bg-slate-700/50 rounded-lg">
                      {getStatusIcon(results.status)}
                      <div>
                        <p className="text-slate-400 text-sm">Status</p>
                        <p
                          className={`font-semibold ${getStatusColor(results.status)}`}
                        >
                          {results.status}
                        </p>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 bg-slate-700/50 rounded-lg">
                        <p className="text-slate-400 text-sm">Iterations</p>
                        <p className="text-2xl font-bold text-white">
                          {results.iteration_count}
                        </p>
                      </div>
                      <div className="p-4 bg-slate-700/50 rounded-lg">
                        <p className="text-slate-400 text-sm">Design File</p>
                        <p className="text-sm text-blue-300 truncate">
                          {results.final_design_file?.split("/").pop()}
                        </p>
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="metrics" className="space-y-3">
                    {results.final_metrics && (
                      <div className="space-y-3">
                        <div className="p-3 bg-slate-700/50 rounded">
                          <p className="text-slate-400 text-sm">
                            Drag Coefficient
                          </p>
                          <div className="flex items-center justify-between">
                            <p className="text-xl font-semibold text-white">
                              {results.final_metrics.drag_coefficient.toFixed(
                                4,
                              )}
                            </p>
                            <p className="text-xs text-slate-400">
                              Limit: {results.constraints?.drag_coefficient_max}
                            </p>
                          </div>
                        </div>

                        <div className="p-3 bg-slate-700/50 rounded">
                          <p className="text-slate-400 text-sm">
                            Pressure Drop
                          </p>
                          <div className="flex items-center justify-between">
                            <p className="text-xl font-semibold text-white">
                              {results.final_metrics.pressure_drop.toFixed(2)}{" "}
                              Pa
                            </p>
                            <p className="text-xs text-slate-400">
                              Limit: {results.constraints?.pressure_drop_max}
                            </p>
                          </div>
                        </div>

                        <div className="p-3 bg-slate-700/50 rounded">
                          <p className="text-slate-400 text-sm">
                            Velocity Uniformity
                          </p>
                          <div className="flex items-center justify-between">
                            <p className="text-xl font-semibold text-white">
                              {results.final_metrics.velocity_uniformity.toFixed(
                                3,
                              )}
                            </p>
                            <p className="text-xs text-slate-400">
                              Min:{" "}
                              {results.constraints?.velocity_uniformity_min}
                            </p>
                          </div>
                        </div>

                        <div className="p-3 bg-slate-700/50 rounded">
                          <p className="text-slate-400 text-sm">
                            Turbulence Separation
                          </p>
                          <p
                            className={`font-semibold ${
                              results.final_metrics.turbulence_separation
                                ? "text-red-400"
                                : "text-green-400"
                            }`}
                          >
                            {results.final_metrics.turbulence_separation
                              ? "Present"
                              : "None"}
                          </p>
                        </div>

                        {results.final_metrics.weak_regions.length > 0 && (
                          <div className="p-3 bg-yellow-900/20 border border-yellow-700 rounded">
                            <p className="text-slate-400 text-sm mb-2">
                              Weak Regions
                            </p>
                            <div className="flex flex-wrap gap-2">
                              {results.final_metrics.weak_regions.map(
                                (region) => (
                                  <span
                                    key={region}
                                    className="px-2 py-1 bg-yellow-700/50 text-yellow-200 text-xs rounded"
                                  >
                                    {region}
                                  </span>
                                ),
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </TabsContent>

                  <TabsContent value="iterations" className="space-y-3">
                    {iterations && iterations.length > 0 ? (
                      <div className="space-y-2 max-h-96 overflow-y-auto">
                        {iterations
                          .slice(0, visibleIterationCount)
                          .map((iter) => (
                            <div
                              key={iter.k}
                              className="p-3 bg-slate-700/50 rounded border border-slate-600"
                            >
                              <div className="flex items-start justify-between mb-2">
                                <span className="font-semibold text-white">
                                  Iteration {iter.k}
                                </span>
                                {iter.validation.pass ? (
                                  <span className="px-2 py-1 bg-green-700/50 text-green-200 text-xs rounded">
                                    PASS
                                  </span>
                                ) : (
                                  <span className="px-2 py-1 bg-red-700/50 text-red-200 text-xs rounded">
                                    FAIL
                                  </span>
                                )}
                              </div>
                              <p className="text-xs text-slate-400 mb-2">
                                Drag:{" "}
                                {iter.cfd_results.drag_coefficient.toFixed(4)} |
                                Pressure:
                                {iter.cfd_results.pressure_drop.toFixed(1)} Pa |
                                Uniformity:
                                {iter.cfd_results.velocity_uniformity.toFixed(
                                  3,
                                )}
                              </p>
                              {iter.design_parameters && (
                                <p className="text-xs text-slate-400 mb-2">
                                  H: {iter.design_parameters.height.toFixed(3)}{" "}
                                  | Curv:{" "}
                                  {iter.design_parameters.curvature.toFixed(3)}{" "}
                                  | Inlet:{" "}
                                  {iter.design_parameters.inlet_size.toFixed(3)}{" "}
                                  | Outlet:{" "}
                                  {iter.design_parameters.outlet_size.toFixed(
                                    3,
                                  )}{" "}
                                  | Angle:{" "}
                                  {iter.design_parameters.angle_deg.toFixed(2)}
                                </p>
                              )}
                              {iter.changes.length > 0 && (
                                <ul className="text-xs text-slate-300 space-y-1">
                                  {iter.changes.map((change, idx) => (
                                    <li key={idx} className="ml-4">
                                      • {change}
                                    </li>
                                  ))}
                                </ul>
                              )}
                            </div>
                          ))}

                        {iterations.length > visibleIterationCount && (
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
                    ) : (
                      <p className="text-slate-400 text-center py-8">
                        No iterations available
                      </p>
                    )}
                  </TabsContent>
                </Tabs>
              )}

              {!results && !loading && !error && (
                <div className="text-center py-12">
                  <BarChart3 className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                  <p className="text-slate-400">
                    Click "Run Optimization" to start the CFD loop
                  </p>
                </div>
              )}

              {loading && (
                <div className="text-center py-12">
                  <div className="inline-block">
                    <div className="w-8 h-8 border-4 border-slate-600 border-t-purple-500 rounded-full animate-spin"></div>
                  </div>
                  <p className="text-slate-400 mt-4">
                    Optimizing design through CFD iterations...
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}
