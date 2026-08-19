import json
import re
from typing import Dict, Any, Optional
from flask import current_app
from backend.utils.logger import get_logger

logger = get_logger("suggestion_service")

_SUGGESTION_PROMPT_TEMPLATE = """You are a clinical AI health advisor. 
You are presented with a patient's multi-disease risk assessment report generated from machine learning models and clinical scoring guidelines (ACC/AHA 2019, ADA 2024, KDIGO 2022).

Patient Health Profile & Assessment Data:
- Age: {age} | Sex: {sex} | BMI: {bmi}
- Blood Pressure: {trestbps} mmHg (Systolic) / {bloodpressure} mmHg (Diastolic)
- Fasting Blood Sugar: {glucose} mg/dL | HbA1c: {hba1c}% | Post-Prandial Glucose: {bgr} mg/dL
- Lipid Panel: Total Cholesterol {chol} mg/dL | LDL {ldl} mg/dL | HDL {hdl} mg/dL | Triglycerides {triglycerides} mg/dL
- Renal Panel: Serum Creatinine {sc} mg/dL | Blood Urea {bu} mg/dL | eGFR {egfr} mL/min
- Pre-existing / Flags: Hypertension={htn}, Diabetes={dm}, CAD={cad}, Anemia={ane}, Pedal Edema={pe}

Calculated Multi-Disease Risk Assessment:
- Cardiovascular Disease (Heart) Risk: {heart_risk}% (Clinical Score: {heart_clinical}/100, ML: {heart_ml}%)
- Type 2 Diabetes Risk: {diabetes_risk}% (Clinical Score: {diabetes_clinical}/100, ML: {diabetes_ml}%)
- Chronic Kidney Disease Risk: {kidney_risk}% (Clinical Score: {kidney_clinical}/100, ML: {kidney_ml}%)
- Health Condition Probabilities: {health_condition}
- Key Risk Factors Identified: {top_risk_factors}

TASK:
1. FIRST, carefully analyze and understand the specific disease risks, abnormal biomarkers, and protective factors.
2. THEN, generate a structured, empathetic, actionable health improvement plan tailored specifically to these findings.
3. Keep advice practical, constructive, and evidence-based (lifestyle, diet, physical activity, habit changes, and clinical monitoring).

You MUST output ONLY a valid JSON object with EXACTLY the following structure (no markdown fences, no explanatory text outside the JSON):
{{
  "summary": "<2-3 sentence overview explaining what the risks mean in clear, reassuring, patient-friendly language>",
  "risk_breakdown": {{
    "heart": "<1-2 sentence interpretation of heart disease risk and key contributing factors>",
    "diabetes": "<1-2 sentence interpretation of diabetes risk and glycemic status>",
    "kidney": "<1-2 sentence interpretation of kidney function and renal indicators>"
  }},
  "lifestyle_suggestions": [
    {{
      "category": "Diet & Nutrition",
      "icon": "Apple",
      "priority": "High" | "Medium" | "Low",
      "title": "<Specific actionable title>",
      "advice": "<Detailed, evidence-based nutritional advice directly addressing abnormal biomarkers>",
      "action_items": [
        "<Concrete actionable daily tip 1>",
        "<Concrete actionable daily tip 2>",
        "<Concrete actionable daily tip 3>"
      ]
    }},
    {{
      "category": "Physical Activity",
      "icon": "Dumbbell",
      "priority": "High" | "Medium" | "Low",
      "title": "<Specific exercise recommendation>",
      "advice": "<Safe, structured activity advice tailored to their cardiovascular and metabolic status>",
      "action_items": [
        "<Concrete activity goal 1>",
        "<Concrete activity goal 2>"
      ]
    }},
    {{
      "category": "Routine Monitoring",
      "icon": "Stethoscope",
      "priority": "High" | "Medium" | "Low",
      "title": "<Clinical follow-up & lab testing plan>",
      "advice": "<Tests and checkups to discuss with a physician to track progress>",
      "action_items": [
        "<Monitoring recommendation 1>",
        "<Monitoring recommendation 2>"
      ]
    }},
    {{
      "category": "Daily Habits & Wellness",
      "icon": "Moon",
      "priority": "High" | "Medium" | "Low",
      "title": "<Sleep, stress, and lifestyle optimization>",
      "advice": "<Actionable habits like sleep duration, hydration, stress management>",
      "action_items": [
        "<Daily habit 1>",
        "<Daily habit 2>"
      ]
    }}
  ],
  "top_priority": "<A single, high-impact sentence highlighting the #1 most important health improvement step the patient should take right now>",
  "disclaimer": "These suggestions are AI-generated for educational and general wellness purposes. They do not constitute a clinical diagnosis or treatment plan. Always consult a qualified healthcare provider before making major medical, dietary, or exercise changes."
}}
"""


class SuggestionService:
    def __init__(self):
        self.logger = get_logger("SuggestionService")

    def generate_suggestions(
        self,
        prediction_results: Dict[str, Any],
        patient_data: Dict[str, Any],
        explainability: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generates personalized health improvement suggestions based on prediction results.
        Tries Gemini 2.0 Flash API first; falls back to an evidence-based rule generator if unavailable.
        """
        api_key = None
        try:
            api_key = current_app.config.get("GOOGLE_API_KEY")
        except RuntimeError:
            # When called outside Flask request context (e.g. testing or CLI)
            import os
            api_key = os.environ.get("GOOGLE_API_KEY")

        if api_key and api_key != "mock_key":
            try:
                suggestions = self._generate_with_gemini(api_key, prediction_results, patient_data, explainability)
                if suggestions:
                    suggestions["generated_by"] = "gemini_ai"
                    return suggestions
            except Exception as e:
                self.logger.warning(f"Gemini suggestion generation failed: {e}. Falling back to rule-based engine.")

        # Fallback to deterministic clinical rule-based suggestions
        fallback = self._generate_fallback_suggestions(prediction_results, patient_data, explainability)
        fallback["generated_by"] = "clinical_rules"
        return fallback

    def _generate_with_gemini(
        self,
        api_key: str,
        results: Dict[str, Any],
        patient_data: Dict[str, Any],
        explainability: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        from google import genai as google_genai

        # Extract top risk factors from SHAP if available
        top_factors = []
        if explainability and "top_features" in explainability:
            for disease, feats in explainability.get("top_features", {}).items():
                if isinstance(feats, list):
                    for f in feats[:3]:
                        if isinstance(f, dict) and f.get("contribution", 0) > 0:
                            top_factors.append(f"{f.get('feature')} (impact: +{f.get('contribution', 0):.3f})")

        top_factors_str = ", ".join(top_factors) if top_factors else "Derived from blood test biomarkers"

        scores_detail = results.get("scores_detail", {})
        clinical_scores = results.get("clinical_scores", {})

        prompt = _SUGGESTION_PROMPT_TEMPLATE.format(
            age=patient_data.get("age", "N/A"),
            sex="Male" if patient_data.get("sex") == 1 else "Female" if patient_data.get("sex") == 0 else "N/A",
            bmi=patient_data.get("bmi", "N/A"),
            trestbps=patient_data.get("trestbps", patient_data.get("systolic_bp", "N/A")),
            bloodpressure=patient_data.get("bloodpressure", patient_data.get("diastolic_bp", "N/A")),
            glucose=patient_data.get("glucose", "N/A"),
            hba1c=patient_data.get("hba1c", "N/A"),
            bgr=patient_data.get("bgr", "N/A"),
            chol=patient_data.get("chol", "N/A"),
            ldl=patient_data.get("ldl", "N/A"),
            hdl=patient_data.get("hdl", "N/A"),
            triglycerides=patient_data.get("triglycerides", "N/A"),
            sc=patient_data.get("sc", "N/A"),
            bu=patient_data.get("bu", "N/A"),
            egfr=patient_data.get("egfr", "N/A"),
            htn=patient_data.get("htn", 0),
            dm=patient_data.get("dm", 0),
            cad=patient_data.get("cad", 0),
            ane=patient_data.get("ane", 0),
            pe=patient_data.get("pe", 0),
            heart_risk=results.get("heart", 0),
            diabetes_risk=results.get("diabetes", 0),
            kidney_risk=results.get("kidney", 0),
            heart_clinical=scores_detail.get("heart", {}).get("clinical", clinical_scores.get("heart_clinical", 0)),
            diabetes_clinical=scores_detail.get("diabetes", {}).get("clinical", clinical_scores.get("diabetes_clinical", 0)),
            kidney_clinical=scores_detail.get("kidney", {}).get("clinical", clinical_scores.get("kidney_clinical", 0)),
            heart_ml=scores_detail.get("heart", {}).get("ml", 0),
            diabetes_ml=scores_detail.get("diabetes", {}).get("ml", 0),
            kidney_ml=scores_detail.get("kidney", {}).get("ml", 0),
            health_condition=json.dumps(results.get("health_condition", {})),
            top_risk_factors=top_factors_str
        )

        client = google_genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
        )

        raw = response.text.strip()
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            clean = re.sub(r"[^\x20-\x7E\n]", "", raw).strip()
            parsed = json.loads(clean)

        if not isinstance(parsed, dict) or "lifestyle_suggestions" not in parsed:
            self.logger.warning("Gemini response did not match expected structure.")
            return None

        return parsed

    def _generate_fallback_suggestions(
        self,
        results: Dict[str, Any],
        patient_data: Dict[str, Any],
        explainability: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        heart = float(results.get("heart", 0))
        diabetes = float(results.get("diabetes", 0))
        kidney = float(results.get("kidney", 0))

        bmi = float(patient_data.get("bmi", 23.0))
        glucose = float(patient_data.get("glucose", 95.0))
        hba1c = float(patient_data.get("hba1c", 5.4))
        sbp = float(patient_data.get("trestbps", patient_data.get("systolic_bp", 120.0)))
        dbp = float(patient_data.get("bloodpressure", patient_data.get("diastolic_bp", 80.0)))
        chol = float(patient_data.get("chol", 180.0))
        ldl = float(patient_data.get("ldl", 95.0))
        egfr = float(patient_data.get("egfr", 95.0))
        sc = float(patient_data.get("sc", 0.9))

        max_risk = max(heart, diabetes, kidney)

        # Summary
        if max_risk > 50:
            summary = (
                f"Your assessment highlights elevated risk markers, primarily in "
                f"{'cardiovascular health' if heart == max_risk else 'glycemic regulation' if diabetes == max_risk else 'renal function'}. "
                f"Implementing targeted nutritional adjustments and lifestyle routines will significantly help improve your trajectory."
            )
        elif max_risk > 30:
            summary = (
                "Your assessment indicates borderline risk levels across some physiological markers. "
                "Proactive lifestyle interventions now can prevent further risk progression and maintain optimal vitality."
            )
        else:
            summary = (
                "Your overall disease risk scores are low and well-controlled. "
                "Continue sustaining your healthy habits while prioritizing preventive wellness and annual screening."
            )

        # Risk breakdown
        heart_desc = (
            f"Heart risk is {heart:.1f}%. Blood pressure ({sbp:.0f}/{dbp:.0f} mmHg) and lipid levels "
            f"({'elevated' if sbp > 130 or ldl > 100 else 'within normal limits'}) are primary influencers."
        )
        diabetes_desc = (
            f"Diabetes risk is {diabetes:.1f}%. Fasting glucose ({glucose:.0f} mg/dL) and HbA1c ({hba1c:.1f}%) "
            f"reflect {'pre-diabetic or elevated glycemic ranges' if glucose > 100 or hba1c > 5.7 else 'healthy metabolic control'}."
        )
        kidney_desc = (
            f"Kidney risk is {kidney:.1f}%. eGFR ({egfr:.0f} mL/min) and serum creatinine ({sc:.2f} mg/dL) indicate "
            f"{'reduced filtration capacity needing clinical monitoring' if egfr < 60 or sc > 1.2 else 'good renal filtration'}."
        )

        suggestions = []

        # 1. Diet & Nutrition
        diet_priority = "High" if (diabetes > 35 or heart > 35 or bmi > 25) else "Medium"
        diet_actions = []
        if diabetes > 30 or glucose > 100:
            diet_actions.append("Prioritize complex carbohydrates with low glycemic index (oats, quinoa, legumes) over refined sugars.")
        if heart > 30 or sbp > 130 or chol > 200:
            diet_actions.append("Adopt a Mediterranean/DASH eating style: increase omega-3 fatty acids and reduce sodium to <2,000 mg/day.")
        if kidney > 30:
            diet_actions.append("Maintain moderate high-quality protein intake and avoid excessive dietary sodium to reduce renal load.")
        if not diet_actions:
            diet_actions.append("Eat a diverse rainbow of antioxidant-rich vegetables, lean proteins, and fiber.")
            diet_actions.append("Stay well-hydrated with 2-2.5 liters of water daily.")

        suggestions.append({
            "category": "Diet & Nutrition",
            "icon": "Apple",
            "priority": diet_priority,
            "title": "Cardiometabolic & Renal Nutrition Plan",
            "advice": "Tailor your daily dietary pattern to stabilize blood glucose and protect vascular integrity.",
            "action_items": diet_actions[:3]
        })

        # 2. Physical Activity
        activity_priority = "High" if (bmi > 27 or diabetes > 35 or heart > 40) else "Medium"
        activity_actions = [
            "Target 150 minutes of moderate-intensity aerobic exercise weekly (e.g., 30-min brisk walk 5x/week).",
            "Incorporate 2 days of functional resistance or strength training to enhance insulin sensitivity.",
            "Take a 10-minute light walk immediately following your largest meal of the day."
        ]
        suggestions.append({
            "category": "Physical Activity",
            "icon": "Dumbbell",
            "priority": activity_priority,
            "title": "Structured Aerobic & Resistance Training",
            "advice": "Regular physical activity directly improves insulin receptor responsiveness, endothelial health, and blood pressure regulation.",
            "action_items": activity_actions
        })

        # 3. Routine Monitoring
        monitoring_priority = "High" if max_risk > 40 else "Medium"
        monitoring_actions = []
        if sbp > 130 or heart > 35:
            monitoring_actions.append("Log home resting blood pressure twice weekly in the morning and evening.")
        if glucose > 100 or hba1c > 5.7 or diabetes > 35:
            monitoring_actions.append("Schedule a repeat HbA1c and fasting lipid panel in 3-6 months.")
        if egfr < 90 or kidney > 30:
            monitoring_actions.append("Request a routine urinalysis (uACR) and comprehensive metabolic panel with your physician.")
        if not monitoring_actions:
            monitoring_actions.append("Complete an annual comprehensive wellness examination with standard blood work.")

        suggestions.append({
            "category": "Routine Monitoring",
            "icon": "Stethoscope",
            "priority": monitoring_priority,
            "title": "Physician Check-ups & Lab Diagnostics",
            "advice": "Routine objective measurements allow early detection and validation of lifestyle improvement progress.",
            "action_items": monitoring_actions[:3]
        })

        # 4. Daily Habits & Wellness
        habit_actions = [
            "Maintain 7 to 8 hours of consistent, restorative sleep nightly to help regulate cortisol and leptin.",
            "Engage in 10 minutes of daily mindfulness, deep diaphragmatic breathing, or stress-reduction practice.",
            "Avoid nicotine products and moderate alcohol consumption to support cardiovascular longevity."
        ]
        suggestions.append({
            "category": "Daily Habits & Wellness",
            "icon": "Moon",
            "priority": "Medium",
            "title": "Sleep Hygiene & Stress Management",
            "advice": "Chronic stress and sleep deprivation directly spike systemic inflammation and sympathetic tone.",
            "action_items": habit_actions
        })

        # Top priority
        if heart > diabetes and heart > kidney and sbp > 130:
            top_priority = "Focus immediately on blood pressure management through reduced sodium intake and daily 30-minute brisk walks."
        elif diabetes >= heart and diabetes >= kidney and (glucose > 100 or hba1c > 5.7):
            top_priority = "Target glycemic control by eliminating sugary beverages and adding post-meal walking routines."
        elif kidney > heart and kidney > diabetes:
            top_priority = "Protect kidney function by optimizing blood pressure, staying hydrated, and scheduling a clinical renal evaluation."
        else:
            top_priority = "Sustain your healthy baseline with 150 minutes of weekly activity and a nutrient-dense whole-food diet."

        return {
            "summary": summary,
            "risk_breakdown": {
                "heart": heart_desc,
                "diabetes": diabetes_desc,
                "kidney": kidney_desc,
            },
            "lifestyle_suggestions": suggestions,
            "top_priority": top_priority,
            "disclaimer": "These suggestions are generated for general wellness and educational purposes. They do not constitute a medical diagnosis. Consult a physician before changing treatment regimens."
        }


suggestion_service = SuggestionService()
