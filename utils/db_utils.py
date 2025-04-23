"""
Database utility functions for the SaaS Cloner system.
"""
import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import datetime

from models.database import Project, Product, Run, AgentState

logger = logging.getLogger("saas_cloner.db_utils")

# Project operations
def create_project(db: Session, project_data: Dict[str, Any]) -> Project:
    """
    Create a new project in the database.
    
    Args:
        db (Session): Database session
        project_data (Dict[str, Any]): Project data
        
    Returns:
        Project: Created project
    """
    project_id = project_data.get("id", str(uuid.uuid4()))
    
    project = Project(
        id=project_id,
        name=project_data.get("name", f"Project {project_id[:8]}"),
        description=project_data.get("description", ""),
        category=project_data.get("category", "productivity"),
        status=project_data.get("status", "created"),
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return project


def get_project(db: Session, project_id: str) -> Optional[Project]:
    """
    Get a project from the database by ID.
    
    Args:
        db (Session): Database session
        project_id (str): Project ID
        
    Returns:
        Optional[Project]: Project or None if not found
    """
    return db.query(Project).filter(Project.id == project_id).first()


def update_project(db: Session, project_id: str, project_data: Dict[str, Any]) -> Optional[Project]:
    """
    Update a project in the database.
    
    Args:
        db (Session): Database session
        project_id (str): Project ID
        project_data (Dict[str, Any]): Project data
        
    Returns:
        Optional[Project]: Updated project or None if not found
    """
    project = get_project(db, project_id)
    if not project:
        return None
    
    updatable_fields = ["name", "description", "category", "status"]
    
    for field in updatable_fields:
        if field in project_data:
            setattr(project, field, project_data[field])
    
    project.updated_at = datetime.datetime.utcnow()
    
    db.commit()
    db.refresh(project)
    
    return project


def delete_project(db: Session, project_id: str) -> bool:
    """
    Delete a project from the database.
    
    Args:
        db (Session): Database session
        project_id (str): Project ID
        
    Returns:
        bool: True if deleted, False if not found
    """
    project = get_project(db, project_id)
    if not project:
        return False
    
    db.delete(project)
    db.commit()
    
    return True


def get_all_projects(db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
    """
    Get all projects from the database.
    
    Args:
        db (Session): Database session
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        
    Returns:
        List[Project]: List of projects
    """
    return db.query(Project).offset(skip).limit(limit).all()


# Product operations
def create_product(db: Session, product_data: Dict[str, Any]) -> Product:
    """
    Create a new product in the database.
    
    Args:
        db (Session): Database session
        product_data (Dict[str, Any]): Product data
        
    Returns:
        Product: Created product
    """
    product_id = product_data.get("id", str(uuid.uuid4()))
    
    product = Product(
        id=product_id,
        project_id=product_data.get("project_id"),
        run_id=product_data.get("run_id"),
        name=product_data.get("name", f"Product {product_id[:8]}"),
        description=product_data.get("description", ""),
        category=product_data.get("category"),
        features=product_data.get("features", {}),
        tech_stack=product_data.get("tech_stack", {}),
        market_analysis=product_data.get("market_analysis", {}),
    )
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return product


def get_product(db: Session, product_id: str) -> Optional[Product]:
    """
    Get a product from the database by ID.
    
    Args:
        db (Session): Database session
        product_id (str): Product ID
        
    Returns:
        Optional[Product]: Product or None if not found
    """
    return db.query(Product).filter(Product.id == product_id).first()


def get_project_products(db: Session, project_id: str) -> List[Product]:
    """
    Get all products for a project.
    
    Args:
        db (Session): Database session
        project_id (str): Project ID
        
    Returns:
        List[Product]: List of products
    """
    return db.query(Product).filter(Product.project_id == project_id).all()


# Run operations
def create_run(db: Session, run_data: Dict[str, Any]) -> Run:
    """
    Create a new run in the database.
    
    Args:
        db (Session): Database session
        run_data (Dict[str, Any]): Run data
        
    Returns:
        Run: Created run
    """
    run_id = run_data.get("id", str(uuid.uuid4()))
    
    run = Run(
        id=run_id,
        project_id=run_data.get("project_id"),
        status=run_data.get("status", "started"),
        current_agent=run_data.get("current_agent"),
        progress=run_data.get("progress", 0),
        results=run_data.get("results", {}),
    )
    
    db.add(run)
    db.commit()
    db.refresh(run)
    
    return run


def get_run(db: Session, run_id: str) -> Optional[Run]:
    """
    Get a run from the database by ID.
    
    Args:
        db (Session): Database session
        run_id (str): Run ID
        
    Returns:
        Optional[Run]: Run or None if not found
    """
    return db.query(Run).filter(Run.id == run_id).first()


def update_run(db: Session, run_id: str, run_data: Dict[str, Any]) -> Optional[Run]:
    """
    Update a run in the database.
    
    Args:
        db (Session): Database session
        run_id (str): Run ID
        run_data (Dict[str, Any]): Run data
        
    Returns:
        Optional[Run]: Updated run or None if not found
    """
    run = get_run(db, run_id)
    if not run:
        return None
    
    updatable_fields = ["status", "current_agent", "progress", "error", "results"]
    
    for field in updatable_fields:
        if field in run_data:
            setattr(run, field, run_data[field])
    
    run.updated_at = datetime.datetime.utcnow()
    
    db.commit()
    db.refresh(run)
    
    return run


def get_project_runs(db: Session, project_id: str) -> List[Run]:
    """
    Get all runs for a project.
    
    Args:
        db (Session): Database session
        project_id (str): Project ID
        
    Returns:
        List[Run]: List of runs
    """
    return db.query(Run).filter(Run.project_id == project_id).all()


# Agent state operations
def create_agent_state(db: Session, agent_state_data: Dict[str, Any]) -> AgentState:
    """
    Create a new agent state in the database.
    
    Args:
        db (Session): Database session
        agent_state_data (Dict[str, Any]): Agent state data
        
    Returns:
        AgentState: Created agent state
    """
    agent_state = AgentState(
        run_id=agent_state_data.get("run_id"),
        agent_name=agent_state_data.get("agent_name"),
        status=agent_state_data.get("status", "running"),
        progress=agent_state_data.get("progress", 0),
        results=agent_state_data.get("results", {}),
        start_time=agent_state_data.get("start_time", datetime.datetime.utcnow()),
    )
    
    db.add(agent_state)
    db.commit()
    db.refresh(agent_state)
    
    return agent_state


def update_agent_state(db: Session, agent_state_id: int, agent_state_data: Dict[str, Any]) -> Optional[AgentState]:
    """
    Update an agent state in the database.
    
    Args:
        db (Session): Database session
        agent_state_id (int): Agent state ID
        agent_state_data (Dict[str, Any]): Agent state data
        
    Returns:
        Optional[AgentState]: Updated agent state or None if not found
    """
    agent_state = db.query(AgentState).filter(AgentState.id == agent_state_id).first()
    if not agent_state:
        return None
    
    updatable_fields = ["status", "progress", "error", "results", "end_time"]
    
    for field in updatable_fields:
        if field in agent_state_data:
            setattr(agent_state, field, agent_state_data[field])
    
    agent_state.updated_at = datetime.datetime.utcnow()
    
    db.commit()
    db.refresh(agent_state)
    
    return agent_state


def get_run_agent_states(db: Session, run_id: str) -> List[AgentState]:
    """
    Get all agent states for a run.
    
    Args:
        db (Session): Database session
        run_id (str): Run ID
        
    Returns:
        List[AgentState]: List of agent states
    """
    return db.query(AgentState).filter(AgentState.run_id == run_id).all()


def get_run_agent_state(db: Session, run_id: str, agent_name: str) -> Optional[AgentState]:
    """
    Get an agent state for a run and agent.
    
    Args:
        db (Session): Database session
        run_id (str): Run ID
        agent_name (str): Agent name
        
    Returns:
        Optional[AgentState]: Agent state or None if not found
    """
    return db.query(AgentState).filter(
        AgentState.run_id == run_id,
        AgentState.agent_name == agent_name
    ).first()