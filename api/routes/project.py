"""
API routes for managing SaaS clone projects.
"""
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import logging
import uuid
import json
import os
from datetime import datetime

from workflows.saas_cloner_graph import SaasCloneGraph
from models.product import Product as ProductSchema, ProductCreate, ProductAnalysis, ProductList
from models.agent_state import AgentState as AgentStateSchema, AgentStateUpdate
from models.database import get_db
from utils import db_utils

# Create the router
router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
async def create_project(project_data: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Create a new SaaS clone project.
    
    Args:
        project_data: Project data including name, description, and category
        db: Database session
        
    Returns:
        Dict containing the created project information
    """
    # Generate a UUID if none is provided
    if "id" not in project_data:
        project_data["id"] = str(uuid.uuid4())
    
    # Create the project in the database
    project = db_utils.create_project(db, project_data)
    
    # Return the project as a dictionary
    return project.to_dict()

@router.get("/{project_id}", response_model=Dict[str, Any])
async def get_project(project_id: str, db: Session = Depends(get_db)):
    """
    Get project details by ID.
    
    Args:
        project_id: The ID of the project to retrieve
        db: Database session
        
    Returns:
        Dict containing the project information
    """
    project = db_utils.get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    return project.to_dict()

@router.put("/{project_id}", response_model=Dict[str, Any])
async def update_project(project_id: str, project_data: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Update project details.
    
    Args:
        project_id: The ID of the project to update
        project_data: Updated project data
        db: Database session
        
    Returns:
        Dict containing the updated project information
    """
    project = db_utils.update_project(db, project_id, project_data)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    return project.to_dict()

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str, db: Session = Depends(get_db)):
    """
    Delete a project.
    
    Args:
        project_id: The ID of the project to delete
        db: Database session
    """
    result = db_utils.delete_project(db, project_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )

@router.post("/{project_id}/run", response_model=Dict[str, Any])
async def run_project(project_id: str, run_config: Dict[str, Any], background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Run a SaaS clone project.
    
    Args:
        project_id: The ID of the project to run
        run_config: Configuration for the run
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Dict containing run information
    """
    project = db_utils.get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    # Start the run in the background
    run_id = str(uuid.uuid4())
    category = run_config.get("category", project.category)
    
    # Create a run in the database
    run_data = {
        "id": run_id,
        "project_id": project_id,
        "status": "running",
        "current_agent": "Market Discovery Agent",
        "progress": 0,
        "results": {},
    }
    
    run = db_utils.create_run(db, run_data)
    
    # Create an initial agent state record
    agent_state_data = {
        "run_id": run_id,
        "agent_name": "Market Discovery Agent",
        "status": "running",
        "progress": 0,
        "results": {},
        "start_time": datetime.now(),
    }
    
    db_utils.create_agent_state(db, agent_state_data)
    
    def run_workflow():
        try:
            # Initialize the SaaS Clone Graph
            saas_graph = SaasCloneGraph()
            
            # Get a new database session (can't reuse the request's session in a background task)
            with db.session_factory() as task_db:
                # Update run status
                db_utils.update_run(task_db, run_id, {
                    "status": "running",
                })
                
                # Prepare the agent states for this run
                run_agent_states = {
                    run_id: {
                        "start_time": datetime.now().timestamp(),
                        "current_agent": "Market Discovery Agent",
                        "progress": 0,
                        "updated_at": datetime.now().timestamp(),
                        "results": {}
                    }
                }
                
                # Run the workflow
                result = saas_graph.run_sync(category, run_id=run_id, agent_states=run_agent_states)
                
                # Update project with results
                if result and "products" in result:
                    for product in result["products"]:
                        product_data = {
                            "id": str(uuid.uuid4()),
                            "project_id": project_id,
                            "run_id": run_id,
                            "name": product.get("name", "Unnamed Product"),
                            "description": product.get("description", ""),
                            "category": product.get("category", category),
                            "features": product.get("features", {}),
                            "tech_stack": product.get("tech_stack", {}),
                            "market_analysis": product.get("market_analysis", {}),
                        }
                        db_utils.create_product(task_db, product_data)
                
                # Extract workflow progress from run_agent_states
                success = result.get("summary", {}).get("success", False)
                
                # Update run
                db_utils.update_run(task_db, run_id, {
                    "status": "completed" if success else "failed",
                    "progress": 100 if success else run_agent_states[run_id].get("progress", 0),
                    "results": result,
                })
                
                # Update project
                db_utils.update_project(task_db, project_id, {
                    "status": "completed" if success else "failed",
                })
                
        except Exception as e:
            logging.error(f"Error running workflow: {e}", exc_info=True)
            
            # Get a new database session
            with db.session_factory() as task_db:
                # Update run status
                db_utils.update_run(task_db, run_id, {
                    "status": "failed",
                    "error": str(e),
                })
                
                # Update project
                db_utils.update_project(task_db, project_id, {
                    "status": "failed",
                })
    
    background_tasks.add_task(run_workflow)
    
    return {
        "project_id": project_id,
        "run_id": run_id,
        "status": "started",
        "category": category,
    }

@router.get("/{project_id}/runs/{run_id}", response_model=Dict[str, Any])
async def get_run_status(project_id: str, run_id: str, db: Session = Depends(get_db)):
    """
    Get the status of a project run.
    
    Args:
        project_id: The ID of the project
        run_id: The ID of the run
        db: Database session
        
    Returns:
        Dict containing run status information
    """
    project = db_utils.get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    run = db_utils.get_run(db, run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run with ID {run_id} not found"
        )
    
    # Verify this run belongs to the requested project
    if run.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run with ID {run_id} not found for project {project_id}"
        )
    
    return run.to_dict()

@router.get("/{project_id}/products", response_model=List[Dict[str, Any]])
async def get_project_products(project_id: str, db: Session = Depends(get_db)):
    """
    Get all products for a project.
    
    Args:
        project_id: The ID of the project
        db: Database session
        
    Returns:
        List of product information
    """
    project = db_utils.get_project(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    products = db_utils.get_project_products(db, project_id)
    return [product.to_dict() for product in products]
