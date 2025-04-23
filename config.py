"""
Configuration module for the SaaS Cloner system.
"""
import logging
import os
from typing import Dict, Any

# OpenAI API configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
DEFAULT_MODEL = "gpt-4o"  # The newest OpenAI model is "gpt-4o" which was released May 13, 2024
MAX_TOKENS = 1000

# Database configuration 
DATABASE_URL = os.environ.get("DATABASE_URL")

# Web scraping configuration
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
REQUEST_TIMEOUT = 10  # seconds
MAX_RETRIES = 3

# Knowledge graph configuration
KNOWLEDGE_GRAPH_VISUALIZATION_PATH = "output/knowledge_graph.html"

# Agent configuration
AGENT_CONFIG = {
    "market_discovery": {
        "sources": ["product_hunt", "g2", "capterra", "reddit"],
        "max_products": 10
    },
    "gap_analysis": {
        "min_gap_confidence": 0.7,
        "max_gaps": 15
    },
    "product_blueprint": {
        "detail_level": "high"
    }
}

def setup_logging():
    """Configure application logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("logs/saas_cloner.log", mode="a")
        ]
    )
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)