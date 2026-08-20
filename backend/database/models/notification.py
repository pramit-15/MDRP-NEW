import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from backend.database.base import Base

def utcnow():
    return datetime.now(timezone.utc)

def _uuid_str():
    return str(uuid.uuid4())

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    type = Column(String(50), nullable=False) # 'risk_alert', 'prediction_complete', 'pdf_parsed', 'system'
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="info") # 'info', 'warning', 'critical'
    is_read = Column(Boolean, default=False, index=True)
    data = Column(JSON, nullable=True, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=utcnow, index=True)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user = relationship("User", backref="notifications")
