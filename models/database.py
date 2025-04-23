"""
Database configuration and models for the SaaS Cloner system.
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
from typing import Dict, Any, List, Optional

# Create database engine
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,   # Recycle connections after an hour
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for declarative models
Base = declarative_base()

# Database models
class Project(Base):
    """Project model for SaaS clones"""
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    products = relationship("Product", back_populates="project", cascade="all, delete-orphan")
    runs = relationship("Run", back_populates="project", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert project to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "products": [product.id for product in self.products],
        }


class Product(Base):
    """Product model for SaaS apps"""
    __tablename__ = "products"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"))
    run_id = Column(String, ForeignKey("runs.id"))
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    features = Column(JSON)
    tech_stack = Column(JSON)
    market_analysis = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="products")
    run = relationship("Run", back_populates="products")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert product to dictionary representation"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "run_id": self.run_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "features": self.features,
            "tech_stack": self.tech_stack,
            "market_analysis": self.market_analysis,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Run(Base):
    """Run model for workflow execution"""
    __tablename__ = "runs"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"))
    status = Column(String)
    current_agent = Column(String)
    progress = Column(Integer)
    error = Column(Text)
    results = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="runs")
    products = relationship("Product", back_populates="run", cascade="all, delete-orphan")
    agent_states = relationship("AgentState", back_populates="run", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert run to dictionary representation"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "status": self.status,
            "current_agent": self.current_agent,
            "progress": self.progress,
            "error": self.error,
            "results": self.results,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AgentState(Base):
    """Agent state model for tracking agent execution"""
    __tablename__ = "agent_states"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey("runs.id"))
    agent_name = Column(String, nullable=False)
    status = Column(String)
    progress = Column(Integer)
    error = Column(Text)
    results = Column(JSON)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    run = relationship("Run", back_populates="agent_states")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent state to dictionary representation"""
        return {
            "id": self.id,
            "run_id": self.run_id,
            "agent_name": self.agent_name,
            "status": self.status,
            "progress": self.progress,
            "error": self.error,
            "results": self.results,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Function to get a database session
def get_db():
    """Get a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create all tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)