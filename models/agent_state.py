"""
Agent state models for the SaaS Cloner system.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class AgentStateUpdate(BaseModel):
    """Data for updating an agent's state."""
    status: Optional[str] = Field(None, description="Status of the agent (running, completed, failed)")
    progress: Optional[int] = Field(None, description="Progress of the agent (0-100)")
    current_agent: Optional[str] = Field(None, description="Currently running agent")
    error: Optional[str] = Field(None, description="Error message if the agent failed")
    results: Optional[Dict[str, Any]] = Field(None, description="Results from the agent")

class AgentState(BaseModel):
    """State of an agent in the system."""
    project_id: str = Field(..., description="ID of the project the agent is running for")
    run_id: str = Field(..., description="ID of the run")
    status: str = Field(..., description="Status of the agent (queued, running, completed, failed)")
    current_agent: str = Field(..., description="Currently running agent")
    progress: int = Field(0, description="Progress of the agent (0-100)")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    results: Dict[str, Any] = Field(default_factory=dict, description="Results from the agent")
    error: Optional[str] = Field(None, description="Error message if the agent failed")

class AgentRun(BaseModel):
    """A run of an agent in the system."""
    id: str = Field(..., description="Unique identifier for the run")
    agent_id: str = Field(..., description="ID of the agent")
    agent_name: str = Field(..., description="Name of the agent")
    status: str = Field(..., description="Status of the run (queued, running, completed, failed)")
    progress: int = Field(0, description="Progress of the run (0-100)")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    input: Dict[str, Any] = Field(..., description="Input data for the run")
    result: Optional[Dict[str, Any]] = Field(None, description="Result of the run")
    error: Optional[str] = Field(None, description="Error message if the run failed")

class AgentCapability(BaseModel):
    """Capability of an agent in the system."""
    id: str = Field(..., description="ID of the agent")
    name: str = Field(..., description="Name of the agent")
    description: str = Field(..., description="Description of the agent")
    input_schema: Dict[str, Any] = Field(..., description="Schema for the agent's input")
    output_schema: Dict[str, Any] = Field(..., description="Schema for the agent's output")

class AgentList(BaseModel):
    """List of agents in the system."""
    agents: List[Dict[str, str]] = Field(..., description="List of agents")

class RunEstimate(BaseModel):
    """Estimation for running an agent."""
    agent_id: str = Field(..., description="ID of the agent")
    agent_name: str = Field(..., description="Name of the agent")
    complexity: str = Field(..., description="Complexity of the run (low, medium, high)")
    estimated_duration_seconds: int = Field(..., description="Estimated duration in seconds")
    input_size: int = Field(..., description="Size of the input data")
