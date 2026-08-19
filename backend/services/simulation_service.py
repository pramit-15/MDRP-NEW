from typing import Dict, Any, Optional
from predict import predict_all
from backend.utils.logger import get_logger

logger = get_logger("simulation_service")

class SimulationService:
    def simulate_risk_reduction(
        self,
        base_inputs: Dict[str, Any],
        modifications: Dict[str, Any],
        base_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Simulates future disease risk reduction given modified lifestyle / biomarker parameters.
        Returns baseline scores, simulated scores, deltas, and milestone improvements.
        """
        # 1. Prepare simulated inputs by merging modifications into base_inputs
        simulated_inputs = dict(base_inputs)
        for key, val in modifications.items():
            if val is not None:
                simulated_inputs[key] = val

        # 2. Recalculate BMI if height and modified weight are provided
        height = simulated_inputs.get("height_cm") or simulated_inputs.get("height")
        weight = simulated_inputs.get("weight_kg") or simulated_inputs.get("weight")
        if height and weight and float(height) > 0:
            try:
                h_m = float(height) / 100.0
                simulated_inputs["bmi"] = round(float(weight) / (h_m * h_m), 1)
            except Exception as e:
                logger.debug(f"BMI recalculation skipped: {e}")

        # 3. Obtain Baseline Results if not provided
        if not base_results or "heart" not in base_results:
            base_pred = predict_all(base_inputs)
            base_heart = float(base_pred.get("heart", 0))
            base_diabetes = float(base_pred.get("diabetes", 0))
            base_kidney = float(base_pred.get("kidney", 0))
        else:
            base_heart = float(base_results.get("heart_risk", base_results.get("heart", 0)))
            base_diabetes = float(base_results.get("diabetes_risk", base_results.get("diabetes", 0)))
            base_kidney = float(base_results.get("kidney_risk", base_results.get("kidney", 0)))

        base_composite = round(base_heart * 0.4 + base_diabetes * 0.35 + base_kidney * 0.25, 2)

        # 4. Compute Simulated Risk Results
        sim_pred = predict_all(simulated_inputs)
        sim_heart = float(sim_pred.get("heart", 0))
        sim_diabetes = float(sim_pred.get("diabetes", 0))
        sim_kidney = float(sim_pred.get("kidney", 0))
        sim_composite = round(sim_heart * 0.4 + sim_diabetes * 0.35 + sim_kidney * 0.25, 2)

        # 5. Compute Deltas & Percentage Reductions
        delta_heart = round(sim_heart - base_heart, 2)
        delta_diabetes = round(sim_diabetes - base_diabetes, 2)
        delta_kidney = round(sim_kidney - base_kidney, 2)
        delta_composite = round(sim_composite - base_composite, 2)

        def calc_pct_reduction(base_val: float, sim_val: float) -> float:
            if base_val <= 0.01:
                return 0.0
            reduction = ((base_val - sim_val) / base_val) * 100.0
            return round(reduction, 1)

        pct_heart_reduct = calc_pct_reduction(base_heart, sim_heart)
        pct_diab_reduct = calc_pct_reduction(base_diabetes, sim_diabetes)
        pct_kidney_reduct = calc_pct_reduction(base_kidney, sim_kidney)
        pct_comp_reduct = calc_pct_reduction(base_composite, sim_composite)

        # 6. Milestone & Category Transition
        def get_level(score: float) -> str:
            if score < 25: return "Low Risk"
            if score < 50: return "Moderate Risk"
            if score < 75: return "High Risk"
            return "Critical Risk"

        base_level = get_level(base_composite)
        sim_level = get_level(sim_composite)
        category_improved = base_level != sim_level and sim_composite < base_composite

        milestones = []
        if pct_comp_reduct >= 20:
            milestones.append("Achieved over 20% overall risk reduction!")
        elif pct_comp_reduct >= 10:
            milestones.append("Achieved over 10% overall risk reduction!")

        if category_improved:
            milestones.append(f"Progressed risk category from {base_level} down to {sim_level}!")

        if pct_diab_reduct >= 25:
            milestones.append("Substantial drop in Type 2 Diabetes risk!")
        if pct_heart_reduct >= 25:
            milestones.append("Substantial drop in Cardiovascular risk!")

        return {
            "success": True,
            "baseline": {
                "heart": round(base_heart, 2),
                "diabetes": round(base_diabetes, 2),
                "kidney": round(base_kidney, 2),
                "composite": round(base_composite, 2),
                "level": base_level
            },
            "simulated": {
                "heart": round(sim_heart, 2),
                "diabetes": round(sim_diabetes, 2),
                "kidney": round(sim_kidney, 2),
                "composite": round(sim_composite, 2),
                "level": sim_level,
                "scores_detail": sim_pred.get("scores_detail", {}),
                "bmi_used": simulated_inputs.get("bmi")
            },
            "deltas": {
                "heart": delta_heart,
                "diabetes": delta_diabetes,
                "kidney": delta_kidney,
                "composite": delta_composite
            },
            "percentage_reductions": {
                "heart": pct_heart_reduct,
                "diabetes": pct_diab_reduct,
                "kidney": pct_kidney_reduct,
                "composite": pct_comp_reduct
            },
            "milestones": milestones,
            "modifications_applied": modifications
        }

simulation_service = SimulationService()
