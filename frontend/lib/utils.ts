import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatRelativeTime(dateString: string): string {
  const now = new Date();
  const date = new Date(dateString);
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffSec < 60) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHour < 24) return `${diffHour}h ago`;
  if (diffDay < 7) return `${diffDay}d ago`;
  return formatDate(dateString);
}

export function calculateBMI(heightCm: number, weightKg: number): number {
  if (!heightCm || !weightKg || heightCm <= 0) return 0;
  return Math.round((weightKg / Math.pow(heightCm / 100, 2)) * 10) / 10;
}

export function getRiskGradient(score: number): string {
  if (score < 20) return "from-emerald-400 to-emerald-600";
  if (score < 40) return "from-amber-400 to-amber-600";
  if (score < 65) return "from-orange-400 to-orange-600";
  return "from-red-400 to-red-600";
}

export function getCompositeScore(
  heart: number,
  diabetes: number,
  kidney: number
): number {
  return Math.round((heart * 0.4 + diabetes * 0.35 + kidney * 0.25) * 10) / 10;
}

export function formatFieldName(field: string): string {
  const map: Record<string, string> = {
    age: "Age",
    sex: "Gender",
    preg: "Pregnancies",
    height_cm: "Height (cm)",
    weight_kg: "Weight (kg)",
    bmi: "BMI",
    systolic_bp: "Systolic BP",
    diastolic_bp: "Diastolic BP",
    thalach: "Max Heart Rate",
    trestbps: "Resting BP",
    glucose: "Fasting Glucose",
    bgr: "Post-Prandial Glucose",
    hba1c: "HbA1c",
    insulin: "Insulin",
    chol: "Total Cholesterol",
    ldl: "LDL",
    hdl: "HDL",
    triglycerides: "Triglycerides",
    sc: "Serum Creatinine",
    bu: "Blood Urea",
    sod: "Sodium",
    pot: "Potassium",
    egfr: "eGFR",
    htn: "Hypertension",
    dm: "Diabetes",
    cad: "Coronary Artery Disease",
    appet: "Appetite",
    pe: "Pedal Edema",
    ane: "Anemia",
    cp: "Chest Pain Type",
    fbs: "Fasting Blood Sugar > 120",
    restecg: "Resting ECG",
    exang: "Exercise-Induced Angina",
    oldpeak: "ST Depression",
    slope: "Slope",
    ca: "Major Vessels",
    thal: "Thalassemia",
  };
  return map[field] || field.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
}
