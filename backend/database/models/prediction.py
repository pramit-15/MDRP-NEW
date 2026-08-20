import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from backend.database.base import Base

def utcnow():
    return datetime.now(timezone.utc)

def _uuid_str():
    return str(uuid.uuid4())

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Risks
    heart_risk = Column(Float, nullable=False)
    diabetes_risk = Column(Float, nullable=False)
    kidney_risk = Column(Float, nullable=False)
    
    # JSON data (works with both SQLite and PostgreSQL)
    health_condition = Column(JSON, nullable=True, default=dict)
    scores_detail = Column(JSON, nullable=True, default=dict)
    clinical_scores = Column(JSON, nullable=True, default=dict)
    inputs_used = Column(JSON, nullable=True, default=dict)
    used_defaults = Column(JSON, nullable=True, default=list)
    ai_suggestions = Column(JSON, nullable=True, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=utcnow, index=True)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    # Relationships
    user = relationship("User", back_populates="predictions")
    explanation = relationship("PredictionExplanation", back_populates="prediction", uselist=False, cascade="all, delete-orphan")
    uploaded_report = relationship("UploadedReport", back_populates="prediction", uselist=False, cascade="all, delete-orphan")

class PredictionExplanation(Base):
    __tablename__ = "prediction_explanations"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    prediction_id = Column(String(36), ForeignKey("predictions.id"), nullable=False, unique=True)
    
    # SHAP explanations and interpretations (JSON works on SQLite + Postgres)
    shap_values = Column(JSON, nullable=True, default=dict)
    feature_importance = Column(JSON, nullable=True, default=dict)
    top_features = Column(JSON, nullable=True, default=dict)
    explanation_summary = Column(JSON, nullable=True, default=dict)
    positive_contributors = Column(JSON, nullable=True, default=dict)
    negative_contributors = Column(JSON, nullable=True, default=dict)
    expected_value = Column(JSON, nullable=True, default=dict)
    base_value = Column(JSON, nullable=True, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=utcnow)
    generated_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    prediction = relationship("Prediction", back_populates="explanation")

class UploadedReport(Base):
    __tablename__ = "uploaded_reports"

    id = Column(String(36), primary_key=True, default=_uuid_str)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    prediction_id = Column(String(36), ForeignKey("predictions.id"), nullable=True, unique=True)
    
    filename = Column(String, nullable=False)
    parsed_data = Column(JSON, nullable=True, default=dict)
    raw_text = Column(Text, nullable=True)
    method = Column(String(50), nullable=True)
    file_size = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user = relationship("User", backref="uploaded_reports")
    prediction = relationship("Prediction", back_populates="uploaded_report")
