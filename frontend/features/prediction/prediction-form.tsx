"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import {
  User, Activity, FlaskConical, ClipboardList, CheckCircle2,
  ChevronLeft, ChevronRight, Info, Calculator, Upload
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { Separator } from "@/components/ui/separator";

import { usePredictMutation } from "@/hooks/use-predictions";
import { calculateBMI } from "@/lib/utils";
import { predictionSchema, type PredictionFormData } from "@/schemas/prediction.schema";
import type { ParsedPdfFields } from "@/types";

// ─── Form Field with Tooltip ──────────────────────────────────────────────────

function FieldWithTooltip({
  label,
  tooltip,
  unit,
  error,
  children,
  optional = true,
}: {
  label: string;
  tooltip?: string;
  unit?: string;
  error?: string;
  children: React.ReactNode;
  optional?: boolean;
}) {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center gap-1.5">
        <Label className="text-sm">{label}</Label>
        {optional && (
          <span className="text-[10px] text-muted-foreground font-normal">(optional)</span>
        )}
        {tooltip && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Info className="h-3.5 w-3.5 text-muted-foreground cursor-help" />
            </TooltipTrigger>
            <TooltipContent side="top" className="max-w-xs">
              {tooltip}
            </TooltipContent>
          </Tooltip>
        )}
        {unit && (
          <span className="ml-auto text-xs text-muted-foreground font-normal">{unit}</span>
        )}
      </div>
      {children}
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}

// ─── Number Input Helper ──────────────────────────────────────────────────────

function NumericInput({
  value,
  onChange,
  onBlur,
  placeholder,
  min,
  max,
  step = "any",
  error,
}: {
  value: number | undefined;
  onChange: (val: number | undefined) => void;
  onBlur?: () => void;
  placeholder?: string;
  min?: number;
  max?: number;
  step?: string;
  error?: string;
}) {
  return (
    <Input
      type="number"
      inputMode="decimal"
      value={value ?? ""}
      onChange={(e) => {
        const v = e.target.value;
        onChange(v === "" ? undefined : parseFloat(v));
      }}
      onBlur={onBlur}
      placeholder={placeholder}
      min={min}
      max={max}
      step={step}
      error={error}
    />
  );
}

// ─── Steps Config ─────────────────────────────────────────────────────────────

const STEPS = [
  { id: 1, title: "Basic Info", icon: User, description: "Personal details" },
  { id: 2, title: "Vital Signs", icon: Activity, description: "Blood pressure & vitals" },
  { id: 3, title: "Lab Results", icon: FlaskConical, description: "Blood work values" },
  { id: 4, title: "Medical History", icon: ClipboardList, description: "Conditions & symptoms" },
  { id: 5, title: "Review", icon: CheckCircle2, description: "Submit prediction" },
];

// ─── Step 1: Basic Info ───────────────────────────────────────────────────────

function Step1({ form }: { form: ReturnType<typeof useForm<PredictionFormData>> }) {
  const { register, watch, setValue, formState: { errors } } = form;
  const heightCm = watch("height_cm");
  const weightKg = watch("weight_kg");
  const sex = watch("sex");

  const bmi = heightCm && weightKg ? calculateBMI(heightCm, weightKg) : undefined;

  return (
    <div className="grid sm:grid-cols-2 gap-5">
      <div className="sm:col-span-2">
        <FieldWithTooltip label="Full Name" optional>
          <Input
            {...register("patient_name")}
            placeholder="John Doe"
            error={errors.patient_name?.message}
          />
        </FieldWithTooltip>
      </div>

      <FieldWithTooltip label="Age" tooltip="Your current age in years" unit="years" optional={false}>
        <NumericInput
          value={watch("age")}
          onChange={(v) => setValue("age", v as number)}
          placeholder="25"
          min={1}
          max={120}
          step="1"
          error={errors.age?.message}
        />
      </FieldWithTooltip>

      <FieldWithTooltip label="Gender" optional={false}>
        <Select
          value={sex}
          onValueChange={(v) => setValue("sex", v as "0" | "1")}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select gender" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="1">Male</SelectItem>
            <SelectItem value="0">Female</SelectItem>
          </SelectContent>
        </Select>
        {errors.sex && <p className="text-xs text-red-500 mt-1">{errors.sex.message}</p>}
      </FieldWithTooltip>

      {sex === "0" && (
        <FieldWithTooltip
          label="Number of Pregnancies"
          tooltip="Number of times pregnant (used for diabetes risk)"
          unit="times"
        >
          <NumericInput
            value={watch("preg")}
            onChange={(v) => setValue("preg", v)}
            placeholder="0"
            min={0}
            max={25}
            step="1"
          />
        </FieldWithTooltip>
      )}

      <FieldWithTooltip label="Height" tooltip="Your height in centimeters" unit="cm">
        <NumericInput
          value={heightCm}
          onChange={(v) => {
            setValue("height_cm", v);
            if (v && weightKg) setValue("bmi", calculateBMI(v, weightKg));
          }}
          placeholder="170"
          min={50}
          max={300}
          step="1"
          error={errors.height_cm?.message}
        />
      </FieldWithTooltip>

      <FieldWithTooltip label="Weight" tooltip="Your weight in kilograms" unit="kg">
        <NumericInput
          value={weightKg}
          onChange={(v) => {
            setValue("weight_kg", v);
            if (heightCm && v) setValue("bmi", calculateBMI(heightCm, v));
          }}
          placeholder="70"
          min={20}
          max={300}
          step="0.1"
          error={errors.weight_kg?.message}
        />
      </FieldWithTooltip>

      {bmi ? (
        <div className="sm:col-span-2">
          <div className="flex items-center gap-3 p-4 rounded-xl bg-blue-600/5 border border-blue-200/50 dark:border-blue-800/30">
            <Calculator className="h-5 w-5 text-blue-600 shrink-0" />
            <div>
              <span className="font-semibold text-blue-600">Calculated BMI: {bmi}</span>
              <span className="text-muted-foreground text-sm ml-2">
                ({bmi < 18.5 ? "Underweight" : bmi < 25 ? "Normal" : bmi < 30 ? "Overweight" : "Obese"})
              </span>
            </div>
          </div>
        </div>
      ) : (
        <FieldWithTooltip
          label="BMI"
          tooltip="Body Mass Index — enter directly if you know it (or provide height/weight above)"
          unit="kg/m²"
        >
          <NumericInput
            value={watch("bmi")}
            onChange={(v) => setValue("bmi", v)}
            placeholder="22.5"
            min={10}
            max={80}
            step="0.1"
            error={errors.bmi?.message}
          />
        </FieldWithTooltip>
      )}
    </div>
  );
}

// ─── Step 2: Vital Signs ──────────────────────────────────────────────────────

function Step2({ form }: { form: ReturnType<typeof useForm<PredictionFormData>> }) {
  const { watch, setValue, formState: { errors } } = form;

  return (
    <div className="grid sm:grid-cols-2 gap-5">
      <FieldWithTooltip
        label="Systolic Blood Pressure"
        tooltip="The top number in a blood pressure reading (e.g., 120 in 120/80). Measures pressure during heartbeat."
        unit="mmHg"
      >
        <NumericInput
          value={watch("systolic_bp")}
          onChange={(v) => setValue("systolic_bp", v)}
          placeholder="120"
          min={50}
          max={300}
          step="1"
          error={errors.systolic_bp?.message}
        />
      </FieldWithTooltip>

      <FieldWithTooltip
        label="Diastolic Blood Pressure"
        tooltip="The bottom number in a blood pressure reading (e.g., 80 in 120/80). Measures pressure between heartbeats."
        unit="mmHg"
      >
        <NumericInput
          value={watch("diastolic_bp")}
          onChange={(v) => setValue("diastolic_bp", v)}
          placeholder="80"
          min={30}
          max={160}
          step="1"
          error={errors.diastolic_bp?.message}
        />
      </FieldWithTooltip>

      <FieldWithTooltip
        label="Maximum Heart Rate"
        tooltip="The highest heart rate you have achieved during exercise or stress testing (thalach)."
        unit="bpm"
      >
        <NumericInput
          value={watch("thalach")}
          onChange={(v) => setValue("thalach", v)}
          placeholder="150"
          min={30}
          max={250}
          step="1"
          error={errors.thalach?.message}
        />
      </FieldWithTooltip>
    </div>
  );
}

// ─── Step 3: Lab Results ──────────────────────────────────────────────────────

function Step3({ form }: { form: ReturnType<typeof useForm<PredictionFormData>> }) {
  const { watch, setValue, formState: { errors } } = form;

  const labFields = [
    { key: "glucose", label: "Fasting Blood Sugar", tooltip: "Blood glucose level after at least 8 hours of fasting (FBS/FPG)", unit: "mg/dL", placeholder: "95" },
    { key: "bgr", label: "Post-Prandial Glucose", tooltip: "Blood glucose measured 2 hours after a meal (PPBS/RBS). Different from fasting glucose.", unit: "mg/dL", placeholder: "115" },
    { key: "hba1c", label: "HbA1c", tooltip: "Glycated hemoglobin — reflects average blood sugar over 2-3 months. Normal: <5.7%", unit: "%", placeholder: "5.3" },
    { key: "insulin", label: "Insulin", tooltip: "Fasting serum insulin level", unit: "µU/mL", placeholder: "10" },
    { key: "chol", label: "Total Cholesterol", tooltip: "Total serum cholesterol from lipid panel. Desirable: <200 mg/dL", unit: "mg/dL", placeholder: "175" },
    { key: "ldl", label: "LDL Cholesterol", tooltip: "Low-density lipoprotein — 'bad' cholesterol. Optimal: <100 mg/dL", unit: "mg/dL", placeholder: "90" },
    { key: "hdl", label: "HDL Cholesterol", tooltip: "High-density lipoprotein — 'good' cholesterol. Good: >60 mg/dL", unit: "mg/dL", placeholder: "55" },
    { key: "triglycerides", label: "Triglycerides", tooltip: "Blood fat levels from lipid panel. Normal: <150 mg/dL", unit: "mg/dL", placeholder: "115" },
    { key: "sc", label: "Serum Creatinine", tooltip: "Kidney filtration marker. Normal range: 0.7–1.2 mg/dL (men), 0.5–1.0 (women)", unit: "mg/dL", placeholder: "0.9" },
    { key: "bu", label: "Blood Urea (BUN)", tooltip: "Blood urea nitrogen — kidney waste marker. Normal: 7–20 mg/dL", unit: "mg/dL", placeholder: "14" },
    { key: "sod", label: "Sodium", tooltip: "Serum sodium from metabolic panel. Normal: 135–145 mEq/L", unit: "mEq/L", placeholder: "140" },
    { key: "pot", label: "Potassium", tooltip: "Serum potassium. Normal: 3.5–5.0 mEq/L", unit: "mEq/L", placeholder: "4.0" },
    { key: "egfr", label: "eGFR", tooltip: "Estimated Glomerular Filtration Rate — measures kidney function. Normal: >90 mL/min/1.73m²", unit: "mL/min", placeholder: "95" },
  ] as const;

  return (
    <div className="grid sm:grid-cols-2 gap-5">
      {labFields.map((field) => (
        <FieldWithTooltip
          key={field.key}
          label={field.label}
          tooltip={field.tooltip}
          unit={field.unit}
        >
          <NumericInput
            value={watch(field.key)}
            onChange={(v) => setValue(field.key, v)}
            placeholder={field.placeholder}
            step="0.01"
            error={(errors[field.key] as { message?: string })?.message}
          />
        </FieldWithTooltip>
      ))}
    </div>
  );
}

// ─── Step 4: Medical History ──────────────────────────────────────────────────

function Step4({ form }: { form: ReturnType<typeof useForm<PredictionFormData>> }) {
  const { watch, setValue } = form;

  const binaryFields = [
    { key: "htn", label: "Hypertension", description: "High blood pressure diagnosis" },
    { key: "dm", label: "Diabetes Mellitus", description: "Diabetes diagnosis (pre-existing)" },
    { key: "cad", label: "Coronary Artery Disease", description: "CAD or history of heart disease" },
    { key: "pe", label: "Pedal Edema", description: "Swelling in feet or ankles" },
    { key: "ane", label: "Anemia", description: "Low red blood cells or hemoglobin" },
  ] as const;

  return (
    <div className="space-y-6">
      <div className="grid sm:grid-cols-2 gap-4">
        {binaryFields.map((field) => {
          const value = watch(field.key);
          return (
            <div
              key={field.key}
              className="flex items-start justify-between p-4 rounded-xl border border-border/50 hover:border-border transition-colors"
            >
              <div>
                <div className="text-sm font-medium">{field.label}</div>
                <div className="text-xs text-muted-foreground">{field.description}</div>
              </div>
              <div className="flex gap-2">
                {(["1", "0"] as const).map((v) => (
                  <button
                    key={v}
                    type="button"
                    onClick={() => setValue(field.key, value === v ? undefined : v)}
                    className={`px-3 py-1 rounded-lg text-xs font-medium border transition-colors ${
                      value === v
                        ? v === "1"
                          ? "bg-red-500 text-white border-red-500"
                          : "bg-emerald-500 text-white border-emerald-500"
                        : "bg-background text-muted-foreground border-border hover:border-foreground"
                    }`}
                  >
                    {v === "1" ? "Yes" : "No"}
                  </button>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Appetite */}
      <div className="flex items-start justify-between p-4 rounded-xl border border-border/50 hover:border-border transition-colors">
        <div>
          <div className="text-sm font-medium">Appetite</div>
          <div className="text-xs text-muted-foreground">Current appetite status (Good / Poor)</div>
        </div>
        <div className="flex gap-2">
          {([
            { v: "1", label: "Good" },
            { v: "0", label: "Poor" },
          ] as const).map(({ v, label }) => (
            <button
              key={v}
              type="button"
              onClick={() => setValue("appet", watch("appet") === v ? undefined : v)}
              className={`px-3 py-1 rounded-lg text-xs font-medium border transition-colors ${
                watch("appet") === v
                  ? "bg-blue-600 text-white border-blue-600"
                  : "bg-background text-muted-foreground border-border hover:border-foreground"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Step 5: Review ───────────────────────────────────────────────────────────

function Step5({ form, onSubmit, isLoading }: {
  form: ReturnType<typeof useForm<PredictionFormData>>;
  onSubmit: () => void;
  isLoading: boolean;
}) {
  const values = form.getValues();

  const reviewGroups = [
    {
      label: "Basic Info",
      fields: [
        { label: "Name", value: values.patient_name || "Not provided" },
        { label: "Age", value: values.age ? `${values.age} years` : "Not provided" },
        { label: "Gender", value: values.sex === "1" ? "Male" : values.sex === "0" ? "Female" : "Not provided" },
        { label: "BMI", value: values.bmi ? `${values.bmi} kg/m²` : "Not provided" },
      ],
    },
    {
      label: "Vital Signs",
      fields: [
        { label: "Blood Pressure", value: values.systolic_bp && values.diastolic_bp ? `${values.systolic_bp}/${values.diastolic_bp} mmHg` : "Not provided" },
        { label: "Max Heart Rate", value: values.thalach ? `${values.thalach} bpm` : "Not provided" },
      ],
    },
    {
      label: "Lab Results",
      fields: [
        { label: "Fasting Glucose", value: values.glucose ? `${values.glucose} mg/dL` : "Not provided" },
        { label: "HbA1c", value: values.hba1c ? `${values.hba1c}%` : "Not provided" },
        { label: "Cholesterol", value: values.chol ? `${values.chol} mg/dL` : "Not provided" },
        { label: "Creatinine", value: values.sc ? `${values.sc} mg/dL` : "Not provided" },
        { label: "eGFR", value: values.egfr ? `${values.egfr} mL/min` : "Not provided" },
      ],
    },
  ];

  return (
    <div className="space-y-6">
      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-200/50 dark:border-amber-800/30 flex gap-3">
        <Info className="h-5 w-5 text-amber-600 shrink-0 mt-0.5" />
        <div className="text-sm">
          <p className="font-medium text-amber-600">About Default Values</p>
          <p className="text-muted-foreground mt-0.5">
            Missing fields will be filled with clinically safe defaults. More data leads to more accurate predictions.
          </p>
        </div>
      </div>

      {reviewGroups.map((group) => (
        <div key={group.label}>
          <h3 className="text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wide">
            {group.label}
          </h3>
          <div className="grid sm:grid-cols-2 gap-2">
            {group.fields.map((field) => (
              <div key={field.label} className="flex items-center justify-between p-3 rounded-lg bg-muted/30 border border-border/30">
                <span className="text-sm text-muted-foreground">{field.label}</span>
                <span className={`text-sm font-medium ${field.value === "Not provided" ? "text-muted-foreground" : ""}`}>
                  {field.value}
                </span>
              </div>
            ))}
          </div>
        </div>
      ))}

      <Button
        onClick={onSubmit}
        loading={isLoading}
        size="xl"
        className="w-full mt-4"
      >
        {isLoading ? "Analyzing..." : "Run Disease Risk Prediction"}
      </Button>
    </div>
  );
}

// ─── Main Form Component ──────────────────────────────────────────────────────

interface PredictionFormProps {
  prefillData?: ParsedPdfFields;
}

export function PredictionForm({ prefillData }: PredictionFormProps) {
  const [step, setStep] = useState(1);
  const router = useRouter();
  const { mutateAsync: predict, isPending } = usePredictMutation();

  const form = useForm<PredictionFormData>({
    resolver: zodResolver(predictionSchema),
    defaultValues: prefillData
      ? {
          age: prefillData.age ?? undefined,
          systolic_bp: prefillData.systolic_bp ?? undefined,
          diastolic_bp: prefillData.diastolic_bp ?? undefined,
          glucose: prefillData.glucose ?? undefined,
          bgr: prefillData.bgr ?? undefined,
          hba1c: prefillData.hba1c ?? undefined,
          insulin: prefillData.insulin ?? undefined,
          chol: prefillData.chol ?? undefined,
          ldl: prefillData.ldl ?? undefined,
          hdl: prefillData.hdl ?? undefined,
          triglycerides: prefillData.triglycerides ?? undefined,
          sc: prefillData.sc ?? undefined,
          bu: prefillData.bu ?? undefined,
          sod: prefillData.sod ?? undefined,
          pot: prefillData.pot ?? undefined,
          egfr: prefillData.egfr ?? undefined,
          htn: prefillData.htn != null ? String(prefillData.htn) as "0" | "1" : undefined,
          dm: prefillData.dm != null ? String(prefillData.dm) as "0" | "1" : undefined,
          cad: prefillData.cad != null ? String(prefillData.cad) as "0" | "1" : undefined,
          appet: prefillData.appet != null ? String(prefillData.appet) as "0" | "1" : undefined,
          pe: prefillData.pe != null ? String(prefillData.pe) as "0" | "1" : undefined,
          ane: prefillData.ane != null ? String(prefillData.ane) as "0" | "1" : undefined,
        }
      : {},
    mode: "onChange",
  });

  const handleNext = useCallback(async () => {
    if (step < 5) setStep((s) => s + 1);
  }, [step]);

  const handleBack = useCallback(() => {
    if (step > 1) setStep((s) => s - 1);
  }, [step]);

  const handleSubmit = useCallback(async () => {
    const values = form.getValues();

    // Build payload — convert string booleans to numbers
    const payload: Record<string, number | string | undefined> = {
      age: values.age,
      sex: values.sex ? parseInt(values.sex) : undefined,
      preg: values.preg,
      bmi: values.bmi,
      height_cm: values.height_cm,
      weight_kg: values.weight_kg,
      systolic_bp: values.systolic_bp,
      diastolic_bp: values.diastolic_bp,
      thalach: values.thalach,
      glucose: values.glucose,
      bgr: values.bgr,
      hba1c: values.hba1c,
      insulin: values.insulin,
      chol: values.chol,
      ldl: values.ldl,
      hdl: values.hdl,
      triglycerides: values.triglycerides,
      sc: values.sc,
      bu: values.bu,
      sod: values.sod,
      pot: values.pot,
      egfr: values.egfr,
      htn: values.htn != null ? parseInt(values.htn) : undefined,
      dm: values.dm != null ? parseInt(values.dm) : undefined,
      cad: values.cad != null ? parseInt(values.cad) : undefined,
      appet: values.appet != null ? parseInt(values.appet) : undefined,
      pe: values.pe != null ? parseInt(values.pe) : undefined,
      ane: values.ane != null ? parseInt(values.ane) : undefined,
      patient_name: values.patient_name,
    };

    // Remove undefined values
    const clean = Object.fromEntries(
      Object.entries(payload).filter(([, v]) => v !== undefined && v !== "")
    );

    if (Object.keys(clean).length < 2) {
      toast.error("Please fill in at least a few fields before submitting");
      return;
    }

    try {
      const result = await predict(clean);
      if (result.success && result.prediction_id) {
        router.push(`/history/${result.prediction_id}`);
      } else if (result.success) {
        // Store result in sessionStorage for display
        sessionStorage.setItem("latest_prediction", JSON.stringify(result));
        router.push("/predictions/result");
      }
    } catch {
      // Error handled in hook
    }
  }, [form, predict, router]);

  const progress = (step / STEPS.length) * 100;

  return (
    <div className="max-w-2xl mx-auto">
      {/* Progress Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          {STEPS.map((s) => (
            <button
              key={s.id}
              onClick={() => s.id < step && setStep(s.id)}
              className={`flex flex-col items-center gap-1 group ${s.id <= step ? "cursor-pointer" : "cursor-default"}`}
            >
              <div
                className={`h-9 w-9 rounded-xl flex items-center justify-center transition-all duration-200 ${
                  step === s.id
                    ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20"
                    : s.id < step
                    ? "bg-emerald-500 text-white"
                    : "bg-muted text-muted-foreground"
                }`}
              >
                {s.id < step ? (
                  <CheckCircle2 className="h-5 w-5" />
                ) : (
                  <s.icon className="h-4 w-4" />
                )}
              </div>
              <span className={`text-xs font-medium hidden sm:block transition-colors ${
                step === s.id ? "text-blue-600" : "text-muted-foreground"
              }`}>
                {s.title}
              </span>
            </button>
          ))}
        </div>
        <Progress value={progress} className="h-1.5" />
        <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
          <span>Step {step} of {STEPS.length}</span>
          <span>{STEPS[step - 1].description}</span>
        </div>
      </div>

      {/* Form Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {(() => {
              const S = STEPS[step - 1];
              return <S.icon className="h-5 w-5 text-blue-600" />;
            })()}
            {STEPS[step - 1].title}
          </CardTitle>
          <CardDescription>{STEPS[step - 1].description}</CardDescription>
        </CardHeader>
        <CardContent>
          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              {step === 1 && <Step1 form={form} />}
              {step === 2 && <Step2 form={form} />}
              {step === 3 && <Step3 form={form} />}
              {step === 4 && <Step4 form={form} />}
              {step === 5 && (
                <Step5 form={form} onSubmit={handleSubmit} isLoading={isPending} />
              )}
            </motion.div>
          </AnimatePresence>

          {step < 5 && (
            <div className="flex items-center justify-between mt-8 pt-6 border-t border-border">
              <Button
                variant="outline"
                onClick={handleBack}
                disabled={step === 1}
              >
                <ChevronLeft className="h-4 w-4 mr-1" />
                Back
              </Button>
              <Button onClick={handleNext}>
                Next
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
