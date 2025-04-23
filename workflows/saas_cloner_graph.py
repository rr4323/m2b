"""
SaaS Cloner workflow system.

This module defines the workflow for discovering, analyzing, and enhancing
SaaS applications using a series of specialized agents.
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Union
import time
import os
import json

from langchain_core.runnables import RunnableSequence, RunnableLambda, RunnableParallel, RunnableBranch

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
from agents.knowledge_graph_agent import KnowledgeGraphAgent
from workflows.graph_rag_integration import (
    enrich_product_with_knowledge_graph,
    generate_enhanced_blueprint_with_kg,
    analyze_market_with_knowledge_graph
)

class SaasCloneGraph:
    """Workflow manager for the SaaS Cloner system."""
    
    def __init__(self):
        """Initialize the SaaS Cloner workflow."""
        self.logger = logging.getLogger("saas_cloner.graph")
        
        # Initialize the agents
        self.market_discovery_agent = MarketDiscoveryAgent()
        self.gap_analysis_agent = GapAnalysisAgent()
        self.product_blueprint_agent = ProductBlueprintAgent()
        self.design_agent = DesignAgent()
        self.frontend_agent = FrontendAgent()
        self.backend_agent = BackendAgent()
        self.devops_agent = DevOpsAgent()
        self.llm_agent = LLMAgent()
        self.test_agent = TestAgent()
        self.deploy_agent = DeployAgent()
        self.marketing_agent = MarketingAgent()
        self.analytics_agent = AnalyticsAgent()
        self.knowledge_graph_agent = KnowledgeGraphAgent()
        
        # Create the workflow
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> RunnableSequence:
        """
        Create the workflow sequence for the SaaS Cloner.
        
        Returns:
            RunnableSequence: The workflow as a sequence of agent operations
        """
        # Create wrapper functions for each agent
        market_discovery_node = self._create_agent_node(self.market_discovery_agent)
        gap_analysis_node = self._create_agent_node(self.gap_analysis_agent)
        product_blueprint_node = self._create_agent_node(self.product_blueprint_agent)
        design_node = self._create_agent_node(self.design_agent)
        
        # Create the frontend and backend parallel workflow
        frontend_node = self._create_agent_node(self.frontend_agent)
        backend_node = self._create_agent_node(self.backend_agent)
        
        # Create a branch after design to handle frontend and backend in parallel
        def design_router(state: Dict[str, Any]) -> Dict[str, Any]:
            """Route to frontend and backend agents after design"""
            self.logger.info("Design complete, routing to frontend and backend development")
            
            # Create a copy of state for each branch to avoid conflicts
            frontend_state = state.copy()
            frontend_state["_agent_context"] = "frontend"
            
            backend_state = state.copy()
            backend_state["_agent_context"] = "backend"
            
            # Run both branches - using invoke() method instead of calling the node directly
            frontend_result = frontend_node.invoke(frontend_state)
            backend_result = backend_node.invoke(backend_state)
            
            # Merge results
            merged_state = state.copy()
            if "frontend_result" in frontend_result:
                merged_state["frontend_result"] = frontend_result["frontend_result"]
            elif isinstance(frontend_result, dict):
                # Just add all results
                for key, value in frontend_result.items():
                    if key.startswith("frontend_"):
                        merged_state[key] = value
            
            if "backend_result" in backend_result:
                merged_state["backend_result"] = backend_result["backend_result"]
            elif isinstance(backend_result, dict):
                # Just add all results
                for key, value in backend_result.items():
                    if key.startswith("backend_"):
                        merged_state[key] = value
            
            merged_state["_design_completed"] = True
            return merged_state
            
        # Create the rest of the workflow nodes
        llm_node = self._create_agent_node(self.llm_agent)
        test_node = self._create_agent_node(self.test_agent)
        devops_node = self._create_agent_node(self.devops_agent)
        deploy_node = self._create_agent_node(self.deploy_agent)
        marketing_node = self._create_agent_node(self.marketing_agent)
        analytics_node = self._create_agent_node(self.analytics_agent)
        knowledge_graph_node = self._create_agent_node(self.knowledge_graph_agent)
        
        # Custom nodes for knowledge graph integration
        def enrich_market_discovery(state: Dict[str, Any]) -> Dict[str, Any]:
            """Enrich market discovery results with knowledge graph insights"""
            self.logger.info("Enhancing product discovery with knowledge graph")
            
            try:
                # Process discovered products with knowledge graph
                products = state.get("products", [])
                enhanced_products = []
                
                # Process each product asynchronously
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    for product in products:
                        # Enrich product with knowledge graph
                        enhanced_product = loop.run_until_complete(
                            enrich_product_with_knowledge_graph(product)
                        )
                        enhanced_products.append(enhanced_product)
                finally:
                    loop.close()
                
                # Replace products with enhanced products
                state["products"] = enhanced_products
                state["knowledge_graph_enabled"] = True
                
                return state
            except Exception as e:
                self.logger.error(f"Error enhancing products with knowledge graph: {e}")
                # Return original state if enhancement fails
                return state
        
        def enhance_blueprint(state: Dict[str, Any]) -> Dict[str, Any]:
            """Enhance blueprint with knowledge graph insights"""
            self.logger.info("Enhancing blueprint with knowledge graph")
            
            try:
                product = state.get("product", {})
                blueprint = state.get("product_blueprint", {})
                gaps = state.get("identified_gaps", {})
                
                # Skip if no product or blueprint
                if not product or not blueprint:
                    return state
                
                # Enhance blueprint with knowledge graph
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    enhanced_blueprint = loop.run_until_complete(
                        generate_enhanced_blueprint_with_kg(product, gaps)
                    )
                    
                    # Replace blueprint with enhanced blueprint
                    state["product_blueprint"] = enhanced_blueprint
                    state["knowledge_graph_enhanced_blueprint"] = True
                finally:
                    loop.close()
                
                return state
            except Exception as e:
                self.logger.error(f"Error enhancing blueprint with knowledge graph: {e}")
                # Return original state if enhancement fails
                return state
        
        # Build the sequential workflow using .pipe() method to chain steps
        workflow = (
            RunnableLambda(self._normalize_input)
            .pipe(market_discovery_node)
            .pipe(RunnableLambda(enrich_market_discovery))  # Enhance products with knowledge graph
            .pipe(gap_analysis_node)
            .pipe(product_blueprint_node)
            .pipe(RunnableLambda(enhance_blueprint))  # Enhance blueprint with knowledge graph
            .pipe(design_node)
            .pipe(RunnableLambda(design_router))
            .pipe(llm_node)
            .pipe(test_node)
            .pipe(devops_node)
            .pipe(deploy_node)
            .pipe(marketing_node)
            .pipe(analytics_node)
            .pipe(RunnableLambda(self._finalize_workflow))
        )
        
        return workflow
    
    def _normalize_input(self, input_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Normalize the input data to ensure it's a dictionary.
        
        Args:
            input_data: The input data, which could be a string or dictionary
            
        Returns:
            Dict[str, Any]: Normalized input data as a dictionary
        """
        if isinstance(input_data, str):
            return {"category": input_data}
        return input_data
    
    def _create_agent_node(self, agent: Any) -> RunnableLambda:
        """
        Create a RunnableLambda wrapper for an agent.
        
        Args:
            agent: The agent object
            
        Returns:
            RunnableLambda: A runnable that processes the agent with the given state
        """
        def agent_function(state: Dict[str, Any]) -> Dict[str, Any]:
            # Function to process the agent synchronously
            async def async_process():
                # Update agent state if run_id is provided
                run_id = state.get("run_id")
                agent_states = state.get("agent_states")
                
                if run_id and agent_states and run_id in agent_states:
                    agent_states[run_id]["current_agent"] = agent.name
                    agent_states[run_id]["updated_at"] = time.time()
                
                # Log the agent execution
                self.logger.info(f"Running agent: {agent.name}")
                
                try:
                    # Run the agent
                    result = await agent.run(state)
                    
                    # Update the state with the agent's result
                    new_state = {**state, **result}
                    
                    # Update progress if agent states is provided
                    if run_id and agent_states and run_id in agent_states:
                        # Map agents to progress percentages
                        agent_progress = {
                            "Market Discovery Agent": 8,
                            "Knowledge Graph Agent": 15,
                            "Gap Analysis Agent": 22,
                            "Product Blueprint Agent": 30,
                            "Design Agent": 40,
                            "Frontend Agent": 50,
                            "Backend Agent": 60,
                            "LLM Agent": 70,
                            "Test Agent": 80,
                            "DevOps Agent": 85,
                            "Deploy Agent": 90,
                            "Marketing Agent": 95,
                            "Analytics Agent": 100,
                        }
                        
                        # Update the progress
                        progress = agent_progress.get(agent.name, 0)
                        agent_states[run_id]["progress"] = progress
                        agent_states[run_id]["updated_at"] = time.time()
                        
                        # Store the agent result in the state
                        agent_states[run_id]["results"][agent.name] = result
                    
                    return new_state
                except Exception as e:
                    self.logger.error(f"Error running agent {agent.name}: {e}", exc_info=True)
                    return {**state, "error": str(e), "failed_agent": agent.name}
            
            # Run the async function and return the result
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(async_process())
                return result
            finally:
                loop.close()
        
        # Create and return a RunnableLambda from the function
        return RunnableLambda(agent_function)
    
    def _finalize_workflow(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the final state of the workflow.
        
        Args:
            state: The final workflow state
            
        Returns:
            Dict[str, Any]: The processed final state
        """
        self.logger.info("Finalizing workflow")
        
        # Create a summary of the workflow result
        summary = {
            "success": "error" not in state,
            "timestamp": time.time(),
        }
        
        if "error" in state:
            summary["error"] = state["error"]
            summary["failed_agent"] = state.get("failed_agent", "Unknown")
        
        result = {**state, "summary": summary}
        
        # Save the result to a file
        run_id = state.get("run_id")
        self._save_result(result, run_id)
        
        return result
    
    async def run(self, input_data: Any, run_id: Optional[str] = None, agent_states: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the workflow with the given input data.
        
        Args:
            input_data: The input data for the workflow
            run_id: Optional ID for tracking the run
            agent_states: Optional dictionary to store agent states
            
        Returns:
            Dict[str, Any]: The result of the workflow
        """
        self.logger.info(f"Starting SaaS Cloner workflow with input: {input_data}")
        
        # Prepare the input state
        state = self._normalize_input(input_data)
        
        # Add run_id and agent_states to the input if provided
        if run_id is not None:
            state["run_id"] = run_id
        
        if agent_states is not None:
            state["agent_states"] = agent_states
            
            # Initialize the agent state for this run if it doesn't exist
            if run_id and run_id not in agent_states:
                agent_states[run_id] = {
                    "start_time": time.time(),
                    "current_agent": None,
                    "progress": 0,
                    "updated_at": time.time(),
                    "results": {}
                }
        
        try:
            # Run the workflow
            result = await self.workflow.ainvoke(state)
            self.logger.info("SaaS Cloner workflow completed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Error running SaaS Cloner workflow: {e}", exc_info=True)
            error_result = {
                **state,
                "error": str(e),
                "summary": {
                    "success": False,
                    "error": str(e),
                    "timestamp": time.time()
                }
            }
            self._save_result(error_result, run_id)
            return error_result
    
    def run_sync(self, input_data: Any, run_id: Optional[str] = None, agent_states: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the workflow synchronously with the given input data.
        
        Args:
            input_data: The input data for the workflow
            run_id: Optional ID for tracking the run
            agent_states: Optional dictionary to store agent states
            
        Returns:
            Dict[str, Any]: The result of the workflow
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.run(input_data, run_id, agent_states))
        loop.close()
        return result
    
    def _save_result(self, result: Dict[str, Any], run_id: Optional[str] = None) -> None:
        """
        Save the workflow result to a file.
        
        Args:
            result: The workflow result
            run_id: Optional ID for the run
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs("output", exist_ok=True)
            
            # Generate a filename
            filename = f"output/result_{run_id or time.strftime('%Y%m%d%H%M%S')}.json"
            
            # Save the result
            with open(filename, "w") as f:
                json.dump(result, f, indent=2)
            
            self.logger.info(f"Saved workflow result to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving workflow result: {e}", exc_info=True)
