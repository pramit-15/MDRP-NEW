"use client";

import React, { useState, useEffect, useTransition, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sliders,
  Sparkles,
  TrendingDown,
  Heart,
  Activity,
  Brain,
  Scale,
  RefreshCw,
  Zap,
  Award,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  ChevronRight,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import type { SimulationResponse, PredictionResponse, HistoryDetail } from "@/types";

interface WhatIfSimulatorProps {
  baselineInputs: Record<string, any>;
  baselineResults: any;
}

export function WhatIfSimulator({ baselineInputs, baselineResults }: WhatIfSimulatorProps) {
  // Extract initial baseline values or safe defaults
  const baseWeight = Number(baselineInputs?.weight_kg || baselineInputs?.weight || 75);
  const baseHeight = Number(baselineInputs?.height_cm || baselineInputs?.height || 170);
  const baseSystolic = Number(baselineInputs?.systolic_bp || 125);
  const baseDiastolic = Number(baselineInputs?.diastolic_bp || 80);
  const baseGlucose = Number(baselineInputs?.glucose || 100);
  const baseHba1c = Number(baselineInputs?.hba1c || 5.6);
  const baseChol = Number(baselineInputs?.chol || 190);
  const baseLdl = Number(baselineInputs?.ldl || 110);

  // Modifiable state
  const [weightKg, setWeightKg] = useState<number>(baseWeight);
  const [systolicBp, setSystolicBp] = useState<number>(baseSystolic);
  const [glucose, setGlucose] = useState<number>(baseGlucose);
  const [hba1c, setHba1c] = useState<number>(baseHba1c);
  const [chol, setChol] = useState<number>(baseChol);
  const [ldl, setLdl] = useState<number>(baseLdl);

  // Simulation response state
  const [simResult, setSimResult] = useState<SimulationResponse | null>(null);
  const [isPending, startTransition] = useTransition();
  const [activePreset, setActivePreset] = useState<string | null>(null);

  // Calculate live BMI
  const currentBmi =
    baseHeight > 0
      ? Number((weightKg / ((baseHeight / 100) * (baseHeight / 100))).toFixed(1))
      : 24.5;
  const initialBmi =
    baseHeight > 0
      ? Number((baseWeight / ((baseHeight / 100) * (baseHeight / 100))).toFixed(1))
      : 24.5;

  // Run simulation API
  const runSimulation = useCallback(async () => {
    try {
      const modifications: Record<string, any> = {
        weight_kg: weightKg,
        systolic_bp: systolicBp,
        glucose: glucose,
        hba1c: hba1c,
        chol: chol,
        ldl: ldl,
      };

      const res = await fetch("/api/v1/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          base_inputs: baselineInputs,
          modifications,
          base_results: baselineResults,
        }),
      });

      if (res.ok) {
        const data: SimulationResponse = await res.json();
        setSimResult(data);
      }
    } catch (err) {
      console.debug("Simulation call failed:", err);
    }
  }, [baselineInputs, baselineResults, weightKg, systolicBp, glucose, hba1c, chol, ldl]);

  // Debounced effect when slider values change
  useEffect(() => {
    const timer = setTimeout(() => {
      startTransition(() => {
        runSimulation();
      });
    }, 150);
    return () => clearTimeout(timer);
  }, [runSimulation]);

  // Preset Handlers
  const applyPreset = (presetKey: string) => {
    setActivePreset(presetKey);
    switch (presetKey) {
      case "weight_loss":
        setWeightKg(Math.max(45, baseWeight - 5));
        setSystolicBp(Math.max(105, baseSystolic - 6));
        break;
      case "dash_diet":
        setSystolicBp(Math.max(110, baseSystolic - 12));
        setChol(Math.max(140, baseChol - 25));
        setLdl(Math.max(70, baseLdl - 20));
        break;
      case "glycemic":
        setHba1c(Math.max(5.0, Number((baseHba1c - 0.8).toFixed(1))));
        setGlucose(Math.max(85, baseGlucose - 25));
        break;
      case "overhaul":
        setWeightKg(Math.max(45, baseWeight - 7));
        setSystolicBp(Math.max(115, baseSystolic - 12));
        setHba1c(Math.max(5.2, Number((baseHba1c - 0.6).toFixed(1))));
        setGlucose(Math.max(90, baseGlucose - 20));
        setChol(Math.max(160, baseChol - 30));
        setLdl(Math.max(85, baseLdl - 25));
        break;
    }
  };

  const handleReset = () => {
    setActivePreset(null);
    setWeightKg(baseWeight);
    setSystolicBp(baseSystolic);
    setGlucose(baseGlucose);
    setHba1c(baseHba1c);
    setChol(baseChol);
    setLdl(baseLdl);
  };

  const baselineComp = simResult?.baseline.composite ?? 0;
  const simComp = simResult?.simulated.composite ?? baselineComp;
  const compDelta = simResult?.deltas.composite ?? 0;
  const compReduction = simResult?.percentage_reductions.composite ?? 0;

  const weightDiff = Number((weightKg - baseWeight).toFixed(1));

  return (
    <Card className="border-2 border-emerald-500/20 bg-gradient-to-b from-emerald-500/5 via-card to-card shadow-sm overflow-hidden">
      <CardHeader className="pb-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-white shadow-sm shadow-emerald-500/20">
              <Sliders className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-lg flex items-center gap-2">
                Interactive &quot;What-If&quot; Risk Simulator
              </CardTitle>
              <CardDescription className="text-xs">
                Simulate future risk drops by tuning your lifestyle &amp; biomarker targets
              </CardDescription>
            </div>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={handleReset}
            className="gap-1.5 text-xs self-start sm:self-center cursor-pointer"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Reset Baseline
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Quick Intervention Presets */}
        <div className="space-y-2">
          <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
            Target Lifestyle Packages
          </span>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {[
              {
                id: "weight_loss",
                label: "5kg Weight Loss",
                desc: "-5kg weight, -6 mmHg BP",
                icon: Scale,
              },
              {
                id: "dash_diet",
                label: "DASH Diet & Sodium",
                desc: "-12 mmHg BP, -25 Chol",
                icon: Heart,
              },
              {
                id: "glycemic",
                label: "Glycemic Control",
                desc: "-0.8% HbA1c, -25 Glucose",
                icon: Activity,
              },
              {
                id: "overhaul",
                label: "Complete Overhaul",
                desc: "Combined optimal targets",
                icon: Zap,
              },
            ].map((p) => {
              const isSelected = activePreset === p.id;
              const Icon = p.icon;
              return (
                <button
                  key={p.id}
                  onClick={() => applyPreset(p.id)}
                  type="button"
                  className={`p-2.5 rounded-xl border text-left transition-all cursor-pointer ${
                    isSelected
                      ? "border-emerald-500 bg-emerald-500/10 text-foreground ring-1 ring-emerald-500/50"
                      : "border-border bg-card/60 hover:bg-muted/60 text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <div className="flex items-center gap-1.5 font-semibold text-xs text-foreground mb-0.5">
                    <Icon className="h-3.5 w-3.5 text-emerald-500 shrink-0" />
                    <span className="truncate">{p.label}</span>
                  </div>
                  <p className="text-[10px] text-muted-foreground truncate">{p.desc}</p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Live Simulation Projection Header */}
        <div className="p-4 sm:p-5 rounded-xl bg-card border border-emerald-500/30 shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block">
                Simulated Composite Health Risk
              </span>
              <div className="flex items-baseline gap-3 mt-1">
                <span className="text-3xl font-bold text-foreground">
                  {simComp.toFixed(1)}%
                </span>
                <span className="text-sm text-muted-foreground line-through">
                  {baselineComp.toFixed(1)}% baseline
                </span>
                {compDelta < 0 && (
                  <Badge className="bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-300 dark:border-emerald-700 text-xs font-semibold gap-1">
                    <TrendingDown className="h-3.5 w-3.5" />
                    {compDelta.toFixed(1)}% ({compReduction}% reduction)
                  </Badge>
                )}
              </div>
            </div>

            {/* Category badge */}
            <div className="text-left sm:text-right">
              <span className="text-[11px] text-muted-foreground block">Projected Status</span>
              <Badge variant="outline" className="mt-0.5 border-emerald-500/40 text-emerald-600 dark:text-emerald-400">
                {simResult?.simulated.level || "Healthy Trajectory"}
              </Badge>
            </div>
          </div>

          {/* Tri-Disease Comparison Gauges */}
          <div className="grid sm:grid-cols-3 gap-3 pt-2">
            {/* Heart */}
            <div className="p-3 rounded-lg bg-muted/40 border border-border/60 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-red-600 dark:text-red-400 flex items-center gap-1">
                  <Heart className="h-3.5 w-3.5" /> Cardiovascular
                </span>
                <span className="font-bold">
                  {simResult?.simulated.heart.toFixed(1) ?? "--"}%
                </span>
              </div>
              <Progress
                value={simResult?.simulated.heart ?? 0}
                className="h-1.5 [&>div]:bg-red-500"
              />
              <div className="flex items-center justify-between text-[11px] text-muted-foreground">
                <span>Base: {simResult?.baseline.heart.toFixed(1)}%</span>
                {(simResult?.deltas.heart ?? 0) < 0 && (
                  <span className="text-emerald-600 dark:text-emerald-400 font-semibold">
                    {simResult?.deltas.heart.toFixed(1)}%
                  </span>
                )}
              </div>
            </div>

            {/* Diabetes */}
            <div className="p-3 rounded-lg bg-muted/40 border border-border/60 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-amber-600 dark:text-amber-400 flex items-center gap-1">
                  <Activity className="h-3.5 w-3.5" /> Diabetes
                </span>
                <span className="font-bold">
                  {simResult?.simulated.diabetes.toFixed(1) ?? "--"}%
                </span>
              </div>
              <Progress
                value={simResult?.simulated.diabetes ?? 0}
                className="h-1.5 [&>div]:bg-amber-500"
              />
              <div className="flex items-center justify-between text-[11px] text-muted-foreground">
                <span>Base: {simResult?.baseline.diabetes.toFixed(1)}%</span>
                {(simResult?.deltas.diabetes ?? 0) < 0 && (
                  <span className="text-emerald-600 dark:text-emerald-400 font-semibold">
                    {simResult?.deltas.diabetes.toFixed(1)}%
                  </span>
                )}
              </div>
            </div>

            {/* Kidney */}
            <div className="p-3 rounded-lg bg-muted/40 border border-border/60 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-blue-600 dark:text-blue-400 flex items-center gap-1">
                  <Brain className="h-3.5 w-3.5" /> Kidney Disease
                </span>
                <span className="font-bold">
                  {simResult?.simulated.kidney.toFixed(1) ?? "--"}%
                </span>
              </div>
              <Progress
                value={simResult?.simulated.kidney ?? 0}
                className="h-1.5 [&>div]:bg-blue-500"
              />
              <div className="flex items-center justify-between text-[11px] text-muted-foreground">
                <span>Base: {simResult?.baseline.kidney.toFixed(1)}%</span>
                {(simResult?.deltas.kidney ?? 0) < 0 && (
                  <span className="text-emerald-600 dark:text-emerald-400 font-semibold">
                    {simResult?.deltas.kidney.toFixed(1)}%
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Milestones Achieved */}
          {simResult?.milestones && simResult.milestones.length > 0 && (
            <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-300 dark:border-emerald-800/40 text-xs space-y-1">
              <div className="font-semibold text-emerald-700 dark:text-emerald-400 flex items-center gap-1.5">
                <Award className="h-4 w-4" /> Projected Health Milestones:
              </div>
              <ul className="text-muted-foreground space-y-0.5 pl-5 list-disc">
                {simResult.milestones.map((m, idx) => (
                  <li key={idx} className="leading-tight">
                    {m}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Interactive Sliders Grid */}
        <div className="space-y-4">
          <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
            Tune Modifiable Biomarkers &amp; Lifestyle Factors
          </span>

          <div className="grid md:grid-cols-2 gap-4">
            {/* Weight & BMI Slider */}
            <div className="p-4 rounded-xl border border-border/80 bg-card space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <Scale className="h-4 w-4 text-emerald-500" />
                  <span className="text-sm font-semibold">Body Weight</span>
                </div>
                <div className="text-right">
                  <span className="text-sm font-bold">{weightKg} kg</span>
                  <span className="text-xs text-muted-foreground ml-1.5">
                    (BMI: {currentBmi})
                  </span>
                </div>
              </div>
              <input
                type="range"
                min={Math.max(40, baseWeight - 25)}
                max={Math.min(180, baseWeight + 15)}
                step="0.5"
                value={weightKg}
                onChange={(e) => {
                  setActivePreset(null);
                  setWeightKg(parseFloat(e.target.value));
                }}
                className="w-full accent-emerald-600 h-2 bg-muted rounded-lg cursor-pointer"
              />
              <div className="flex items-center justify-between text-[11px] text-muted-foreground">
                <span>Baseline: {baseWeight} kg (BMI {initialBmi})</span>
                <span className={weightDiff < 0 ? "text-emerald-500 font-semibold" : ""}>
                  {weightDiff > 0 ? `+${weightDiff}` : weightDiff} kg
                </span>
              </div>
            </div>

            {/* Systolic BP Slider */}
            <div className="p-4 rounded-xl border border-border/80 bg-card space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <Heart className="h-4 w-4 text-red-500" />
                  <span className="text-sm font-semibold">Systolic Blood Pressure</span>
                </div>
                <span className="text-sm font-bold">{systolicBp} mmHg</span>
              </div>
              <input
                type="range"
                min={95}
                max={Math.max(160, baseSystolic + 15)}
                step="1"
                value={systolicBp}
                onChange={(e) => {
                  setActivePreset(null);
                  setSystolicBp(parseInt(e.target.value));
                }}
                className="w-full accent-red-500 h-2 bg-muted rounded-lg cursor-pointer"
              />
              <div className="flex items-center justify-between text-[11px] text-muted-foreground">
                <span>Optimal: 115-120 mmHg</span>
                <span>Baseline: {baseSystolic} mmHg</span>
              </div>
            </div>

            {/* HbA1c Slider */}
            <div className="p-4 rounded-xl border border-border/80 bg-card space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <Activity className="h-4 w-4 text-amber-500" />
                  <span className="text-sm font-semibold">Glycated Hemoglobin (HbA1c)</span>
                </div>
                <span className="text-sm font-bold">{hba1c.toFixed(1)}%</span>
              </div>
              <input
                type="range"
                min={4.8}
                max={Math.max(9.0, baseHba1c + 1.5)}
                step="0.1"
                value={hba1c}
                onChange={(e) => {
                  setActivePreset(null);
                  setHba1c(parseFloat(e.target.value));
                }}
                className="w-full accent-amber-500 h-2 bg-muted rounded-lg cursor-pointer"
              />
              <div className="flex items-center justify-between text-[11px] text-muted-foreground">
                <span>Normal: &lt;5.7%</span>
                <span>Baseline: {baseHba1c}%</span>
              </div>
            </div>

            {/* Fasting Glucose Slider */}
            <div className="p-4 rounded-xl border border-border/80 bg-card space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <Activity className="h-4 w-4 text-amber-500" />
                  <span className="text-sm font-semibold">Fasting Blood Glucose</span>
                </div>
                <span className="text-sm font-bold">{glucose} mg/dL</span>
              </div>
              <input
                type="range"
                min={75}
                max={Math.max(200, baseGlucose + 30)}
                step="1"
                value={glucose}
                onChange={(e) => {
                  setActivePreset(null);
                  setGlucose(parseInt(e.target.value));
                }}
                className="w-full accent-amber-500 h-2 bg-muted rounded-lg cursor-pointer"
              />
              <div className="flex items-center justify-between text-[11px] text-muted-foreground">
                <span>Normal: 70-99 mg/dL</span>
                <span>Baseline: {baseGlucose} mg/dL</span>
              </div>
            </div>

            {/* Total Cholesterol Slider */}
            <div className="p-4 rounded-xl border border-border/80 bg-card space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <ShieldCheck className="h-4 w-4 text-blue-500" />
                  <span className="text-sm font-semibold">Total Cholesterol</span>
                </div>
                <span className="text-sm font-bold">{chol} mg/dL</span>
              </div>
              <input
                type="range"
                min={120}
                max={Math.max(280, baseChol + 30)}
                step="2"
                value={chol}
                onChange={(e) => {
                  setActivePreset(null);
                  setChol(parseInt(e.target.value));
                }}
                className="w-full accent-blue-500 h-2 bg-muted rounded-lg cursor-pointer"
              />
              <div className="flex items-center justify-between text-[11px] text-muted-foreground">
                <span>Desirable: &lt;200 mg/dL</span>
                <span>Baseline: {baseChol} mg/dL</span>
              </div>
            </div>

            {/* LDL Cholesterol Slider */}
            <div className="p-4 rounded-xl border border-border/80 bg-card space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <ShieldCheck className="h-4 w-4 text-blue-500" />
                  <span className="text-sm font-semibold">LDL (Bad Cholesterol)</span>
                </div>
                <span className="text-sm font-bold">{ldl} mg/dL</span>
              </div>
              <input
                type="range"
                min={50}
                max={Math.max(200, baseLdl + 30)}
                step="2"
                value={ldl}
                onChange={(e) => {
                  setActivePreset(null);
                  setLdl(parseInt(e.target.value));
                }}
                className="w-full accent-blue-500 h-2 bg-muted rounded-lg cursor-pointer"
              />
              <div className="flex items-center justify-between text-[11px] text-muted-foreground">
                <span>Optimal: &lt;100 mg/dL</span>
                <span>Baseline: {baseLdl} mg/dL</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
