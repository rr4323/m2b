"""
Base agent class for the SaaS Cloner system.
"""
import logging
import json
from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Base class for all agents in the SaaS Cloner system."""
    
    def __init__(self, name: str, description: str):
        """
        Initialize the agent.
        
        Args:
            name (str): The name of the agent
            description (str): A description of the agent's purpose and functionality
        """
        self.name = name
        self.description = description
        self.state: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"agent.{name}")
    
    @abstractmethod
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the agent's primary task.
        
        Args:
            input_data (Dict[str, Any]): Input data for the agent
            
        Returns:
            Dict[str, Any]: Output data from the agent
        """
        pass
    
    def set_state(self, key: str, value: Any) -> None:
        """Set a state value"""
        self.state[key] = value
        
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get a state value"""
        return self.state.get(key, default)
    
    def reset_state(self) -> None:
        """Reset the agent's state"""
        self.state = {}
    
    def log_info(self, message: str) -> None:
        """Log an info message"""
        self.logger.info(message)
    
    def log_error(self, message: str) -> None:
        """Log an error message"""
        self.logger.error(message)
    
    def log_warning(self, message: str) -> None:
        """Log a warning message"""
        self.logger.warning(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation"""
        return {
            "name": self.name,
            "description": self.description,
            "state": self.state
        }
    
    def __str__(self) -> str:
        """String representation of the agent"""
        return f"{self.name}: {self.description}"
