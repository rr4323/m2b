"""
Configuration module for the SaaS Cloner system.
"""
import os
import logging
from typing import Dict, Any

# Application settings
APP_NAME = "SaaS Cloner & Enhancer"
APP_VERSION = "0.1.0"

# API endpoints for market discovery
PRODUCT_HUNT_API = "https://api.producthunt.com/v1/"
G2_REVIEW_URL = "https://www.g2.com/products/"
APPSUMO_URL = "https://appsumo.com/"
YC_DEMO_URL = "https://www.ycombinator.com/companies"

# OpenAI configuration
OPENAI_MODEL = "gpt-4o"  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Default parameters for agents
DEFAULT_AGENT_PARAMS: Dict[str, Any] = {
    "max_retries": 3,
    "timeout": 60,
    "concurrency": 5
}

# Directories for generated outputs
OUTPUT_DIR = "output"
SPECS_DIR = os.path.join(OUTPUT_DIR, "specs")
DESIGN_DIR = os.path.join(OUTPUT_DIR, "design")
CODE_DIR = os.path.join(OUTPUT_DIR, "code")
REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")

# Ensure directories exist
for directory in [OUTPUT_DIR, SPECS_DIR, DESIGN_DIR, CODE_DIR, REPORTS_DIR]:
    os.makedirs(directory, exist_ok=True)

def setup_logging():
    """Configure application logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(OUTPUT_DIR, "saas_cloner.log")),
            logging.StreamHandler()
        ]
    )
