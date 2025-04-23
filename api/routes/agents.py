"""
API routes for interacting with agents in the SaaS Cloner system.
"""
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from typing import Dict, Any, List, Optional
import logging
import uuid
import json
from datetime import datetime

from agents.market_discovery_agent import MarketDiscoveryAgent
from agents.gap_analysis_agent import GapAnalysisAgent
from agents.product_blueprint_agent import ProductBlueprintAgent
from agents.design_agent import DesignAgent
from agents.frontend_agent import FrontendAgent
from agents.backend_agent import BackendAgent
from agents.devops_agent import DevOpsAgent
from agents.llm_agent import LLMAgent
from agents.test_agent import TestAgent
from agents.deploy_agent import DeployAgent
from agents.marketing_agent import MarketingAgent
from agents.analytics_agent import AnalyticsAgent
from models.agent_state import AgentState, AgentStateUpdate

# Create the router
router = APIRouter()

# Dictionary of available agents
available_agents = {
    "market_discovery": MarketDiscoveryAgent,
    "gap_analysis": GapAnalysisAgent,
    "product_blueprint": ProductBlueprintAgent,
    "design": DesignAgent,
    "frontend": FrontendAgent,
    "backend": BackendAgent,
    "devops": DevOpsAgent,
    "llm": LLMAgent,
    "test": TestAgent,
    "deploy": DeployAgent,
    "marketing": MarketingAgent,
    "analytics": AnalyticsAgent,
}

# In-memory storage for agent runs
agent_runs = {}

@router.get("/", response_model=List[Dict[str, str]])
async def list_agents():
    """
    List all available agents in the system.
    
    Returns:
        List of agent information dictionaries
    """
    agents_list = []
    
    for agent_id, agent_class in available_agents.items():
        agent_instance = agent_class()
        agents_list.append({
            "id": agent_id,
            "name": agent_instance.name,
            "description": agent_instance.description,
        })
    
    return agents_list

@router.post("/{agent_id}/run", response_model=Dict[str, Any])
async def run_agent(agent_id: str, input_data: Dict[str, Any], background_tasks: BackgroundTasks):
    """
    Run a specific agent with provided input data.
    
    Args:
        agent_id: The ID of the agent to run
        input_data: Input data for the agent
        background_tasks: FastAPI background tasks
        
    Returns:
        Dict containing the run information
    """
    if agent_id not in available_agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    
    agent_class = available_agents[agent_id]
    agent_instance = agent_class()
    
    run_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    
    agent_run = {
        "id": run_id,
        "agent_id": agent_id,
        "agent_name": agent_instance.name,
        "status": "queued",
        "progress": 0,
        "created_at": created_at,
        "updated_at": created_at,
        "input": input_data,
        "result": None,
        "error": None,
    }
    
    agent_runs[run_id] = agent_run
    
    def run_agent_task():
        try:
            # Update status to running
            agent_runs[run_id]["status"] = "running"
            agent_runs[run_id]["updated_at"] = datetime.now().isoformat()
            
            # Run the agent
            result = agent_instance.run_sync(input_data)
            
            # Update the run with the result
            agent_runs[run_id]["status"] = "completed"
            agent_runs[run_id]["progress"] = 100
            agent_runs[run_id]["result"] = result
            agent_runs[run_id]["updated_at"] = datetime.now().isoformat()
            
        except Exception as e:
            logging.error(f"Error running agent {agent_id}: {e}", exc_info=True)
            
            # Update the run with the error
            agent_runs[run_id]["status"] = "failed"
            agent_runs[run_id]["error"] = str(e)
            agent_runs[run_id]["updated_at"] = datetime.now().isoformat()
    
    background_tasks.add_task(run_agent_task)
    
    return {
        "run_id": run_id,
        "agent_id": agent_id,
        "agent_name": agent_instance.name,
        "status": "queued",
    }

@router.get("/runs/{run_id}", response_model=Dict[str, Any])
async def get_agent_run(run_id: str):
    """
    Get the details of a specific agent run.
    
    Args:
        run_id: The ID of the agent run
        
    Returns:
        Dict containing the run information
    """
    if run_id not in agent_runs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent run with ID {run_id} not found"
        )
    
    return agent_runs[run_id]

@router.get("/runs", response_model=List[Dict[str, Any]])
async def list_agent_runs(agent_id: Optional[str] = None, status: Optional[str] = None, limit: int = 10):
    """
    List agent runs with optional filtering.
    
    Args:
        agent_id: Optional filter by agent ID
        status: Optional filter by status
        limit: Maximum number of runs to return
        
    Returns:
        List of agent run information dictionaries
    """
    filtered_runs = []
    
    for run_id, run_data in agent_runs.items():
        if agent_id and run_data["agent_id"] != agent_id:
            continue
        
        if status and run_data["status"] != status:
            continue
        
        filtered_runs.append(run_data)
        
        if len(filtered_runs) >= limit:
            break
    
    return filtered_runs

@router.post("/{agent_id}/estimate", response_model=Dict[str, Any])
async def estimate_agent_run(agent_id: str, input_data: Dict[str, Any]):
    """
    Estimate the complexity and duration of running an agent with given input.
    
    Args:
        agent_id: The ID of the agent to estimate
        input_data: Input data for the agent
        
    Returns:
        Dict containing the estimation information
    """
    if agent_id not in available_agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    
    agent_class = available_agents[agent_id]
    agent_instance = agent_class()
    
    # This is a simplified estimation logic
    # In a real implementation, this would be more sophisticated
    input_complexity = len(json.dumps(input_data))
    
    complexity = "low"
    if input_complexity > 1000:
        complexity = "medium"
    if input_complexity > 5000:
        complexity = "high"
    
    estimated_duration = 10  # seconds
    if complexity == "medium":
        estimated_duration = 30
    if complexity == "high":
        estimated_duration = 60
    
    return {
        "agent_id": agent_id,
        "agent_name": agent_instance.name,
        "complexity": complexity,
        "estimated_duration_seconds": estimated_duration,
        "input_size": input_complexity,
    }

@router.get("/{agent_id}/capabilities", response_model=Dict[str, Any])
async def get_agent_capabilities(agent_id: str):
    """
    Get detailed information about an agent's capabilities.
    
    Args:
        agent_id: The ID of the agent
        
    Returns:
        Dict containing the agent's capabilities
    """
    if agent_id not in available_agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    
    agent_class = available_agents[agent_id]
    agent_instance = agent_class()
    
    capabilities = {
        "id": agent_id,
        "name": agent_instance.name,
        "description": agent_instance.description,
        "input_schema": {
            "type": "object",
            "properties": {},
        },
        "output_schema": {
            "type": "object",
            "properties": {},
        },
    }
    
    # Add agent-specific capabilities
    if agent_id == "market_discovery":
        capabilities["input_schema"]["properties"] = {
            "category": {
                "type": "string",
                "description": "Category of SaaS applications to discover",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of applications to discover",
            },
        }
        capabilities["output_schema"]["properties"] = {
            "products": {
                "type": "array",
                "description": "List of discovered products",
            },
            "count": {
                "type": "integer",
                "description": "Number of discovered products",
            },
            "category": {
                "type": "string",
                "description": "Category that was searched",
            },
        }
    elif agent_id == "gap_analysis":
        capabilities["input_schema"]["properties"] = {
            "product": {
                "type": "object",
                "description": "Product to analyze for gaps",
            },
        }
        capabilities["output_schema"]["properties"] = {
            "product_name": {
                "type": "string",
                "description": "Name of the analyzed product",
            },
            "reviews_analyzed": {
                "type": "integer",
                "description": "Number of reviews analyzed",
            },
            "identified_gaps": {
                "type": "object",
                "description": "Gaps identified in the product",
            },
            "improvement_opportunities": {
                "type": "object",
                "description": "Opportunities for improvement",
            },
        }
    # Additional agent capabilities would be defined similarly
    
    return capabilities
