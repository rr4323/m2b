"""
Main entry point for the Multi-Agent SaaS Cloner & Enhancer system.
This coordinates the workflow for discovering, analyzing, and enhancing SaaS applications.
"""
import asyncio
import json
import logging
import os
from typing import Dict, Any, List, Optional

from agents.knowledge_graph_agent import KnowledgeGraphAgent
from utils.web_scraper import discover_trending_products, save_discovered_products, load_discovered_products
from utils.openai_utils import analyze_product_data, identify_market_gaps, generate_product_blueprint
from utils.knowledge_graph import knowledge_graph

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
DISCOVERY_OUTPUT_PATH = "data/discovered_products.json"
ANALYSIS_OUTPUT_PATH = "data/analyzed_products.json"
GAPS_OUTPUT_PATH = "data/identified_gaps.json"
BLUEPRINT_OUTPUT_PATH = "data/product_blueprint.json"
SAMPLE_CATEGORY = "Productivity"

async def discover_products(category: str, sources: Optional[List[str]] = None, use_cache: bool = True) -> List[Dict[str, Any]]:
    """
    Discover trending products in a category.
    
    Args:
        category: The category to discover products for
        sources: List of sources to search (producthunt, g2, capterra, reddit)
        use_cache: Whether to use cached product data if available
        
    Returns:
        List[Dict[str, Any]]: List of discovered products
    """
    # Check if we have cached product data
    if use_cache and os.path.exists(DISCOVERY_OUTPUT_PATH):
        logger.info(f"Loading cached product data from {DISCOVERY_OUTPUT_PATH}")
        products = load_discovered_products(DISCOVERY_OUTPUT_PATH)
        if products:
            return products
    
    # If no cached data or cache not wanted, scrape product data
    logger.info(f"Discovering trending products in category: {category}")
    products = discover_trending_products(category, sources)
    
    # Save discovered products to cache
    save_discovered_products(products, DISCOVERY_OUTPUT_PATH)
    
    return products

async def analyze_products(products: List[Dict[str, Any]], use_cache: bool = True) -> List[Dict[str, Any]]:
    """
    Analyze discovered products.
    
    Args:
        products: List of discovered products
        use_cache: Whether to use cached analysis data if available
        
    Returns:
        List[Dict[str, Any]]: List of analyzed products
    """
    # Check if we have cached analysis data
    if use_cache and os.path.exists(ANALYSIS_OUTPUT_PATH):
        logger.info(f"Loading cached product analysis from {ANALYSIS_OUTPUT_PATH}")
        with open(ANALYSIS_OUTPUT_PATH, 'r', encoding='utf-8') as f:
            analyzed_products = json.load(f)
        if analyzed_products:
            return analyzed_products
    
    # Analyze each product
    logger.info(f"Analyzing {len(products)} discovered products")
    analyzed_products = []
    
    for product in products:
        logger.info(f"Analyzing product: {product.get('name', 'Unknown Product')}")
        analysis = analyze_product_data(product)
        
        # Combine product data with analysis
        analyzed_product = {**product, "analysis": analysis}
        analyzed_products.append(analyzed_product)
    
    # Save analyzed products to cache
    with open(ANALYSIS_OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(analyzed_products, f, indent=2, ensure_ascii=False)
    
    return analyzed_products

async def identify_gaps(products: List[Dict[str, Any]], category: str, use_cache: bool = True) -> List[Dict[str, Any]]:
    """
    Identify market gaps based on analyzed products.
    
    Args:
        products: List of analyzed products
        category: The category of the products
        use_cache: Whether to use cached gap data if available
        
    Returns:
        List[Dict[str, Any]]: List of identified market gaps
    """
    # Check if we have cached gap data
    if use_cache and os.path.exists(GAPS_OUTPUT_PATH):
        logger.info(f"Loading cached gap analysis from {GAPS_OUTPUT_PATH}")
        with open(GAPS_OUTPUT_PATH, 'r', encoding='utf-8') as f:
            gaps = json.load(f)
        if gaps:
            return gaps
    
    # Identify market gaps
    logger.info(f"Identifying market gaps in {category} category based on {len(products)} products")
    gaps = identify_market_gaps(products, category)
    
    # If no gaps were identified, use sample gaps
    if not gaps:
        sample_gaps_path = "data/sample_gaps.json"
        if os.path.exists(sample_gaps_path):
            logger.info(f"No gaps identified. Using sample gaps from {sample_gaps_path}")
            try:
                with open(sample_gaps_path, 'r', encoding='utf-8') as f:
                    gaps = json.load(f)
                logger.info(f"Loaded {len(gaps)} sample gaps")
            except Exception as e:
                logger.error(f"Error loading sample gaps: {e}")
    
    # Save identified gaps to cache
    with open(GAPS_OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(gaps, f, indent=2, ensure_ascii=False)
    
    return gaps

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
    
    # Check if OpenAI API key is available
    if not config.OPENAI_API_KEY:
        logger.warning("OpenAI API key not found. Using default product blueprint.")
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

async def run_workflow():
    """
    Run the complete SaaS Cloner workflow from discovery to blueprint generation.
    """
    logger.info("Starting the workflow")
    
    # Discover products in the Productivity category
    logger.info(f"Starting market discovery process")
    products = await discover_products(SAMPLE_CATEGORY, use_cache=True)
    logger.info(f"Market discovery completed, found {len(products)} products")
    
    # For demo purposes, let's just use one product to keep things simpler
    sample_product = next((p for p in products if "Notion" in p.get("name", "")), products[0])
    logger.info(f"Analyzing product: {sample_product.get('name', 'Unknown Product')}")
    sample_products = [sample_product]
    
    # Analyze products
    analyzed_products = await analyze_products(sample_products, use_cache=True)
    
    # Identify market gaps
    logger.info("Starting gap analysis process")
    gaps = await identify_gaps(analyzed_products, SAMPLE_CATEGORY, use_cache=True)
    logger.info("Completed gap analysis")
    
    # Create product blueprint
    product_name = f"Enhanced {sample_product.get('name', 'SaaS Product')}"
    product_description = f"An improved version of {sample_product.get('name', 'SaaS Product')} with additional features and capabilities"
    
    logger.info(f"Starting product blueprint generation")
    blueprint = await create_product_blueprint(
        product_name,
        product_description,
        gaps[:3],  # Use top 3 gaps
        analyzed_products,
        use_cache=True
    )
    logger.info(f"Product blueprint generated for: {product_name}")
    
    # Build and visualize knowledge graph
    logger.info("Building and visualizing knowledge graph")
    kg_result = await build_knowledge_graph(analyzed_products, gaps)
    
    # Complete workflow
    logger.info("SaaS Cloner workflow completed")
    
    return {
        "discovered_products": len(products),
        "analyzed_products": len(analyzed_products),
        "identified_gaps": len(gaps),
        "product_blueprint": product_name,
        "knowledge_graph_stats": kg_result
    }

def main():
    """Main entry point for the SaaS Cloner workflow"""
    try:
        result = asyncio.run(run_workflow())
        print("\n=== Workflow Results ===")
        print(f"Discovered Products: {result['discovered_products']}")
        print(f"Analyzed Products: {result['analyzed_products']}")
        print(f"Identified Gaps: {result['identified_gaps']}")
        print(f"Product Blueprint: {result['product_blueprint']}")
        print(f"Knowledge Graph: {result['knowledge_graph_stats'].get('num_products', 0)} products, {result['knowledge_graph_stats'].get('num_features', 0)} features")
        print("\nCheck the 'data' directory for detailed outputs and 'output' directory for visualizations")
    except Exception as e:
        logger.error(f"Error running workflow: {e}", exc_info=True)

if __name__ == "__main__":
    main()