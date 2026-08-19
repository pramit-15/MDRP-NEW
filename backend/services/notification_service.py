from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import select, update, desc, func
from backend.database import get_db_session
from backend.database.models.notification import Notification
from backend.repositories.user_repository import UserRepository
from backend.utils.logger import get_logger

logger = get_logger("notification_service")

class NotificationService:
    def create_notification(
        self,
        clerk_id: str,
        type: str,
        title: str,
        message: str,
        severity: str = "info",
        data: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Creates and stores a notification for a user."""
        try:
            with get_db_session() as session:
                user_repo = UserRepository(session)
                user = user_repo.get_or_create(clerk_id)
                if not user:
                    return None

                notification = Notification(
                    user_id=user.id,
                    type=type,
                    title=title,
                    message=message,
                    severity=severity,
                    data=data or {}
                )
                session.add(notification)
                session.flush()
                logger.info(f"Created notification [{type}] for user {clerk_id}: {title}")
                return str(notification.id)
        except Exception as e:
            logger.exception(f"Failed to create notification for {clerk_id}: {e}")
            return None

    def dispatch_prediction_notifications(
        self,
        clerk_id: str,
        prediction_id: str,
        results: Dict[str, Any]
    ):
        """Automatically triggers completion and high-risk alerts when a prediction is made."""
        heart = results.get("heart", 0)
        diabetes = results.get("diabetes", 0)
        kidney = results.get("kidney", 0)
        
        # 1. Prediction completion notification
        composite = round(heart * 0.4 + diabetes * 0.35 + kidney * 0.25, 1)
        self.create_notification(
            clerk_id=clerk_id,
            type="prediction_complete",
            title="Assessment Complete",
            message=f"Your multi-disease risk analysis is ready. Composite risk score: {composite}%.",
            severity="info",
            data={
                "prediction_id": prediction_id,
                "composite_risk": composite,
                "heart": heart,
                "diabetes": diabetes,
                "kidney": kidney
            }
        )

        # 2. High Risk Alert if any disease risk is >= 50%
        high_risks = []
        if heart >= 50:
            high_risks.append(f"Cardiovascular ({heart:.1f}%)")
        if diabetes >= 50:
            high_risks.append(f"Diabetes ({diabetes:.1f}%)")
        if kidney >= 50:
            high_risks.append(f"Kidney Disease ({kidney:.1f}%)")

        if high_risks:
            self.create_notification(
                clerk_id=clerk_id,
                type="risk_alert",
                title="Elevated Health Risk Alert",
                message=f"Elevated risk detected in: {', '.join(high_risks)}. Please review AI suggestions and consult a physician.",
                severity="critical" if len(high_risks) > 1 or max(heart, diabetes, kidney) >= 70 else "warning",
                data={
                    "prediction_id": prediction_id,
                    "high_risks": high_risks
                }
            )

    def dispatch_pdf_parsed_notification(
        self,
        clerk_id: str,
        report_id: str,
        filename: str,
        field_count: int,
        method: str
    ):
        """Triggers a notification when a medical report PDF is parsed."""
        engine_label = "Gemini AI" if method == "gemini_ai" else "Pattern Matching"
        self.create_notification(
            clerk_id=clerk_id,
            type="pdf_parsed",
            title="Report Extraction Complete",
            message=f"Successfully extracted {field_count} biomarker values from '{filename}' using {engine_label}.",
            severity="info",
            data={
                "report_id": report_id,
                "filename": filename,
                "field_count": field_count,
                "method": method
            }
        )

    def get_user_notifications(
        self,
        clerk_id: str,
        unread_only: bool = False,
        limit: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Fetches notifications and total unread count for a user."""
        with get_db_session() as session:
            user_repo = UserRepository(session)
            user = user_repo.get_by_clerk_id(clerk_id)
            if not user:
                return [], 0

            # Count unread
            unread_stmt = select(func.count()).select_from(Notification).where(
                Notification.user_id == user.id,
                Notification.is_read == False
            )
            unread_count = session.execute(unread_stmt).scalar() or 0

            # Query notifications
            stmt = select(Notification).where(Notification.user_id == user.id)
            if unread_only:
                stmt = stmt.where(Notification.is_read == False)
            stmt = stmt.order_by(desc(Notification.created_at)).limit(limit)

            items = session.scalars(stmt).all()
            results = []
            for n in items:
                results.append({
                    "id": str(n.id),
                    "type": n.type,
                    "title": n.title,
                    "message": n.message,
                    "severity": n.severity,
                    "is_read": n.is_read,
                    "data": n.data,
                    "created_at": n.created_at.isoformat()
                })

            return results, unread_count

    def mark_as_read(self, clerk_id: str, notification_id: str) -> bool:
        """Marks a single notification as read."""
        with get_db_session() as session:
            user_repo = UserRepository(session)
            user = user_repo.get_by_clerk_id(clerk_id)
            if not user:
                return False

            stmt = select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user.id
            )
            notif = session.scalars(stmt).first()
            if notif:
                notif.is_read = True
                session.flush()
                return True
            return False

    def mark_all_as_read(self, clerk_id: str) -> int:
        """Marks all notifications as read for a user."""
        with get_db_session() as session:
            user_repo = UserRepository(session)
            user = user_repo.get_by_clerk_id(clerk_id)
            if not user:
                return 0

            stmt = update(Notification).where(
                Notification.user_id == user.id,
                Notification.is_read == False
            ).values(is_read=True)
            result = session.execute(stmt)
            session.flush()
            return result.rowcount

notification_service = NotificationService()
