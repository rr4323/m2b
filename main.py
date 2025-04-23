#!/usr/bin/env python3
"""
Main entry point for the Multi-Agent SaaS Cloner & Enhancer system.
This coordinates the workflow for discovering, analyzing, and enhancing SaaS applications.
"""
import asyncio
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.app import app as api_app
from workflows.saas_cloner_graph import SaasCloneGraph
from utils.openai_utils import check_api_key
from config import setup_logging

def setup_app():
    """Setup the API application with middleware"""
    api_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return api_app

async def run_test_workflow():
    """Run a test workflow"""
    # Initialize the workflow
    saas_graph = SaasCloneGraph()
    
    # Run a test workflow with a simple category
    logging.info("Initializing test workflow")
    try:
        result = await saas_graph.run("productivity")
        logging.info(f"Workflow test completed successfully")
        return result
    except Exception as e:
        logging.error(f"Error running test workflow: {e}", exc_info=True)
        return {"error": str(e)}

def main():
    """Main entry point for the SaaS Cloner workflow"""
    setup_logging()
    logging.info("Starting SaaS Cloner system")
    
    # Check if OpenAI API key is available
    if not check_api_key():
        logging.error("OpenAI API key not found! Set the OPENAI_API_KEY environment variable.")
        return
    
    # Run test workflow in a separate event loop
    asyncio.run(run_test_workflow())
    
    # Start the API server (this should be in the main thread)
    logging.info("Starting API server")
    import uvicorn
    app = setup_app()
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()
