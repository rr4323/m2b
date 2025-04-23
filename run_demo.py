"""
Demo script for the SaaS Cloner system.
This uses sample data without attempting to scrape websites.
"""
import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any, List, Optional

from agents.knowledge_graph_agent import KnowledgeGraphAgent
from utils.openai_utils import generate_product_blueprint

import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure output directories exist
os.makedirs("output", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Constants
SAMPLE_PRODUCTS_PATH = "data/sample_products.json"
SAMPLE_GAPS_PATH = "data/sample_gaps.json"
BLUEPRINT_OUTPUT_PATH = "data/product_blueprint.json"
SAMPLE_CATEGORY = "Productivity"

async def load_sample_products() -> List[Dict[str, Any]]:
    """
    Load sample product data.
    
    Returns:
        List[Dict[str, Any]]: List of sample products
    """
    if not os.path.exists(SAMPLE_PRODUCTS_PATH):
        logger.error(f"Sample products file not found: {SAMPLE_PRODUCTS_PATH}")
        return []
    
    try:
        with open(SAMPLE_PRODUCTS_PATH, 'r', encoding='utf-8') as f:
            products = json.load(f)
        logger.info(f"Loaded {len(products)} sample products")
        return products
    except Exception as e:
        logger.error(f"Error loading sample products: {e}")
        return []

async def load_sample_gaps() -> List[Dict[str, Any]]:
    """
    Load sample gap data.
    
    Returns:
        List[Dict[str, Any]]: List of sample gaps
    """
    if not os.path.exists(SAMPLE_GAPS_PATH):
        logger.error(f"Sample gaps file not found: {SAMPLE_GAPS_PATH}")
        return []
    
    try:
        with open(SAMPLE_GAPS_PATH, 'r', encoding='utf-8') as f:
            gaps = json.load(f)
        logger.info(f"Loaded {len(gaps)} sample gaps")
        return gaps
    except Exception as e:
        logger.error(f"Error loading sample gaps: {e}")
        return []

async def create_product_blueprint(
    product_name: str,
    product_description: str,
    target_gaps: List[Dict[str, Any]],
    inspiration_products: List[Dict[str, Any]],
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Create a product blueprint for a new product.
    
    Args:
        product_name: The name of the new product
        product_description: A brief description of the new product
        target_gaps: List of gaps the new product will address
        inspiration_products: List of products that serve as inspiration
        use_cache: Whether to use cached blueprint data if available
        
    Returns:
        Dict[str, Any]: Product blueprint
    """
    # Check if we have cached blueprint data
    if use_cache and os.path.exists(BLUEPRINT_OUTPUT_PATH):
        logger.info(f"Loading cached product blueprint from {BLUEPRINT_OUTPUT_PATH}")
        with open(BLUEPRINT_OUTPUT_PATH, 'r', encoding='utf-8') as f:
            blueprint = json.load(f)
        if blueprint:
            return blueprint
    
    # If we don't have an OpenAI API key, use the default blueprint
    if not config.OPENAI_API_KEY:
        logger.info("OpenAI API not properly configured. Using default product blueprint.")
        try:
            default_blueprint_path = "data/default_product_blueprint.json"
            if os.path.exists(default_blueprint_path):
                with open(default_blueprint_path, 'r', encoding='utf-8') as f:
                    blueprint = json.load(f)
                logger.info(f"Loaded default product blueprint from {default_blueprint_path}")
            else:
                logger.warning(f"Default blueprint file not found at {default_blueprint_path}. Creating a simple blueprint.")
                blueprint = {
                    "product_overview": {
                        "name": product_name,
                        "description": product_description,
                        "positioning": "An enhanced productivity platform designed for teams who need advanced features."
                    },
                    "value_proposition": [
                        "AI-powered content creation and organization",
                        "Advanced data visualization and insights",
                        "Fully functional offline mode with seamless syncing"
                    ],
                    "target_audience": {
                        "primary": "Knowledge workers and teams in tech companies",
                        "secondary": "Researchers, students, and creative professionals"
                    },
                    "core_features": [
                        {
                            "name": "AI Content Assistant",
                            "description": "Uses GPT-4o to help users draft, summarize, and enhance content."
                        },
                        {
                            "name": "Advanced Data Visualization",
                            "description": "Interactive charts and graphs integrated directly into the workspace."
                        },
                        {
                            "name": "Offline-First Architecture",
                            "description": "Full offline functionality with smart conflict resolution."
                        }
                    ]
                }
        except Exception as e:
            logger.error(f"Error loading default blueprint: {e}")
            blueprint = {"error": "Failed to load default blueprint"}
    else:
        # Generate product blueprint using OpenAI
        logger.info(f"Generating product blueprint for {product_name}")
        blueprint = generate_product_blueprint(
            product_name,
            product_description,
            target_gaps,
            inspiration_products
        )
    
    # Save blueprint to cache
    with open(BLUEPRINT_OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(blueprint, f, indent=2, ensure_ascii=False)
    
    return blueprint

async def build_knowledge_graph(products: List[Dict[str, Any]], gaps: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build a knowledge graph of products and gaps.
    
    Args:
        products: List of analyzed products
        gaps: List of identified market gaps
        
    Returns:
        Dict[str, Any]: Information about the built knowledge graph
    """
    # Create knowledge graph agent
    kg_agent = KnowledgeGraphAgent()
    
    # Build knowledge graph
    logger.info(f"Building knowledge graph with {len(products)} products and {len(gaps)} gaps")
    result = await kg_agent.run({
        "operation": "build_graph",
        "products": products,
        "gaps": gaps
    })
    
    # Visualize the knowledge graph
    logger.info("Visualizing knowledge graph")
    visualization_path = await kg_agent.run({
        "operation": "visualize"
    })
    
    return result

async def run_demo_workflow():
    """
    Run the demo workflow using sample data.
    """
    logger.info("Starting the demo workflow")
    
    # Load sample products
    products = await load_sample_products()
    logger.info(f"Loaded {len(products)} sample products")
    
    # For demo purposes, let's just use one product to keep things simpler
    sample_product = next((p for p in products if "Notion" in p.get("name", "")), products[0])
    logger.info(f"Using sample product: {sample_product.get('name', 'Unknown Product')}")
    
    # Load sample gaps
    gaps = await load_sample_gaps()
    logger.info(f"Loaded {len(gaps)} sample gaps")
    
    # Create product blueprint
    product_name = f"Enhanced {sample_product.get('name', 'SaaS Product')}"
    product_description = f"An improved version of {sample_product.get('name', 'SaaS Product')} with additional features and capabilities"
    
    logger.info(f"Creating product blueprint for: {product_name}")
    blueprint = await create_product_blueprint(
        product_name,
        product_description,
        gaps[:3],  # Use top 3 gaps
        [sample_product],
        use_cache=True
    )
    logger.info(f"Product blueprint created for: {product_name}")
    
    # Build and visualize knowledge graph
    logger.info("Building and visualizing knowledge graph")
    kg_result = await build_knowledge_graph(products, gaps)
    
    # Complete workflow
    logger.info("Demo workflow completed")
    
    return {
        "sample_products": len(products),
        "sample_gaps": len(gaps),
        "product_blueprint": product_name,
        "knowledge_graph_stats": kg_result
    }

def main():
    """Main entry point for the demo workflow"""
    try:
        result = asyncio.run(run_demo_workflow())
        print("\n=== Demo Workflow Results ===")
        print(f"Sample Products: {result['sample_products']}")
        print(f"Sample Gaps: {result['sample_gaps']}")
        print(f"Product Blueprint: {result['product_blueprint']}")
        print(f"Knowledge Graph: {result['knowledge_graph_stats'].get('num_products', 0)} products, {result['knowledge_graph_stats'].get('num_features', 0)} features")
        print("\nCheck the 'data' directory for detailed outputs and 'output' directory for visualizations")
    except Exception as e:
        logger.error(f"Error running demo workflow: {e}", exc_info=True)

if __name__ == "__main__":
    main()