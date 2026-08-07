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
import type { HistoryDetail, PredictionResponse, ShapContribution, ExplainabilityResult } from "@/types";
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

// ─── Real SHAP Feature Importance ─────────────────────────────────────────────

const FEATURE_LABELS: Record<string, string> = {
  age: "Age", glucose: "Fasting Glucose", hba1c: "HbA1c", bmi: "BMI",
  trestbps: "Systolic BP", bloodpressure: "Diastolic BP", chol: "Cholesterol",
  ldl: "LDL", hdl: "HDL", triglycerides: "Triglycerides", sc: "Creatinine",
  bu: "Blood Urea", egfr: "eGFR", sod: "Sodium", pot: "Potassium",
  htn: "Hypertension", dm: "Diabetes", cad: "CAD", pe: "Pedal Edema",
  ane: "Anemia", appet: "Appetite", cp: "Chest Pain", thalach: "Max Heart Rate",
  exang: "Exercise Angina", oldpeak: "ST Depression", fbs: "Fasting BS",
  ca: "Major Vessels", thal: "Thalassemia", skin: "Skin Thickness",
  insulin: "Insulin", preg: "Pregnancies", dpf: "DPF", sex: "Sex",
};

function SHAPContributionBar({ item }: { item: { name: string; value: number; contribution: number } }) {
  const maxBar = 100;
  const width = Math.min(Math.abs(item.contribution) * 400, maxBar);
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-1.5">
          <span className="font-medium">{item.name}</span>
          <span className="text-xs text-muted-foreground">{item.value.toFixed(2)}</span>
        </div>
        <div className="flex items-center gap-1.5">
          {item.contribution > 0 ? (
            <TrendingUp className="h-3.5 w-3.5 text-red-500" />
          ) : item.contribution < 0 ? (
            <TrendingDown className="h-3.5 w-3.5 text-emerald-500" />
          ) : (
            <Minus className="h-3.5 w-3.5 text-muted-foreground" />
          )}
          <span className={`font-semibold text-xs ${item.contribution > 0 ? "text-red-500" : item.contribution < 0 ? "text-emerald-500" : "text-muted-foreground"}`}>
            {item.contribution > 0 ? "+" : ""}{item.contribution.toFixed(4)}
          </span>
        </div>
      </div>
      <div className="flex items-center gap-2 h-2">
        <div className="flex-1 flex justify-end">
          {item.contribution < 0 && (
            <div className="h-2 rounded-full bg-emerald-500" style={{ width: `${width}%` }} />
          )}
        </div>
        <div className="w-px h-full bg-border" />
        <div className="flex-1">
          {item.contribution > 0 && (
            <div className="h-2 rounded-full bg-red-500" style={{ width: `${width}%` }} />
          )}
        </div>
      </div>
    </div>
  );
}

function FeatureContributions({
  explainability,
  inputsUsed,
}: {
  explainability?: ExplainabilityResult;
  inputsUsed?: Record<string, number>;
}) {
  // Try to get real SHAP data first
  const hasRealShap = explainability?.feature_importance && Object.keys(explainability.feature_importance).length > 0;

  if (hasRealShap) {
    // Aggregate top features across all diseases
    const allContribs: Array<{ name: string; value: number; contribution: number; disease: string }> = [];
    const diseases = ["heart", "diabetes", "kidney"];
    for (const disease of diseases) {
      const feats = explainability!.feature_importance![disease] || [];
      feats.slice(0, 5).forEach((f: ShapContribution) => {
        allContribs.push({
          name: FEATURE_LABELS[f.feature] || f.feature,
          value: f.value,
          contribution: f.contribution,
          disease,
        });
      });
    }
    // Deduplicate by feature name, keeping highest absolute contribution
    const seen = new Map<string, typeof allContribs[0]>();
    for (const c of allContribs) {
      const existing = seen.get(c.name);
      if (!existing || Math.abs(c.contribution) > Math.abs(existing.contribution)) {
        seen.set(c.name, c);
      }
    }
    const top = Array.from(seen.values()).sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution)).slice(0, 8);

    // Per-disease SHAP summaries
    const summaries = explainability!.explanation_summary || {};

    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            SHAP Feature Importance (Real ML Explanations)
          </CardTitle>
          <CardDescription>Actual SHAP values computed per prediction — positive = increases risk</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-3">
            {top.map((item) => <SHAPContributionBar key={item.name} item={item} />)}
            <div className="flex justify-between text-xs text-muted-foreground pt-2 border-t border-border">
              <span>← Decreases risk</span>
              <span>Increases risk →</span>
            </div>
          </div>
          {(summaries.heart || summaries.diabetes || summaries.kidney) && (
            <div className="space-y-2 pt-2 border-t border-border">
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">AI Summary</p>
              {["heart", "diabetes", "kidney"].map((d) => summaries[d] && (
                <p key={d} className="text-xs text-muted-foreground">
                  <span className="font-medium capitalize text-foreground">{d}: </span>{summaries[d]}
                </p>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  // Fallback: heuristic visualization if no SHAP data
  const contributions = [
    { name: "HbA1c", value: inputsUsed?.hba1c ?? 0, contribution: inputsUsed?.hba1c ? (inputsUsed.hba1c > 6.5 ? 0.082 : inputsUsed.hba1c > 5.7 ? 0.041 : -0.032) : 0, provided: !!inputsUsed?.hba1c },
    { name: "Fasting Glucose", value: inputsUsed?.glucose ?? 0, contribution: inputsUsed?.glucose ? (inputsUsed.glucose > 126 ? 0.071 : inputsUsed.glucose > 100 ? 0.035 : -0.028) : 0, provided: !!inputsUsed?.glucose },
    { name: "BMI", value: inputsUsed?.bmi ?? 0, contribution: inputsUsed?.bmi ? (inputsUsed.bmi > 30 ? 0.063 : inputsUsed.bmi > 25 ? 0.028 : -0.025) : 0, provided: !!inputsUsed?.bmi },
    { name: "Creatinine", value: inputsUsed?.sc ?? 0, contribution: inputsUsed?.sc ? (inputsUsed.sc > 1.2 ? 0.067 : inputsUsed.sc > 0.9 ? 0.024 : -0.021) : 0, provided: !!inputsUsed?.sc },
    { name: "eGFR", value: inputsUsed?.egfr ?? 0, contribution: inputsUsed?.egfr ? (inputsUsed.egfr < 60 ? 0.073 : inputsUsed.egfr < 90 ? 0.021 : -0.031) : 0, provided: !!inputsUsed?.egfr },
  ].filter(c => c.provided && c.contribution !== 0).sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution));

  if (contributions.length === 0) return (
    <Card>
      <CardHeader><CardTitle className="text-base">SHAP Feature Contributions</CardTitle></CardHeader>
      <CardContent><p className="text-muted-foreground text-sm">Provide more health data to see which factors influenced your risk score.</p></CardContent>
    </Card>
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-blue-600" />
          Feature Contributions
        </CardTitle>
        <CardDescription>Positive values increase risk, negative values reduce risk</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {contributions.map((item) => <SHAPContributionBar key={item.name} item={item} />)}
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
  const explainability = (result as PredictionResponse).explainability;

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
        explainability={explainability}
        inputsUsed={inputsUsed as Record<string, number>}
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
