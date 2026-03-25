import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./components/ui/select";
import { Slider } from "./components/ui/slider";
import { Separator } from "./components/ui/separator";
import {
  Target,
  ArrowRight,
  Sparkles,
  TrendingUp,
  BarChart3,
} from "lucide-react";
import { CFDOptimization } from "./components/CFDOptimization";
import { UnifiedOptimization } from "./components/UnifiedOptimization";

const normalizeBaseUrl = (url: string): string => url.replace(/\/+$/, "");

const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL as
  | string
  | undefined;
const API_BASE_URLS = configuredBaseUrl
  ? [normalizeBaseUrl(configuredBaseUrl)]
  : ["http://localhost:8001", "http://127.0.0.1:8001", "http://localhost:8000"];

// Fields to exclude from results display
const EXCLUDED_FIELDS = [
  "temperature",
  "thermal_resistance",
  "mass",
  "h_avg",
  "rad_pct",
  "sensitivity",
  "dominant_factor",
  "alloy_properties",
  "tb",
  "t_base",
];

// Length fields that should be converted from meters to mm
// NOTE: 'n' is NUMBER OF FINS (not a length), so it's excluded!
const LENGTH_FIELDS = ["h_max", "s", "l_fin", "t", "p", "h", "t_tip"];

// Mapping of field names to display names
const FIELD_DISPLAY_NAMES: { [key: string]: string } = {
  n: "Number of Fins",
  h: "Fin Height",
  h_max: "Max Height",
  t_base: "Base Thickness",
  t: "Thickness",
  s: "Fin Spacing",
  type: "Geometry Type",
  t_tip: "Tip Thickness",
  l_fin: "Fin Length",
  p: "Pitch",
  taper_angle: "Taper Angle",
  valid: "Valid Design",
  geometry: "Geometry",
  parameters: "Parameters",
  alloy: "Material Alloy",
};

// Helper function to format field name
const formatFieldName = (key: string): string => {
  const lowerKey = key.toLowerCase();
  return FIELD_DISPLAY_NAMES[lowerKey] || key.replace(/_/g, " ");
};

// Helper function to format display value
const formatValue = (key: string, value: any): string => {
  if (typeof value === "number") {
    // Convert meters to mm for length fields
    if (LENGTH_FIELDS.includes(key.toLowerCase())) {
      return (value * 1000).toFixed(3) + " mm";
    }
    return value.toFixed(3);
  }
  return String(value);
};

// Helper function to filter and process results
const filterResults = (results: any) => {
  const filtered: any = {};
  Object.entries(results).forEach(([key, value]: [string, any]) => {
    if (!EXCLUDED_FIELDS.includes(key.toLowerCase())) {
      if (typeof value === "object" && value !== null) {
        const filteredObj: any = {};
        Object.entries(value).forEach(([k, v]: [string, any]) => {
          // Also apply EXCLUDED_FIELDS filter to nested keys
          if (!EXCLUDED_FIELDS.includes(k.toLowerCase())) {
            filteredObj[k] = v;
          }
        });
        filtered[key] = filteredObj;
      } else {
        filtered[key] = value;
      }
    }
  });
  return filtered;
};

interface MotorParams {
  motor_type: string;
  rated_power: number;
  rated_voltage: number;
  rated_current: number;
  efficiency: number | null;
  max_temp: number;
  motor_diameter: number;
  motor_length: number;
}

interface EnvironmentParams {
  ambient_temp: number;
  airflow_type: string;
  air_velocity: number;
}

interface ConstraintParams {
  max_height: number;
  min_fin_thickness: number;
  max_weight: number | null;
}

function App() {
  const [activeTab, setActiveTab] = useState("unified");
  const [motorData, setMotorData] = useState<MotorParams>({
    motor_type: "Servo",
    rated_power: 1000,
    rated_voltage: 48,
    rated_current: 25,
    efficiency: null,
    max_temp: 100,
    motor_diameter: 0.05,
    motor_length: 0.1,
  });

  const [environmentData, setEnvironmentData] = useState<EnvironmentParams>({
    ambient_temp: 25,
    airflow_type: "Forced",
    air_velocity: 5.0,
  });

  const [constraintData, setConstraintData] = useState<ConstraintParams>({
    max_height: 50,
    min_fin_thickness: 2,
    max_weight: null,
  });

  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleMotorChange = (field: keyof MotorParams, value: any) => {
    setMotorData((prev) => ({ ...prev, [field]: value }));
  };

  const handleEnvironmentChange = (
    field: keyof EnvironmentParams,
    value: any,
  ) => {
    setEnvironmentData((prev) => ({ ...prev, [field]: value }));
  };

  const handleConstraintChange = (
    field: keyof ConstraintParams,
    value: any,
  ) => {
    setConstraintData((prev) => ({ ...prev, [field]: value }));
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const controller = new AbortController();
      const timeoutId = window.setTimeout(() => controller.abort(), 45000);

      // Use relaxed defaults for optional parameters to ensure feasible design
      const payload = {
        motor: motorData,
        environment: {
          ambient_temp: environmentData.ambient_temp,
          airflow_type: "Forced", // Use forced convection for better cooling
          air_velocity: 10.0, // Reasonable airflow velocity
        },
        constraints: {
          max_height: Math.max(constraintData.max_height / 1000, 0.1), // Min 100mm
          min_fin_thickness: Math.min(
            constraintData.min_fin_thickness / 1000,
            0.001,
          ), // Max 1mm
          max_weight: null,
        },
        preferred_alloy: null,
      };

      let response: Response | null = null;
      let lastFetchError: unknown = null;

      for (const baseUrl of API_BASE_URLS) {
        try {
          response = await fetch(`${baseUrl}/recommend/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
            signal: controller.signal,
          });
          break;
        } catch (fetchError) {
          lastFetchError = fetchError;
          if (fetchError instanceof Error && fetchError.name === "AbortError") {
            throw fetchError;
          }
        }
      }

      window.clearTimeout(timeoutId);

      if (!response) {
        throw new Error(
          `Could not reach backend API. Tried: ${API_BASE_URLS.join(", ")}. Error: ${String(lastFetchError)}`,
        );
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Analysis failed");
      }
      const data = await response.json();
      setResults(data);
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") {
        setError(
          "Analysis timed out. Please try again with different constraints.",
        );
      } else {
        setError(err instanceof Error ? err.message : "An error occurred");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4 sm:p-8 overflow-x-hidden">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-blue-500 p-2 rounded-lg">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-white">
              Fins Design Studio
            </h1>
          </div>
          <p className="text-slate-400">
            Optimize motor cooling fin configurations with AI-powered analysis
            and CFD feedback
          </p>
        </motion.div>

        {/* Tabs Navigation */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-8">
          <TabsList className="bg-slate-800 border border-slate-700">
            <TabsTrigger value="unified" className="gap-2">
              <Sparkles className="w-4 h-4" />
              Unified Optimizer
            </TabsTrigger>
            <TabsTrigger value="motor" className="gap-2">
              <Target className="w-4 h-4" />
              Heat Sink Optimizer
            </TabsTrigger>
            <TabsTrigger value="cfd" className="gap-2">
              <BarChart3 className="w-4 h-4" />
              CFD Optimization
            </TabsTrigger>
          </TabsList>

          {/* Unified Optimization Tab */}
          <TabsContent value="unified">
            <UnifiedOptimization apiBaseUrls={API_BASE_URLS} />
          </TabsContent>

          {/* Heat Sink Optimization Tab */}
          <TabsContent value="motor">
            {/* Main Content */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Input Panel */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
                className="lg:col-span-1"
              >
                <Card className="bg-slate-800 border-slate-700 shadow-2xl">
                  <CardHeader className="pb-4">
                    <CardTitle className="text-white flex items-center gap-2">
                      <TrendingUp className="w-5 h-5" />
                      Configuration
                    </CardTitle>
                    <CardDescription className="text-slate-400">
                      Set your motor and environment parameters
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="power" className="text-slate-300">
                          Power (W) *
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
                          className="bg-slate-700 border-slate-600 text-white"
                          placeholder="1000"
                        />
                      </div>
                      <div>
                        <Label htmlFor="voltage" className="text-slate-300">
                          Voltage (V) *
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
                          className="bg-slate-700 border-slate-600 text-white"
                          placeholder="48"
                        />
                      </div>
                      <div>
                        <Label htmlFor="current" className="text-slate-300">
                          Current (A) *
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
                          className="bg-slate-700 border-slate-600 text-white"
                          placeholder="25"
                        />
                      </div>
                      <div>
                        <Label htmlFor="max-temp" className="text-slate-300">
                          Max Temp (°C) *
                        </Label>
                        <Input
                          id="max-temp"
                          type="number"
                          value={motorData.max_temp}
                          onChange={(e) =>
                            handleMotorChange(
                              "max_temp",
                              parseFloat(e.target.value),
                            )
                          }
                          className="bg-slate-700 border-slate-600 text-white"
                          placeholder="100"
                        />
                      </div>
                      <div>
                        <Label
                          htmlFor="motor-diameter"
                          className="text-slate-300"
                        >
                          Motor Diameter (mm) *
                        </Label>
                        <Input
                          id="motor-diameter"
                          type="number"
                          value={motorData.motor_diameter * 1000}
                          onChange={(e) =>
                            handleMotorChange(
                              "motor_diameter",
                              parseFloat(e.target.value) / 1000,
                            )
                          }
                          className="bg-slate-700 border-slate-600 text-white"
                          placeholder="50"
                        />
                      </div>
                      <div>
                        <Label
                          htmlFor="motor-length"
                          className="text-slate-300"
                        >
                          Motor Length (mm) *
                        </Label>
                        <Input
                          id="motor-length"
                          type="number"
                          value={motorData.motor_length * 1000}
                          onChange={(e) =>
                            handleMotorChange(
                              "motor_length",
                              parseFloat(e.target.value) / 1000,
                            )
                          }
                          className="bg-slate-700 border-slate-600 text-white"
                          placeholder="100"
                        />
                      </div>
                    </div>

                    <Separator className="bg-slate-700" />

                    <Button
                      onClick={handleAnalyze}
                      disabled={loading}
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white gap-2"
                      size="lg"
                    >
                      {loading ? (
                        <>
                          <div className="animate-spin">⚙️</div>
                          Analyzing...
                        </>
                      ) : (
                        <>
                          Analyze Design
                          <ArrowRight className="w-4 h-4" />
                        </>
                      )}
                    </Button>

                    {error && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="p-3 bg-red-900/30 border border-red-700 rounded text-red-200 text-sm"
                      >
                        {error}
                      </motion.div>
                    )}
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
                <AnimatePresence>
                  {results ? (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      transition={{ duration: 0.3 }}
                      className="space-y-4"
                    >
                      <Card className="bg-slate-800 border-slate-700 shadow-2xl">
                        <CardHeader>
                          <CardTitle className="text-white flex items-center gap-2">
                            <Target className="w-5 h-5" />
                            Analysis Results
                          </CardTitle>
                          <CardDescription className="text-slate-400">
                            Recommended fin configurations based on your
                            parameters
                          </CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-4">
                            {Object.entries(filterResults(results)).map(
                              ([key, value]: [string, any], idx) => (
                                <motion.div
                                  key={key}
                                  initial={{ opacity: 0, y: 10 }}
                                  animate={{ opacity: 1, y: 0 }}
                                  transition={{ delay: idx * 0.1 }}
                                  className="p-4 bg-slate-700 rounded-lg border border-slate-600"
                                >
                                  <h3 className="font-semibold text-white mb-2 capitalize">
                                    {formatFieldName(key)}
                                  </h3>
                                  <div className="space-y-2">
                                    {typeof value === "object" ? (
                                      Object.entries(value).map(([k, v]) => (
                                        <div
                                          key={k}
                                          className="flex justify-between text-sm"
                                        >
                                          <span className="text-slate-400">
                                            {formatFieldName(k)}:
                                          </span>
                                          <span className="text-white font-medium">
                                            {formatValue(k, v)}
                                          </span>
                                        </div>
                                      ))
                                    ) : (
                                      <div className="text-slate-300">
                                        {formatValue(key, value)}
                                      </div>
                                    )}
                                  </div>
                                </motion.div>
                              ),
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ) : (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="h-full flex items-center justify-center"
                    >
                      <Card className="bg-slate-800 border-slate-700 shadow-2xl w-full">
                        <CardContent className="p-12 text-center">
                          <div className="text-slate-500 space-y-3">
                            <Sparkles className="w-16 h-16 mx-auto opacity-20" />
                            <p className="text-lg">
                              Configure your motor parameters and click "Analyze
                              Design"
                            </p>
                            <p className="text-sm">Results will appear here</p>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            </div>
          </TabsContent>

          {/* CFD Optimization Tab */}
          <TabsContent value="cfd">
            <CFDOptimization apiBaseUrls={API_BASE_URLS} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export default App;
