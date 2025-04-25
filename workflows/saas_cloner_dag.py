"""
LangGraph DAG for Multi-Agent SaaS Cloner Workflow
Connects all major agents in the logical order for end-to-end automation.
"""
from langgraph.graph import StateGraph
from agents.market_discovery_agent import MarketDiscoveryAgent
from agents.gap_analysis_agent import GapAnalysisAgent
from agents.product_blueprint_agent import ProductBlueprintAgent
from agents.design_agent import DesignAgent
from agents.frontend_agent import FrontendAgent
from agents.backend_agent import BackendAgent
from agents.devops_agent import DevOpsAgent
from agents.test_agent import TestAgent
from agents.deploy_agent import DeployAgent
from agents.analytics_agent import AnalyticsAgent
from agents.knowledge_graph_agent import KnowledgeGraphAgent
from agents.llm_agent import LLMAgent
from agents.marketing_agent import MarketingAgent
# Add FeedbackAgent, IterateAgent if/when implemented

# Initialize agents
market_discovery = MarketDiscoveryAgent()
gap_analysis = GapAnalysisAgent()
product_blueprint = ProductBlueprintAgent()
design = DesignAgent()
frontend = FrontendAgent()
backend = BackendAgent()
devops = DevOpsAgent()
test = TestAgent()
deploy = DeployAgent()
analytics = AnalyticsAgent()
knowledge_graph = KnowledgeGraphAgent()
llm = LLMAgent()
marketing = MarketingAgent()

# Define the workflow DAG
workflow = StateGraph()

# Add nodes (agents)
workflow.add_node("market_discovery", market_discovery.run)
workflow.add_node("gap_analysis", gap_analysis.run)
workflow.add_node("product_blueprint", product_blueprint.run)
workflow.add_node("design", design.run)
workflow.add_node("frontend", frontend.run)
workflow.add_node("backend", backend.run)
workflow.add_node("devops", devops.run)
workflow.add_node("test", test.run)
workflow.add_node("deploy", deploy.run)
workflow.add_node("analytics", analytics.run)
workflow.add_node("knowledge_graph", knowledge_graph.run)
workflow.add_node("llm", llm.run)
workflow.add_node("marketing", marketing.run)
# Add feedback/iterate agents as needed

# Connect nodes (edges)
workflow.add_edge("market_discovery", "gap_analysis")
workflow.add_edge("gap_analysis", "product_blueprint")
workflow.add_edge("product_blueprint", "design")
workflow.add_edge("design", "frontend")
workflow.add_edge("design", "backend")
workflow.add_edge("frontend", "devops")
workflow.add_edge("backend", "devops")
workflow.add_edge("devops", "test")
workflow.add_edge("test", "deploy")
workflow.add_edge("deploy", "analytics")
workflow.add_edge("product_blueprint", "knowledge_graph")
workflow.add_edge("frontend", "llm")
workflow.add_edge("backend", "llm")
workflow.add_edge("analytics", "marketing")
# Add more edges as needed for feedback/iteration

# Set entry and exit points
workflow.set_entry("market_discovery")
workflow.set_exit("marketing")

# Export the workflow object for use in main.py or other orchestration scripts
saas_cloner_workflow = workflow
