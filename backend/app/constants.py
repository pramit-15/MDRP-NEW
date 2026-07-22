# Prediction Weights
W_ML = 0.40
W_CLINICAL = 0.60
RISK_THRESHOLD = 0.5

# Safe Defaults (from input_mapper.py)
SAFE_DEFAULTS = {
    "age": 45, "sex": 1,
    "cp": 0, "trestbps": 118, "chol": 175, "fbs": 0, "restecg": 0,
    "thalach": 150, "exang": 0, "oldpeak": 0.0, "slope": 1, "ca": 0, "thal": 2,
    "preg": 0, "glucose": 95, "bloodpressure": 78, "skin": 22,
    "insulin": 10, "bmi": 22.5, "dpf": 0.37,
    "bp": 78, "bgr": 115, "bu": 14, "sc": 0.9, "sod": 140, "pot": 4.0,
    "htn": 0, "dm": 0, "cad": 0, "appet": 1, "pe": 0, "ane": 0,
    "hba1c": 5.3, "ldl": 90, "hdl": 55, "triglycerides": 115, "egfr": 95,
}

# Normal Values (from clinical_risk.py)
_NORMAL = {
    "age": 45.0, "bmi": 22.5, "chol": 175.0, "triglycerides": 115.0,
    "ldl": 90.0, "hdl": 55.0, "trestbps": 118.0, "hba1c": 5.3,
    "fbs": 0.0,
    "glucose": 95.0, "bgr": 115.0, "egfr": 95.0, "sc": 0.9, "bu": 14.0,
    "sod": 140.0, "pot": 4.0,
    "htn": 0.0, "dm": 0.0, "cad": 0.0,
    "appet": 1.0, "pe": 0.0, "ane": 0.0
}

# API Fields (from api.py)
ALL_LAB_FIELDS = [
    "glucose", "bgr", "hba1c", "insulin",
    "chol", "ldl", "hdl", "triglycerides",
    "sc", "bu", "sod", "pot", "egfr",
    "htn", "dm", "cad", "appet", "pe", "ane",
]

FIELD_BOUNDS = {
    "age":          (1,   120),
    "height_cm":    (50,  300),
    "weight_kg":    (20,  300),
    "bmi":          (10,  80),
    "glucose":      (40,  700),
    "bgr":          (40,  700),   # post-prandial / random blood glucose
    "hba1c":        (3.0, 20.0),
    "insulin":      (1,   800),
    "chol":         (80,  500),
    "ldl":          (20,  400),
    "hdl":          (10,  150),
    "triglycerides":(20,  1500),
    "sc":           (0.2, 20.0),
    "bu":           (5,   400),
    "sod":          (100, 175),
    "pot":          (1.5, 9.0),
    "egfr":         (1,   200),
    "thalach":      (30,  250),   # heart rate
    "systolic_bp":  (50,  300),
    "diastolic_bp": (30,  160),
    "sex":          (0,   1),
    "preg":         (0,   25),
    "htn":          (0,   1),
    "dm":           (0,   1),
    "cad":          (0,   1),
    "appet":        (0,   1),
    "pe":           (0,   1),
    "ane":          (0,   1),
}

_GEMINI_PROMPT = """You are a specialist medical lab report parser.
Read the complete report text below and extract ONLY the listed values.

CRITICAL EXTRACTION RULES:
1. "glucose" = FASTING glucose only (FBS / FPG / Fasting Blood Sugar / Fasting Plasma Glucose).
   Do NOT use Estimated Average Glucose (eAG) for this field.
2. "bgr" = POST-PRANDIAL or RANDOM blood glucose (PPBS / RBS / Post Prandial Blood Sugar /
   Post Meal Glucose / Random Blood Sugar / Random Blood Glucose / 2hr Post Glucose).
   This is DIFFERENT from fasting glucose. If found, always populate this key.
3. "bu" = Blood Urea (prefer "Urea" over "BUN" if both appear).
4. "egfr" = extract ONLY if explicitly stated; never calculate from creatinine yourself.
5. "ldl", "hdl", "chol" must come from the BLOOD/SERUM lipid panel — NOT from urine reports.
6. "hba1c" = HbA1c / Glycated Haemoglobin / A1c — NOT the same as haemoglobin level.
7. For binary clinical flags (htn, dm, cad, pe, ane): use 1 if condition is mentioned as
   present/yes/positive, 0 if absent/no/normal. Use null if not mentioned.
8. "appet" = 1 for good/normal appetite, 0 for poor/reduced. null if not mentioned.
9. All numeric values must be plain numbers — NO units, NO ranges, NO comparison symbols.
10. Return null for any key not found or not clearly readable in the report.

Return ONLY a valid JSON object with exactly these keys:
{
  "age":          <integer or null>,
  "systolic_bp":  <number or null>,
  "diastolic_bp": <number or null>,
  "glucose":      <number or null>,
  "bgr":          <number or null>,
  "hba1c":        <number or null>,
  "insulin":      <number or null>,
  "chol":         <number or null>,
  "ldl":          <number or null>,
  "hdl":          <number or null>,
  "triglycerides":<number or null>,
  "sc":           <number or null>,
  "bu":           <number or null>,
  "sod":          <number or null>,
  "pot":          <number or null>,
  "egfr":         <number or null>,
  "htn":          <0 or 1 or null>,
  "dm":           <0 or 1 or null>,
  "cad":          <0 or 1 or null>,
  "appet":        <0 or 1 or null>,
  "pe":           <0 or 1 or null>,
  "ane":          <0 or 1 or null>
}

No markdown. No explanation. No text before or after the JSON object.

Report text:
"""
