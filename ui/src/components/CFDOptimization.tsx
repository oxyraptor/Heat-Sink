import { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

interface CFDOptimizationProps {
  apiBaseUrls: string[];
}

export function CFDOptimization({ apiBaseUrls }: CFDOptimizationProps) {
  const [inletVelocity, setInletVelocity] = useState<number>(14.0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<any | null>(null);

  const postToFirstAvailableBaseUrl = async (
    path: string,
    payload: unknown,
  ): Promise<Response | null> => {
    for (const baseUrl of apiBaseUrls) {
      try {
        const response = await fetch(`${baseUrl}${path}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        return response;
      } catch {
        // try next
      }
    }
    return null;
  };

  const handleRun = async () => {
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const payload = { inlet_velocity: inletVelocity };
      const resp = await postToFirstAvailableBaseUrl("/cfd-optimize/", payload);
      if (!resp) throw new Error("Backend not reachable");
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.detail || `Request failed (${resp.status})`);
      }
      const data = await resp.json();
      setResponse(data);
    } catch (e: any) {
      setError(e?.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Card className="bg-slate-800 border-slate-700 shadow-2xl">
        <CardHeader>
          <CardTitle className="text-white">Inlet Velocity</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="inlet-velocity" className="text-slate-300 text-sm">
              Inlet Velocity (m/s)
            </Label>
            <Input
              id="inlet-velocity"
              type="number"
              step="0.1"
              value={inletVelocity}
              onChange={(e: any) =>
                setInletVelocity(parseFloat(e.target.value))
              }
              className="bg-slate-700 border-slate-600 text-white mt-1"
            />
          </div>

          <Button onClick={handleRun} disabled={loading} className="w-full">
            {loading ? "Sending..." : "Send Inlet Velocity"}
          </Button>

          {error && <div className="text-red-400">{error}</div>}

          {response && (
            <div className="text-slate-200">
              <pre className="text-xs">{JSON.stringify(response, null, 2)}</pre>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
