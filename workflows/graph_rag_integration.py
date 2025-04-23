"""
Integration module for connecting the Knowledge Graph with the SaaS Cloner workflow.
"""
import logging
from typing import Dict, Any, List, Optional

from agents.knowledge_graph_agent import KnowledgeGraphAgent

async def enrich_product_with_knowledge_graph(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich product data with information from the knowledge graph.
    
    Args:
        product_data: Original product data from the Market Discovery Agent
        
    Returns:
        Dict[str, Any]: Enhanced product data with knowledge graph insights
    """
    try:
        # Initialize the Knowledge Graph Agent
        kg_agent = KnowledgeGraphAgent()
        
        # Check if product exists in knowledge graph, add if not
        add_result = await kg_agent.run({
            "operation": "add_product",
            "product_data": product_data
        })
        
        if add_result.get("status") == "error":
            logging.warning(f"Error adding product to knowledge graph: {add_result.get('message')}")
        
        # Get enhanced analysis from knowledge graph
        analysis_result = await kg_agent.run({
            "operation": "analyze_product",
            "product_name": product_data.get("name", "")
        })
        
        # If analysis succeeded, enrich the product data
        if "status" not in analysis_result or analysis_result.get("status") != "error":
            product_data["knowledge_graph_analysis"] = {
                "similar_products": analysis_result.get("similar_products", []),
                "missing_features": analysis_result.get("missing_features", {})
            }
            
            # Add competitors if not already present
            if "competitors" not in product_data or not product_data["competitors"]:
                competitors = analysis_result.get("competitors", [])
                product_data["competitors"] = [comp.get("name") for comp in competitors]
        
        return product_data
    
    except Exception as e:
        logging.error(f"Error enriching product with knowledge graph: {e}")
        return product_data  # Return original data if enrichment fails

async def generate_enhanced_blueprint_with_kg(product_data: Dict[str, Any], gaps: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate an enhanced product blueprint using knowledge graph insights.
    
    Args:
        product_data: Product data from Market Discovery Agent
        gaps: Identified gaps from Gap Analysis Agent
        
    Returns:
        Dict[str, Any]: Enhanced product blueprint with knowledge graph recommendations
    """
    try:
        # Initialize the Knowledge Graph Agent
        kg_agent = KnowledgeGraphAgent()
        
        # Get enhancement opportunities from knowledge graph
        opportunities = await kg_agent.run({
            "operation": "find_enhancement_opportunities",
            "product_name": product_data.get("name", "")
        })
        
        # If opportunities analysis succeeded, use it to enhance the blueprint
        if "status" not in opportunities or opportunities.get("status") != "error":
            kg_recommendations = opportunities.get("enhancement_opportunities", {})
            
            # Create enhanced blueprint
            blueprint = {
                "product_name": f"Enhanced {product_data.get('name', '')}",
                "description": f"An improved version of {product_data.get('name', '')} with enhanced features and capabilities",
                "based_on": product_data.get("name", ""),
                "original_features": product_data.get("feature_list", []),
                "enhanced_features": product_data.get("feature_list", []),  # Start with original features
                "must_have_additions": kg_recommendations.get("must_have_features", []),
                "innovative_additions": kg_recommendations.get("innovative_differentiators", []),
                "ux_improvements": kg_recommendations.get("user_experience_improvements", []),
                "technical_enhancements": kg_recommendations.get("technical_enhancements", []),
                "integration_opportunities": kg_recommendations.get("integration_opportunities", []),
                "market_positioning": "Premium alternative with advanced features and improved user experience",
                "target_audience": product_data.get("target_audience", "Professionals and teams looking for advanced solutions"),
                "identified_gaps": gaps
            }
            
            # Add all the new features to the enhanced_features list
            for feature_list in [
                kg_recommendations.get("must_have_features", []),
                kg_recommendations.get("innovative_differentiators", []),
                kg_recommendations.get("user_experience_improvements", [])
            ]:
                for feature in feature_list:
                    if feature not in blueprint["enhanced_features"]:
                        blueprint["enhanced_features"].append(feature)
            
            return blueprint
        else:
            logging.warning(f"Error getting enhancement opportunities: {opportunities.get('message')}")
            # Return a basic blueprint without knowledge graph enhancements
            return {
                "product_name": f"Enhanced {product_data.get('name', '')}",
                "description": f"An improved version of {product_data.get('name', '')}",
                "based_on": product_data.get("name", ""),
                "features": product_data.get("feature_list", []),
                "identified_gaps": gaps
            }
    
    except Exception as e:
        logging.error(f"Error generating enhanced blueprint with knowledge graph: {e}")
        # Return a basic blueprint without knowledge graph enhancements
        return {
            "product_name": f"Enhanced {product_data.get('name', '')}",
            "description": f"An improved version of {product_data.get('name', '')}",
            "based_on": product_data.get("name", ""),
            "features": product_data.get("feature_list", []),
            "identified_gaps": gaps
        }

async def analyze_market_with_knowledge_graph(category: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze the market using the knowledge graph.
    
    Args:
        category: Optional category to focus the analysis on
        
    Returns:
        Dict[str, Any]: Market analysis results
    """
    try:
        # Initialize the Knowledge Graph Agent
        kg_agent = KnowledgeGraphAgent()
        
        # Get market analysis from knowledge graph
        market_analysis = await kg_agent.run({
            "operation": "market_analysis",
            "category": category
        })
        
        return market_analysis
    
    except Exception as e:
        logging.error(f"Error analyzing market with knowledge graph: {e}")
        return {
            "status": "error",
            "message": f"Failed to analyze market with knowledge graph: {str(e)}"
        }

async def visualize_knowledge_graph() -> str:
    """
    Generate a visualization of the knowledge graph.
    
    Returns:
        str: Path to the visualization file
    """
    try:
        # Initialize the Knowledge Graph Agent
        kg_agent = KnowledgeGraphAgent()
        
        # Generate visualization
        result = await kg_agent.run({
            "operation": "visualize"
        })
        
        if result.get("status") == "success":
            return result.get("visualization_path", "")
        else:
            logging.error(f"Error visualizing knowledge graph: {result.get('message')}")
            return ""
    
    except Exception as e:
        logging.error(f"Error visualizing knowledge graph: {e}")
        return ""