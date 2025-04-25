"""
SQLAlchemy schema for SaaS Cloner: discovered apps, clone runs, and performance metrics.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class SaaSApp(Base):
    __tablename__ = "saas_apps"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String)
    category = Column(String)
    feature_list = Column(JSON)
    tech_stack = Column(JSON)
    pricing_model = Column(String)
    discovered_at = Column(DateTime, default=datetime.datetime.utcnow)
    clone_runs = relationship("CloneRun", back_populates="app")

class CloneRun(Base):
    __tablename__ = "clone_runs"
    id = Column(String, primary_key=True)
    app_id = Column(String, ForeignKey("saas_apps.id"))
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    finished_at = Column(DateTime)
    status = Column(String)
    result = Column(JSON)
    performance_metrics = relationship("PerformanceMetric", back_populates="run")
    app = relationship("SaaSApp", back_populates="clone_runs")

class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"
    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("clone_runs.id"))
    metric_name = Column(String)
    metric_value = Column(Float)
    recorded_at = Column(DateTime, default=datetime.datetime.utcnow)
    run = relationship("CloneRun", back_populates="performance_metrics")
