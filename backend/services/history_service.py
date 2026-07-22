from backend.database import get_db_session
from backend.repositories.user_repository import UserRepository
from backend.repositories.prediction_repository import PredictionRepository
from backend.utils.logger import get_logger

logger = get_logger("HistoryService")

class HistoryService:
    def get_history(self, clerk_id: str, skip: int = 0, limit: int = 10):
        with get_db_session() as session:
            user_repo = UserRepository(session)
            user = user_repo.get_by_clerk_id(clerk_id)
            if not user:
                return [], 0
                
            pred_repo = PredictionRepository(session)
            items, total = pred_repo.get_history_by_user(user.id, skip=skip, limit=limit)
            
            results = []
            for p in items:
                results.append({
                    "id": str(p.id),
                    "heart_risk": p.heart_risk,
                    "diabetes_risk": p.diabetes_risk,
                    "kidney_risk": p.kidney_risk,
                    "health_condition": p.health_condition,
                    "created_at": p.created_at.isoformat()
                })
        return results, total

    def get_history_detail(self, clerk_id: str, prediction_id: str):
        with get_db_session() as session:
            user_repo = UserRepository(session)
            user = user_repo.get_by_clerk_id(clerk_id)
            if not user:
                return None
                
            pred_repo = PredictionRepository(session)
            p = pred_repo.get_by_id_and_user(prediction_id, user.id)
            if not p:
                return None
                
            result = {
                "id": str(p.id),
                "heart_risk": p.heart_risk,
                "diabetes_risk": p.diabetes_risk,
                "kidney_risk": p.kidney_risk,
                "health_condition": p.health_condition,
                "scores_detail": p.scores_detail,
                "clinical_scores": p.clinical_scores,
                "inputs_used": p.inputs_used,
                "used_defaults": p.used_defaults,
                "created_at": p.created_at.isoformat()
            }
            
            if p.explanation:
                result["explainability"] = {
                    "shap_values": p.explanation.shap_values,
                    "feature_importance": p.explanation.feature_importance,
                    "top_features": p.explanation.top_features,
                    "explanation_summary": p.explanation.explanation_summary,
                    "positive_contributors": p.explanation.positive_contributors,
                    "negative_contributors": p.explanation.negative_contributors,
                    "expected_value": p.explanation.expected_value,
                    "base_value": p.explanation.base_value,
                }
            return result

    def delete_history(self, clerk_id: str, prediction_id: str) -> bool:
        with get_db_session() as session:
            user_repo = UserRepository(session)
            user = user_repo.get_by_clerk_id(clerk_id)
            if not user:
                return False
                
            pred_repo = PredictionRepository(session)
            return pred_repo.delete_by_id_and_user(prediction_id, user.id)
            
    def save_prediction_result(self, clerk_id: str, results: dict, patient_data: dict):
        with get_db_session() as session:
            user_repo = UserRepository(session)
            user = user_repo.get_or_create(clerk_id)
            
            pred_repo = PredictionRepository(session)
            pred = pred_repo.save_prediction(
                user_id=user.id,
                results=results,
                inputs=patient_data,
                explanation=results.get("explainability")
            )
            return str(pred.id)

history_service = HistoryService()
