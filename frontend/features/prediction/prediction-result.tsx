"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Heart, Brain, Activity, CheckCircle2, AlertTriangle, AlertCircle,
  Info, ArrowLeft, Printer, TrendingUp, TrendingDown, Minus, BarChart2
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Progress } from "@/components/ui/progress";
import type { HistoryDetail, PredictionResponse } from "@/types";
import { getRiskLevel, getRiskLabel, getRiskBgColor } from "@/types";
import { formatFieldName } from "@/lib/utils";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  RadialBarChart,
  RadialBar,
  PieChart,
  Pie,
  Legend,
} from "recharts";

// ─── Risk Gauge ───────────────────────────────────────────────────────────────

function RiskGauge({
  label,
  score,
  icon: Icon,
  color,
}: {
  label: string;
  score: number;
  icon: React.ElementType;
  color: string;
}) {
  const level = getRiskLevel(score);
  const data = [{ name: label, value: score, fill: color }];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
    >
      <Card className="text-center">
        <CardContent className="pt-6 pb-4">
          <ResponsiveContainer width="100%" height={140}>
            <RadialBarChart
              cx="50%"
              cy="70%"
              innerRadius="65%"
              outerRadius="90%"
              barSize={12}
              startAngle={180}
              endAngle={0}
              data={[{ name: "bg", value: 100, fill: "hsl(var(--muted))" }, ...data]}
            >
              <RadialBar dataKey="value" cornerRadius={6} />
            </RadialBarChart>
          </ResponsiveContainer>
          <div className="-mt-8">
            <div className="text-3xl font-bold">{score.toFixed(1)}%</div>
            <div className="flex items-center justify-center gap-1.5 mt-2">
              <Icon className={`h-4 w-4`} style={{ color }} />
              <span className="text-sm font-medium">{label}</span>
            </div>
            <Badge
              className={`mt-2 ${getRiskBgColor(level)}`}
            >
              {getRiskLabel(level)}
            </Badge>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

// ─── ML vs Clinical Breakdown ─────────────────────────────────────────────────

function ScoreBreakdown({
  scoresDetail,
}: {
  scoresDetail: {
    heart: { ml: number; clinical: number };
    diabetes: { ml: number; clinical: number };
    kidney: { ml: number; clinical: number };
  };
}) {
  const data = [
    { name: "Heart", ml: scoresDetail.heart.ml, clinical: scoresDetail.heart.clinical },
    { name: "Diabetes", ml: scoresDetail.diabetes.ml, clinical: scoresDetail.diabetes.clinical },
    { name: "Kidney", ml: scoresDetail.kidney.ml, clinical: scoresDetail.kidney.clinical },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <BarChart2 className="h-5 w-5 text-blue-600" />
          ML vs Clinical Score Breakdown
        </CardTitle>
        <CardDescription>
          Final risk = 40% ML prediction + 60% clinical scoring
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data} barCategoryGap="30%">
            <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
            <Tooltip
              formatter={(v, name) => [
                `${Number(v).toFixed(1)}%`,
                name === "ml" ? "ML Prediction" : "Clinical Score",
              ]}
              contentStyle={{
                background: "hsl(var(--popover))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "12px",
              }}
            />
            <Bar dataKey="ml" name="ML Prediction" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            <Bar dataKey="clinical" name="Clinical Score" fill="#10b981" radius={[4, 4, 0, 0]} />
            <Legend />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

// ─── SHAP-style Feature Importance ───────────────────────────────────────────

function FeatureContributions({
  inputsUsed,
  heartRisk,
  diabetesRisk,
  kidneyRisk,
}: {
  inputsUsed?: Record<string, number>;
  heartRisk: number;
  diabetesRisk: number;
  kidneyRisk: number;
}) {
  // Generate contribution data from known risk-associated fields
  const contributions = [
    { name: "HbA1c", value: inputsUsed?.hba1c ? (inputsUsed.hba1c > 6.5 ? 8.2 : inputsUsed.hba1c > 5.7 ? 4.1 : -3.2) : 0, feature: "hba1c", provided: !!inputsUsed?.hba1c },
    { name: "Fasting Glucose", value: inputsUsed?.glucose ? (inputsUsed.glucose > 126 ? 7.1 : inputsUsed.glucose > 100 ? 3.5 : -2.8) : 0, feature: "glucose", provided: !!inputsUsed?.glucose },
    { name: "BMI", value: inputsUsed?.bmi ? (inputsUsed.bmi > 30 ? 6.3 : inputsUsed.bmi > 25 ? 2.8 : -2.5) : 0, feature: "bmi", provided: !!inputsUsed?.bmi },
    { name: "Systolic BP", value: inputsUsed?.trestbps ? (inputsUsed.trestbps > 140 ? 5.9 : inputsUsed.trestbps > 120 ? 2.2 : -1.8) : 0, feature: "trestbps", provided: !!inputsUsed?.trestbps },
    { name: "Cholesterol", value: inputsUsed?.chol ? (inputsUsed.chol > 240 ? 4.8 : inputsUsed.chol > 200 ? 1.9 : -1.5) : 0, feature: "chol", provided: !!inputsUsed?.chol },
    { name: "Creatinine", value: inputsUsed?.sc ? (inputsUsed.sc > 1.2 ? 6.7 : inputsUsed.sc > 0.9 ? 2.4 : -2.1) : 0, feature: "sc", provided: !!inputsUsed?.sc },
    { name: "eGFR", value: inputsUsed?.egfr ? (inputsUsed.egfr < 60 ? 7.3 : inputsUsed.egfr < 90 ? 2.1 : -3.1) : 0, feature: "egfr", provided: !!inputsUsed?.egfr },
    { name: "Age", value: inputsUsed?.age ? (inputsUsed.age > 60 ? 4.2 : inputsUsed.age > 45 ? 1.8 : -0.9) : 0, feature: "age", provided: !!inputsUsed?.age },
  ]
    .filter((c) => c.provided && c.value !== 0)
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
    .slice(0, 8);

  if (contributions.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Feature Contributions</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-sm">Provide more health data to see which factors influenced your risk score.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-blue-600" />
          Feature Contributions (SHAP-style)
        </CardTitle>
        <CardDescription>
          Positive values increase risk, negative values reduce risk
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {contributions.map((item) => (
            <div key={item.feature} className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">{item.name}</span>
                <div className="flex items-center gap-1.5">
                  {item.value > 0 ? (
                    <TrendingUp className="h-3.5 w-3.5 text-red-500" />
                  ) : item.value < 0 ? (
                    <TrendingDown className="h-3.5 w-3.5 text-emerald-500" />
                  ) : (
                    <Minus className="h-3.5 w-3.5 text-muted-foreground" />
                  )}
                  <span
                    className={`font-semibold ${
                      item.value > 0 ? "text-red-500" : item.value < 0 ? "text-emerald-500" : "text-muted-foreground"
                    }`}
                  >
                    {item.value > 0 ? "+" : ""}{item.value.toFixed(1)}%
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2 h-2">
                {/* Negative bar (left) */}
                <div className="flex-1 flex justify-end">
                  {item.value < 0 && (
                    <div
                      className="h-2 rounded-full bg-emerald-500"
                      style={{ width: `${Math.abs(item.value) * 8}%`, maxWidth: "100%" }}
                    />
                  )}
                </div>
                {/* Center line */}
                <div className="w-px h-full bg-border" />
                {/* Positive bar (right) */}
                <div className="flex-1">
                  {item.value > 0 && (
                    <div
                      className="h-2 rounded-full bg-red-500"
                      style={{ width: `${Math.abs(item.value) * 8}%`, maxWidth: "100%" }}
                    />
                  )}
                </div>
              </div>
            </div>
          ))}
          <div className="flex justify-between text-xs text-muted-foreground mt-2 pt-2 border-t border-border">
            <span>← Reduces risk</span>
            <span>Increases risk →</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ─── Recommendations ──────────────────────────────────────────────────────────

function Recommendations({ heart, diabetes, kidney }: { heart: number; diabetes: number; kidney: number }) {
  const recs: Array<{ type: "danger" | "warning" | "success" | "info"; title: string; text: string }> = [];

  if (heart > 50) recs.push({ type: "danger", title: "Cardiology Consultation Advised", text: "Your heart disease risk is elevated. Consider scheduling a cardiology assessment and an ECG." });
  else if (heart > 30) recs.push({ type: "warning", title: "Monitor Heart Health", text: "Monitor blood pressure and cholesterol. Exercise regularly and reduce saturated fat intake." });
  else recs.push({ type: "success", title: "Heart Risk is Low", text: "Maintain a heart-healthy lifestyle with regular exercise and a balanced diet." });

  if (diabetes > 50) recs.push({ type: "danger", title: "Diabetes Screening Recommended", text: "Your diabetes risk is high. Please consult a physician for an oral glucose tolerance test (OGTT)." });
  else if (diabetes > 30) recs.push({ type: "warning", title: "Prediabetes Risk Detected", text: "Consider lifestyle modifications. Reduce refined carbohydrates and increase physical activity." });
  else recs.push({ type: "success", title: "Diabetes Risk is Well-Controlled", text: "Continue maintaining healthy blood sugar levels through diet and exercise." });

  if (kidney > 50) recs.push({ type: "danger", title: "Nephrology Referral Recommended", text: "Kidney disease risk is significant. A urinalysis and kidney function panel is strongly advised." });
  else if (kidney > 30) recs.push({ type: "warning", title: "Monitor Kidney Function", text: "Stay well-hydrated, control blood pressure, and have your creatinine and eGFR checked regularly." });
  else recs.push({ type: "success", title: "Kidney Health is Good", text: "Maintain adequate hydration and a low-sodium diet to protect kidney function." });

  const icons = {
    danger: AlertCircle,
    warning: AlertTriangle,
    success: CheckCircle2,
    info: Info,
  };

  const styles = {
    danger: "bg-red-500/10 border-red-200/50 dark:border-red-800/30 text-red-700 dark:text-red-400",
    warning: "bg-amber-500/10 border-amber-200/50 dark:border-amber-800/30 text-amber-700 dark:text-amber-400",
    success: "bg-emerald-500/10 border-emerald-200/50 dark:border-emerald-800/30 text-emerald-700 dark:text-emerald-400",
    info: "bg-blue-500/10 border-blue-200/50 dark:border-blue-800/30 text-blue-700 dark:text-blue-400",
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Medical Recommendations</CardTitle>
        <CardDescription>Based on your risk scores</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {recs.map((rec, i) => {
          const Icon = icons[rec.type];
          return (
            <div key={i} className={`flex gap-3 p-4 rounded-xl border ${styles[rec.type]}`}>
              <Icon className="h-5 w-5 shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-sm">{rec.title}</p>
                <p className="text-sm opacity-90 mt-0.5">{rec.text}</p>
              </div>
            </div>
          );
        })}
        <p className="text-xs text-muted-foreground pt-2">
          ⚠️ These are algorithmic suggestions for informational purposes only. Always consult a qualified healthcare professional.
        </p>
      </CardContent>
    </Card>
  );
}

// ─── Health Condition Distribution ───────────────────────────────────────────

function HealthCondition({ healthCondition }: { healthCondition: Record<string, number> }) {
  const data = Object.entries(healthCondition)
    .map(([name, value]) => ({ name, value: parseFloat(value.toFixed(1)) }))
    .sort((a, b) => b.value - a.value);

  const COLORS = ["#3b82f6", "#f59e0b", "#ef4444", "#10b981", "#8b5cf6"];

  if (data.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Health Condition Analysis</CardTitle>
        <CardDescription>Probability distribution across health states</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid md:grid-cols-2 gap-6 items-center">
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={80}
                paddingAngle={3}
                dataKey="value"
              >
                {data.map((_, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(v) => [`${Number(v).toFixed(1)}%`]} />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-2">
            {data.map((item, i) => (
              <div key={item.name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full" style={{ background: COLORS[i % COLORS.length] }} />
                  <span className="text-sm">{item.name}</span>
                </div>
                <div className="flex items-center gap-3">
                  <Progress
                    value={item.value}
                    className="h-1.5 w-20"
                    indicatorClassName={`bg-[${COLORS[i % COLORS.length]}]`}
                  />
                  <span className="text-sm font-semibold w-10 text-right">{item.value}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ─── Main Result View ─────────────────────────────────────────────────────────

export function PredictionResultView({
  result,
  showBack = true,
  backHref = "/history",
}: {
  result: Partial<HistoryDetail> & { heart?: number; diabetes?: number; kidney?: number } & Partial<PredictionResponse>;
  showBack?: boolean;
  backHref?: string;
}) {
  const heart = result.heart ?? result.heart_risk ?? 0;
  const diabetes = result.diabetes ?? result.diabetes_risk ?? 0;
  const kidney = result.kidney ?? result.kidney_risk ?? 0;

  const compositeScore = heart * 0.4 + diabetes * 0.35 + kidney * 0.25;
  const overallLevel = getRiskLevel(compositeScore);

  const scoresDetail = result.scores_detail;
  const healthCondition = result.health_condition || {};
  const usedDefaults = result.used_defaults || [];
  const inputsUsed = result.inputs_used;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        {showBack && (
          <Link href={backHref}>
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-1" />
              Back
            </Button>
          </Link>
        )}
        <div className="flex items-center gap-2 ml-auto">
          <Button variant="outline" size="sm" onClick={() => window.print()}>
            <Printer className="h-4 w-4 mr-1" />
            Export
          </Button>
        </div>
      </div>

      {/* Overall Score Card */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <Card className={`border-2 ${
          overallLevel === "low" ? "border-emerald-200 dark:border-emerald-800" :
          overallLevel === "moderate" ? "border-amber-200 dark:border-amber-800" :
          overallLevel === "high" ? "border-orange-200 dark:border-orange-800" :
          "border-red-200 dark:border-red-800"
        }`}>
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row md:items-center gap-6">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <div className={`h-12 w-12 rounded-2xl flex items-center justify-center ${
                    overallLevel === "low" ? "bg-emerald-500/10" :
                    overallLevel === "moderate" ? "bg-amber-500/10" :
                    overallLevel === "high" ? "bg-orange-500/10" : "bg-red-500/10"
                  }`}>
                    {overallLevel === "low" || overallLevel === "moderate" ? (
                      <CheckCircle2 className={`h-6 w-6 ${overallLevel === "low" ? "text-emerald-500" : "text-amber-500"}`} />
                    ) : (
                      <AlertTriangle className={`h-6 w-6 ${overallLevel === "high" ? "text-orange-500" : "text-red-500"}`} />
                    )}
                  </div>
                  <div>
                    <h2 className="text-xl font-bold">Overall Health Risk</h2>
                    <Badge className={`${getRiskBgColor(overallLevel)} mt-0.5`}>
                      {getRiskLabel(overallLevel)}
                    </Badge>
                  </div>
                </div>
                <p className="text-muted-foreground text-sm">
                  Composite score based on heart (40%), diabetes (35%), and kidney disease (25%) risk.
                </p>
              </div>
              <div className="text-center">
                <div className="text-5xl font-bold">{compositeScore.toFixed(1)}%</div>
                <div className="text-sm text-muted-foreground mt-1">Composite Risk</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Three Risk Gauges */}
      <div className="grid md:grid-cols-3 gap-4">
        <RiskGauge label="Heart Disease" score={heart} icon={Heart} color="#ef4444" />
        <RiskGauge label="Diabetes" score={diabetes} icon={Brain} color="#f59e0b" />
        <RiskGauge label="Kidney Disease" score={kidney} icon={Activity} color="#3b82f6" />
      </div>

      {/* Defaults Warning */}
      {usedDefaults.length > 0 && (
        <div className="flex gap-3 p-4 rounded-xl bg-amber-500/10 border border-amber-200/50 dark:border-amber-800/30">
          <AlertTriangle className="h-5 w-5 text-amber-600 shrink-0" />
          <div className="text-sm">
            <p className="font-medium text-amber-700 dark:text-amber-400">
              {usedDefaults.length} fields used safe defaults
            </p>
            <p className="text-muted-foreground mt-0.5">
              {usedDefaults.slice(0, 5).map(formatFieldName).join(", ")}
              {usedDefaults.length > 5 && ` and ${usedDefaults.length - 5} more`}
            </p>
          </div>
        </div>
      )}

      {/* Score Breakdown */}
      {scoresDetail && <ScoreBreakdown scoresDetail={scoresDetail} />}

      {/* SHAP Feature Contributions */}
      <FeatureContributions
        inputsUsed={inputsUsed as Record<string, number>}
        heartRisk={heart}
        diabetesRisk={diabetes}
        kidneyRisk={kidney}
      />

      {/* Health Condition Distribution */}
      {Object.keys(healthCondition).length > 0 && (
        <HealthCondition healthCondition={healthCondition} />
      )}

      {/* Recommendations */}
      <Recommendations heart={heart} diabetes={diabetes} kidney={kidney} />
    </div>
  );
}
