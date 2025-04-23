"""
API routes for managing SaaS clone projects.
"""
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from typing import Dict, Any, List, Optional
import logging
import uuid
import json
import os
from datetime import datetime

from workflows.saas_cloner_graph import SaasCloneGraph
from models.product import Product, ProductCreate, ProductAnalysis, ProductList
from models.agent_state import AgentState, AgentStateUpdate

# Create the router
router = APIRouter()

# In-memory storage (would be replaced with a database in production)
projects = {}
products = {}
agent_states = {}

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
async def create_project(project_data: Dict[str, Any]):
    """
    Create a new SaaS clone project.
    
    Args:
        project_data: Project data including name, description, and category
        
    Returns:
        Dict containing the created project information
    """
    project_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    
    project = {
        "id": project_id,
        "name": project_data.get("name", f"Project {project_id[:8]}"),
        "description": project_data.get("description", ""),
        "category": project_data.get("category", "productivity"),
        "status": "created",
        "created_at": created_at,
        "updated_at": created_at,
        "products": [],
    }
    
    projects[project_id] = project
    
    return project

@router.get("/{project_id}", response_model=Dict[str, Any])
async def get_project(project_id: str):
    """
    Get project details by ID.
    
    Args:
        project_id: The ID of the project to retrieve
        
    Returns:
        Dict containing the project information
    """
    if project_id not in projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    return projects[project_id]

@router.put("/{project_id}", response_model=Dict[str, Any])
async def update_project(project_id: str, project_data: Dict[str, Any]):
    """
    Update project details.
    
    Args:
        project_id: The ID of the project to update
        project_data: Updated project data
        
    Returns:
        Dict containing the updated project information
    """
    if project_id not in projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    project = projects[project_id]
    
    updatable_fields = ["name", "description", "category", "status"]
    
    for field in updatable_fields:
        if field in project_data:
            project[field] = project_data[field]
    
    project["updated_at"] = datetime.now().isoformat()
    
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str):
    """
    Delete a project.
    
    Args:
        project_id: The ID of the project to delete
    """
    if project_id not in projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    del projects[project_id]

@router.post("/{project_id}/run", response_model=Dict[str, Any])
async def run_project(project_id: str, run_config: Dict[str, Any], background_tasks: BackgroundTasks):
    """
    Run a SaaS clone project.
    
    Args:
        project_id: The ID of the project to run
        run_config: Configuration for the run
        background_tasks: FastAPI background tasks
        
    Returns:
        Dict containing run information
    """
    if project_id not in projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    project = projects[project_id]
    
    # Start the run in the background
    run_id = str(uuid.uuid4())
    category = run_config.get("category", project.get("category", "productivity"))
    
    agent_states[run_id] = {
        "project_id": project_id,
        "run_id": run_id,
        "status": "running",
        "current_agent": "Market Discovery Agent",
        "progress": 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "results": {},
    }
    
    def run_workflow():
        try:
            # Initialize the SaaS Clone Graph
            saas_graph = SaasCloneGraph()
            
            # Update agent state
            agent_states[run_id]["status"] = "running"
            agent_states[run_id]["updated_at"] = datetime.now().isoformat()
            
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
                    product_id = str(uuid.uuid4())
                    products[product_id] = {
                        "id": product_id,
                        "project_id": project_id,
                        "run_id": run_id,
                        **product,
                    }
                    if "products" not in project:
                        project["products"] = []
                    project["products"].append(product_id)
            
            # Extract workflow progress from run_agent_states
            success = result.get("summary", {}).get("success", False)
            
            # Update agent state
            agent_states[run_id]["status"] = "completed" if success else "failed"
            agent_states[run_id]["progress"] = 100 if success else run_agent_states[run_id].get("progress", 0)
            agent_states[run_id]["updated_at"] = datetime.now().isoformat()
            agent_states[run_id]["results"] = result
            
            # Update project
            project["status"] = "completed" if success else "failed"
            project["updated_at"] = datetime.now().isoformat()
            
        except Exception as e:
            logging.error(f"Error running workflow: {e}", exc_info=True)
            
            # Update agent state
            agent_states[run_id]["status"] = "failed"
            agent_states[run_id]["error"] = str(e)
            agent_states[run_id]["updated_at"] = datetime.now().isoformat()
            
            # Update project
            project["status"] = "failed"
            project["updated_at"] = datetime.now().isoformat()
    
    background_tasks.add_task(run_workflow)
    
    return {
        "project_id": project_id,
        "run_id": run_id,
        "status": "started",
        "category": category,
    }

@router.get("/{project_id}/runs/{run_id}", response_model=Dict[str, Any])
async def get_run_status(project_id: str, run_id: str):
    """
    Get the status of a project run.
    
    Args:
        project_id: The ID of the project
        run_id: The ID of the run
        
    Returns:
        Dict containing run status information
    """
    if project_id not in projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    if run_id not in agent_states:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run with ID {run_id} not found"
        )
    
    return agent_states[run_id]

@router.get("/{project_id}/products", response_model=List[Dict[str, Any]])
async def get_project_products(project_id: str):
    """
    Get all products for a project.
    
    Args:
        project_id: The ID of the project
        
    Returns:
        List of product information
    """
    if project_id not in projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    project = projects[project_id]
    project_products = []
    
    for product_id in project.get("products", []):
        if product_id in products:
            project_products.append(products[product_id])
    
    return project_products
