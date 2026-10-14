from __future__ import annotations
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.db import Base

def utcnow(): return datetime.utcnow()

class AutoMLJob(Base):
    __tablename__ = "automl_jobs"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    dataset_uri: Mapped[str] = mapped_column(String(300), default="")
    status: Mapped[str] = mapped_column(String(24), default="running", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

class CandidateModel(Base):
    __tablename__ = "candidate_models"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(120))
    accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    f1: Mapped[float] = mapped_column(Float, default=0.0)
    params_json: Mapped[str] = mapped_column(Text, default="{}")
    selected: Mapped[bool] = mapped_column(Boolean, default=False)
