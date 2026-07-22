from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, desc
from backend.database.models.prediction import Prediction, PredictionExplanation, UploadedReport
from backend.repositories.base_repository import BaseRepository

class PredictionRepository(BaseRepository[Prediction]):
    def __init__(self, session: Session):
        super().__init__(Prediction, session)

    def save_prediction(
        self, 
        user_id: str, 
        results: dict, 
        inputs: dict, 
        explanation: dict = None,
        uploaded_report: dict = None
    ) -> Prediction:
        # Construct prediction dict
        prediction_in = {
            "user_id": user_id,
            "heart_risk": results["heart"],
            "diabetes_risk": results["diabetes"],
            "kidney_risk": results["kidney"],
            "health_condition": results.get("health_condition", {}),
            "scores_detail": results.get("scores_detail", {}),
            "clinical_scores": results.get("clinical_scores", {}),
            "inputs_used": inputs,
            "used_defaults": results.get("used_defaults", [])
        }
        prediction = self.create(prediction_in)
        
        # Save explanation if provided
        if explanation:
            exp = PredictionExplanation(
                prediction_id=prediction.id,
                shap_values=explanation.get("shap_values", {}),
                feature_importance=explanation.get("feature_importance", {}),
                top_features=explanation.get("top_features", {}),
                explanation_summary=explanation.get("explanation_summary", {}),
                positive_contributors=explanation.get("positive_contributors", {}),
                negative_contributors=explanation.get("negative_contributors", {}),
                expected_value=explanation.get("expected_value", {}),
                base_value=explanation.get("base_value", {})
            )
            self.session.add(exp)
            
        # Save uploaded report if provided
        if uploaded_report:
            rep = UploadedReport(
                prediction_id=prediction.id, 
                filename=uploaded_report.get("filename"),
                parsed_data=uploaded_report.get("parsed_data", {})
            )
            self.session.add(rep)
            
        self.session.flush()
        return prediction

    def get_history_by_user(
        self, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 10, 
        disease_filter: str = None
    ) -> tuple[List[Prediction], int]:
        stmt = select(Prediction).where(Prediction.user_id == user_id)
        
        if disease_filter:
            # We could filter by asking if risk > threshold, but for now we just order by it
            pass
            
        # Count total
        from sqlalchemy import func
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.session.execute(count_stmt).scalar()
        
        # Get paginated
        stmt = stmt.options(
            joinedload(Prediction.explanation),
            joinedload(Prediction.uploaded_report)
        ).order_by(desc(Prediction.created_at)).offset(skip).limit(limit)
        
        items = self.session.scalars(stmt).unique().all()
        return items, total

    def get_by_id_and_user(self, prediction_id: str, user_id: str) -> Optional[Prediction]:
        stmt = select(Prediction).options(
            joinedload(Prediction.explanation),
            joinedload(Prediction.uploaded_report)
        ).where(
            Prediction.id == prediction_id,
            Prediction.user_id == user_id
        )
        return self.session.scalars(stmt).first()
        
    def delete_by_id_and_user(self, prediction_id: str, user_id: str) -> bool:
        prediction = self.get_by_id_and_user(prediction_id, user_id)
        if prediction:
            self.session.delete(prediction)
            self.session.flush()
            return True
        return False
