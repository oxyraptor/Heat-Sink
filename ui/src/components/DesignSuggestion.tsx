import { useState } from "react";
import type { ReactNode } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowRight,
  CheckCircle2,
  Factory,
  GitCompare,
  Loader2,
  Ruler,
  Shapes,
  Thermometer,
} from "lucide-react";
import { Button } from "./ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { Separator } from "./ui/separator";

interface DesignSuggestionProps {
  apiBaseUrls: string[];
}

interface DesignCandidate {
  shape: string;
  geometry_family: string;
  score: number;
  thermal_score: number;
  predicted_temp: number;
  constraint_passed: boolean;
  arrangement: string;
  explanation: string;
  geometry: {
    base_length: number;
    base_width: number;
    base_thickness: number;
    fin_height: number;
    fin_width: number;
    fin_thickness: number;
    fin_spacing: number;
    fin_pitch: number;
    fin_count: number;
    arrangement: string;
  };
}

interface DesignSuggestionResult {
  recommended_shape: string;
  alternative_shapes: string[];
  geometry_family: string;
  geometry: DesignCandidate["geometry"];
  thermal_score: number;
  predicted_temp: number;
  constraint_passed: boolean;
  arrangement: string;
  explanation: string;
  ranked_candidates: DesignCandidate[];
  units: string;
  alloy: string;
}

const mm = (value: number) => `${(value * 1000).toFixed(1)} mm`;
const pct = (value: number) => `${Math.round(value * 100)}%`;
const titleCase = (value: string) =>
  value.replace(/-/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());

export function DesignSuggestion({ apiBaseUrls }: DesignSuggestionProps) {
  const [form, setForm] = useState({
    ratedPower: 1200,
    ratedVoltage: 72,
    ratedCurrent: 16.7,
    maxTemp: 95,
    baseLength: 120,
    baseWidth: 80,
    maxHeight: 55,
    minFinThickness: 1.2,
    shape: "Rectangular",
    ambientTemp: 25,
    airflowType: "Forced",
    airVelocity: 7,
    preferredAlloy: "6063-T5",
  });
  const [result, setResult] = useState<DesignSuggestionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateNumber = (field: keyof typeof form, value: string) => {
    setForm((current) => ({ ...current, [field]: Number(value) }));
  };

  const postToFirstAvailableBaseUrl = async (
    payload: unknown,
    signal: AbortSignal,
  ) => {
    let lastError: unknown = null;
    let lastResponse: Response | null = null;
    for (const baseUrl of apiBaseUrls) {
      try {
        const response = await fetch(`${baseUrl}/suggest-design/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
          signal,
        });
        if (response.ok || ![404, 405].includes(response.status)) {
          return response;
        }
        lastResponse = response;
      } catch (fetchError) {
        lastError = fetchError;
        if (fetchError instanceof Error && fetchError.name === "AbortError") {
          throw fetchError;
        }
      }
    }
    if (lastResponse) {
      return lastResponse;
    }
    throw new Error(`Could not reach backend API. Error: ${String(lastError)}`);
  };

  const handleSuggest = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const controller = new AbortController();
      const timeoutId = window.setTimeout(() => controller.abort(), 60000);
      const payload = {
        motor: {
          motor_type: "Servo",
          rated_power: form.ratedPower,
          rated_voltage: form.ratedVoltage,
          rated_current: form.ratedCurrent,
          max_temp: form.maxTemp,
          motor_diameter: Math.min(form.baseWidth, form.baseLength) / 1000,
          motor_length: form.baseLength / 1000,
          casing_width: form.baseWidth / 1000,
          casing_length: form.baseLength / 1000,
          casing_height: Math.max(form.maxHeight / 1000, 0.02),
        },
        environment: {
          ambient_temp: form.ambientTemp,
          airflow_type: form.airflowType,
          air_velocity: form.airVelocity,
        },
        constraints: {
          max_height: form.maxHeight / 1000,
          min_fin_thickness: form.minFinThickness / 1000,
          max_weight: null,
        },
        preferred_alloy: form.preferredAlloy,
        preferred_shape: form.shape,
        geometry_type: form.shape,
        candidate_limit: 3,
      };

      const response = await postToFirstAvailableBaseUrl(
        payload,
        controller.signal,
      );
      window.clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Design suggestion failed");
      }

      setResult(await response.json());
    } catch (requestError) {
      if (requestError instanceof Error && requestError.name === "AbortError") {
        setError(
          "Design suggestion timed out. Try a smaller envelope or stronger airflow.",
        );
      } else {
        setError(
          requestError instanceof Error
            ? requestError.message
            : "An error occurred",
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const primaryCandidate = result?.ranked_candidates?.[0] ?? null;

  return (
    <div className="grid grid-cols-1 xl:grid-cols-[420px_1fr] gap-8">
      <Card className="bg-slate-800 border-slate-700 shadow-2xl">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Shapes className="w-5 h-5" />
            Design Synthesizer
          </CardTitle>
          <CardDescription className="text-slate-400">
            Selects a base shape, fin family, and manufacturable dimensions.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label className="text-slate-300" htmlFor="suggest-power">
                Power (W)
              </Label>
              <Input
                id="suggest-power"
                type="number"
                value={form.ratedPower}
                onChange={(event) =>
                  updateNumber("ratedPower", event.target.value)
                }
                className="bg-slate-700 border-slate-600 text-white"
              />
            </div>
            <div>
              <Label className="text-slate-300" htmlFor="suggest-temp">
                Max Temp (deg C)
              </Label>
              <Input
                id="suggest-temp"
                type="number"
                value={form.maxTemp}
                onChange={(event) =>
                  updateNumber("maxTemp", event.target.value)
                }
                className="bg-slate-700 border-slate-600 text-white"
              />
            </div>
            <div>
              <Label className="text-slate-300" htmlFor="suggest-voltage">
                Voltage (V)
              </Label>
              <Input
                id="suggest-voltage"
                type="number"
                value={form.ratedVoltage}
                onChange={(event) =>
                  updateNumber("ratedVoltage", event.target.value)
                }
                className="bg-slate-700 border-slate-600 text-white"
              />
            </div>
            <div>
              <Label className="text-slate-300" htmlFor="suggest-current">
                Current (A)
              </Label>
              <Input
                id="suggest-current"
                type="number"
                value={form.ratedCurrent}
                onChange={(event) =>
                  updateNumber("ratedCurrent", event.target.value)
                }
                className="bg-slate-700 border-slate-600 text-white"
              />
            </div>
          </div>

          <Separator className="bg-slate-700" />

          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label className="text-slate-300" htmlFor="suggest-length">
                Base Length (mm)
              </Label>
              <Input
                id="suggest-length"
                type="number"
                value={form.baseLength}
                onChange={(event) =>
                  updateNumber("baseLength", event.target.value)
                }
                className="bg-slate-700 border-slate-600 text-white"
              />
            </div>
            <div>
              <Label className="text-slate-300" htmlFor="suggest-width">
                Base Width (mm)
              </Label>
              <Input
                id="suggest-width"
                type="number"
                value={form.baseWidth}
                onChange={(event) =>
                  updateNumber("baseWidth", event.target.value)
                }
                className="bg-slate-700 border-slate-600 text-white"
              />
            </div>
            <div>
              <Label className="text-slate-300" htmlFor="suggest-height">
                Max Height (mm)
              </Label>
              <Input
                id="suggest-height"
                type="number"
                value={form.maxHeight}
                onChange={(event) =>
                  updateNumber("maxHeight", event.target.value)
                }
                className="bg-slate-700 border-slate-600 text-white"
              />
            </div>
            <div>
              <Label className="text-slate-300" htmlFor="suggest-thickness">
                Min Fin (mm)
              </Label>
              <Input
                id="suggest-thickness"
                type="number"
                step="0.1"
                value={form.minFinThickness}
                onChange={(event) =>
                  updateNumber("minFinThickness", event.target.value)
                }
                className="bg-slate-700 border-slate-600 text-white"
              />
            </div>
            <div>
              <Label className="text-slate-300" htmlFor="suggest-shape">
                Fin Shape
              </Label>
              <Select
                value={form.shape}
                onValueChange={(value) =>
                  setForm((current) => ({ ...current, shape: value }))
                }
              >
                <SelectTrigger
                  id="suggest-shape"
                  className="bg-slate-700 border-slate-600 text-white"
                >
                  <SelectValue placeholder="Choose a fin shape" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Rectangular">Rectangular</SelectItem>
                  <SelectItem value="Triangular">Triangular</SelectItem>
                  <SelectItem value="Trapezoidal">Trapezoidal</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-[1fr_1.35fr] sm:items-stretch">
            <div className="space-y-2 rounded-lg border border-slate-700 bg-slate-900/30 p-3">
              <Label className="text-slate-300">CFD Inlet</Label>
              <Select
                value={form.airflowType}
                onValueChange={(value) =>
                  setForm((current) => ({ ...current, airflowType: value }))
                }
              >
                <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Forced">Forced</SelectItem>
                  <SelectItem value="Mixed">Mixed</SelectItem>
                  <SelectItem value="Natural">Natural</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-slate-400">
                Pick the inlet condition from CFD before setting the design
                velocity.
              </p>
            </div>
            <div className="space-y-2 rounded-lg border border-slate-700 bg-slate-900/30 p-3 h-full">
              <Label className="text-slate-300" htmlFor="suggest-velocity">
                Inlet Velocity from CFD (m/s)
              </Label>
              <Input
                id="suggest-velocity"
                type="number"
                step="0.5"
                value={form.airVelocity}
                onChange={(event) =>
                  updateNumber("airVelocity", event.target.value)
                }
                className="bg-slate-700 border-slate-600 text-white"
              />
              <p className="text-xs text-slate-400">
                Use the CFD inlet velocity here so the synthesizer matches the
                airflow condition you want to design for.
              </p>
            </div>
          </div>

          <Button
            onClick={handleSuggest}
            disabled={loading}
            className="w-full bg-cyan-600 hover:bg-cyan-700 text-white gap-2"
            size="lg"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <ArrowRight className="w-4 h-4" />
            )}
            Suggest Design
          </Button>

          {error && (
            <div className="p-3 bg-red-900/30 border border-red-700 rounded text-red-200 text-sm">
              {error}
            </div>
          )}
        </CardContent>
      </Card>

      <AnimatePresence mode="wait">
        {result && primaryCandidate ? (
          <motion.div
            key="results"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            className="space-y-5"
          >
            <Card className="bg-slate-800 border-slate-700 shadow-2xl">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  {titleCase(result.recommended_shape)} Proposal
                </CardTitle>
                <CardDescription className="text-slate-400">
                  {result.explanation}
                </CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-6">
                <div className="min-h-[220px] rounded-lg border border-slate-600 bg-slate-900 p-5 flex items-end justify-center">
                  <div
                    className="w-full max-w-[220px] border-b-8 border-cyan-500 flex items-end justify-around"
                    style={{ height: 170 }}
                  >
                    {Array.from({
                      length: Math.min(result.geometry.fin_count, 18),
                    }).map((_, index) => (
                      <div
                        key={index}
                        className={
                          result.geometry_family === "Triangular"
                            ? "bg-emerald-400"
                            : "bg-cyan-400"
                        }
                        style={{
                          width:
                            result.geometry_family === "Triangular" ? 9 : 6,
                          height: `${Math.max(36, Math.min(138, result.geometry.fin_height * 2200))}px`,
                          clipPath:
                            result.geometry_family === "Triangular"
                              ? "polygon(50% 0, 0 100%, 100% 100%)"
                              : undefined,
                        }}
                      />
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  <Metric
                    icon={<Thermometer className="w-4 h-4" />}
                    label="Predicted Temp"
                    value={`${result.predicted_temp.toFixed(1)} deg C`}
                  />
                  <Metric
                    icon={<Factory className="w-4 h-4" />}
                    label="Arrangement"
                    value={titleCase(result.arrangement)}
                  />
                  <Metric
                    icon={<GitCompare className="w-4 h-4" />}
                    label="Thermal Score"
                    value={pct(result.thermal_score)}
                  />
                  <Metric
                    icon={<Ruler className="w-4 h-4" />}
                    label="Base"
                    value={`${mm(result.geometry.base_length)} x ${mm(result.geometry.base_width)}`}
                  />
                  <Metric
                    icon={<Ruler className="w-4 h-4" />}
                    label="Fin Height"
                    value={mm(result.geometry.fin_height)}
                  />
                  <Metric
                    icon={<Ruler className="w-4 h-4" />}
                    label="Spacing / Pitch"
                    value={`${mm(result.geometry.fin_spacing)} / ${mm(result.geometry.fin_pitch)}`}
                  />
                  <Metric
                    icon={<Shapes className="w-4 h-4" />}
                    label="Fin Count"
                    value={String(result.geometry.fin_count)}
                  />
                  <Metric
                    icon={<Ruler className="w-4 h-4" />}
                    label="Thickness"
                    value={mm(result.geometry.fin_thickness)}
                  />
                  <Metric
                    icon={<CheckCircle2 className="w-4 h-4" />}
                    label="Constraint"
                    value={result.constraint_passed ? "Passed" : "Needs Review"}
                  />
                </div>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {result.ranked_candidates.slice(1).map((candidate) => (
                <Card
                  key={candidate.shape}
                  className="bg-slate-800 border-slate-700"
                >
                  <CardHeader className="pb-3">
                    <CardTitle className="text-white text-base">
                      {titleCase(candidate.shape)}
                    </CardTitle>
                    <CardDescription className="text-slate-400">
                      {candidate.explanation}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="grid grid-cols-3 gap-2 text-sm">
                    <Metric label="Score" value={pct(candidate.score)} />
                    <Metric
                      label="Temp"
                      value={`${candidate.predicted_temp.toFixed(1)} C`}
                    />
                    <Metric
                      label="Fins"
                      value={String(candidate.geometry.fin_count)}
                    />
                  </CardContent>
                </Card>
              ))}
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="empty"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="h-full min-h-[420px] flex items-center justify-center"
          >
            <Card className="bg-slate-800 border-slate-700 shadow-2xl w-full">
              <CardContent className="p-12 text-center text-slate-500 space-y-3">
                <Shapes className="w-16 h-16 mx-auto opacity-20" />
                <p className="text-lg">
                  Run the synthesizer to rank base shapes and fin geometry.
                </p>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function Metric({
  icon,
  label,
  value,
}: {
  icon?: ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg border border-slate-600 bg-slate-700/80 p-3 min-w-0">
      <div className="text-slate-400 text-xs flex items-center gap-1.5 mb-1">
        {icon}
        <span className="truncate">{label}</span>
      </div>
      <div className="text-white font-semibold text-sm break-words">
        {value}
      </div>
    </div>
  );
}
