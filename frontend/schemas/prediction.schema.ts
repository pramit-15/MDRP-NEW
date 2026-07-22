import { z } from "zod";

// ─── Step 1: Basic Information ────────────────────────────────────────────────
export const basicInfoSchema = z.object({
  patient_name: z.string().min(2, "Name must be at least 2 characters").optional().or(z.literal("")),
  age: z
    .number({ error: "Age is required" })
    .min(1, "Age must be at least 1")
    .max(120, "Age must be at most 120"),
  sex: z.enum(["0", "1"], { error: "Gender is required" }),
  preg: z
    .number()
    .min(0)
    .max(25)
    .optional()
    .or(z.literal(undefined)),
  height_cm: z
    .number({ error: "Height must be a number" })
    .min(50, "Height must be at least 50 cm")
    .max(300, "Height must be at most 300 cm")
    .optional()
    .or(z.literal(undefined)),
  weight_kg: z
    .number({ error: "Weight must be a number" })
    .min(20, "Weight must be at least 20 kg")
    .max(300, "Weight must be at most 300 kg")
    .optional()
    .or(z.literal(undefined)),
  bmi: z
    .number({ error: "BMI must be a number" })
    .min(10, "BMI must be at least 10")
    .max(80, "BMI must be at most 80")
    .optional()
    .or(z.literal(undefined)),
});

// ─── Step 2: Vital Signs ──────────────────────────────────────────────────────
export const vitalsSchema = z.object({
  systolic_bp: z
    .number({ error: "Systolic BP must be a number" })
    .min(50, "Must be at least 50 mmHg")
    .max(300, "Must be at most 300 mmHg")
    .optional()
    .or(z.literal(undefined)),
  diastolic_bp: z
    .number({ error: "Diastolic BP must be a number" })
    .min(30, "Must be at least 30 mmHg")
    .max(160, "Must be at most 160 mmHg")
    .optional()
    .or(z.literal(undefined)),
  thalach: z
    .number({ error: "Heart rate must be a number" })
    .min(30, "Must be at least 30 bpm")
    .max(250, "Must be at most 250 bpm")
    .optional()
    .or(z.literal(undefined)),
});

// ─── Step 3: Lab Results ──────────────────────────────────────────────────────
export const labResultsSchema = z.object({
  glucose: z.number({ error: "Must be a number" }).min(40).max(700).optional().or(z.literal(undefined)),
  bgr: z.number({ error: "Must be a number" }).min(40).max(700).optional().or(z.literal(undefined)),
  hba1c: z.number({ error: "Must be a number" }).min(3.0).max(20.0).optional().or(z.literal(undefined)),
  insulin: z.number({ error: "Must be a number" }).min(1).max(800).optional().or(z.literal(undefined)),
  chol: z.number({ error: "Must be a number" }).min(80).max(500).optional().or(z.literal(undefined)),
  ldl: z.number({ error: "Must be a number" }).min(20).max(400).optional().or(z.literal(undefined)),
  hdl: z.number({ error: "Must be a number" }).min(10).max(150).optional().or(z.literal(undefined)),
  triglycerides: z.number({ error: "Must be a number" }).min(20).max(1500).optional().or(z.literal(undefined)),
  sc: z.number({ error: "Must be a number" }).min(0.2).max(20.0).optional().or(z.literal(undefined)),
  bu: z.number({ error: "Must be a number" }).min(5).max(400).optional().or(z.literal(undefined)),
  sod: z.number({ error: "Must be a number" }).min(100).max(175).optional().or(z.literal(undefined)),
  pot: z.number({ error: "Must be a number" }).min(1.5).max(9.0).optional().or(z.literal(undefined)),
  egfr: z.number({ error: "Must be a number" }).min(1).max(200).optional().or(z.literal(undefined)),
});

// ─── Step 4: Medical History ──────────────────────────────────────────────────
export const medicalHistorySchema = z.object({
  htn: z.enum(["0", "1"]).optional().or(z.literal(undefined)),
  dm: z.enum(["0", "1"]).optional().or(z.literal(undefined)),
  cad: z.enum(["0", "1"]).optional().or(z.literal(undefined)),
  appet: z.enum(["0", "1"]).optional().or(z.literal(undefined)),
  pe: z.enum(["0", "1"]).optional().or(z.literal(undefined)),
  ane: z.enum(["0", "1"]).optional().or(z.literal(undefined)),
});

// ─── Full Prediction Schema ───────────────────────────────────────────────────
export const predictionSchema = basicInfoSchema
  .merge(vitalsSchema)
  .merge(labResultsSchema)
  .merge(medicalHistorySchema);

export type PredictionFormData = z.infer<typeof predictionSchema>;
export type BasicInfoData = z.infer<typeof basicInfoSchema>;
export type VitalsData = z.infer<typeof vitalsSchema>;
export type LabResultsData = z.infer<typeof labResultsSchema>;
export type MedicalHistoryData = z.infer<typeof medicalHistorySchema>;
