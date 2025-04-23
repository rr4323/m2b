"""
Base Agent interface for all specialized agents in the SaaS Cloner system.
"""
import logging
from typing import Dict, Any

class BaseAgent:
    """
    Base class for all specialized agents in the SaaS Cloner system.
    
    Each specialized agent inherits from this base class and implements
    the `run` method to perform its specific task in the SaaS cloning workflow.
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize the base agent.
        
        Args:
            name: Name of the agent for identification
            description: Brief description of the agent's role
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"agent.{name}")
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the agent's task with the provided input data.
        
        Args:
            input_data: Data required by the agent to perform its task
                
        Returns:
            Dict[str, Any]: The result of the agent's task
        """
        self.log_info("Running agent task")
        # This method should be overridden by subclasses
        return {"message": "BaseAgent.run() should be overridden by specialized agents"}
    
    def log_info(self, message: str) -> None:
        """Log an info message"""
        self.logger.info(message)
    
    def log_error(self, message: str) -> None:
        """Log an error message"""
        self.logger.error(message)
    
    def log_warning(self, message: str) -> None:
        """Log a warning message"""
        self.logger.warning(message)
    
    def log_debug(self, message: str) -> None:
        """Log a debug message"""
        self.logger.debug(message)