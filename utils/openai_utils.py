"""
Utility functions for working with the OpenAI API.
"""
import json
import os
import logging
import base64
from typing import Dict, Any, List

from openai import OpenAI
from config import OPENAI_MODEL

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def check_api_key() -> bool:
    """Check if the OpenAI API key is available and valid"""
    return bool(OPENAI_API_KEY)

def generate_completion(prompt: str, system_message: str = None) -> str:
    """
    Generate a text completion using the OpenAI API.
    
    Args:
        prompt (str): The user prompt to send to the API
        system_message (str, optional): Optional system message
    
    Returns:
        str: The generated text
    """
    try:
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        response = openai.chat.completions.create(
            model=OPENAI_MODEL,  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error generating completion: {e}")
        return f"Error: {str(e)}"

def generate_json_completion(prompt: str, system_message: str = None) -> Dict[str, Any]:
    """
    Generate a JSON-formatted completion using the OpenAI API.
    
    Args:
        prompt (str): The user prompt to send to the API
        system_message (str, optional): Optional system message
    
    Returns:
        Dict[str, Any]: The generated JSON object
    """
    try:
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        response = openai.chat.completions.create(
            model=OPENAI_MODEL,  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=messages,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        logging.error(f"Error generating JSON completion: {e}")
        return {"error": str(e)}

def analyze_text_with_structure(
    text: str, 
    task_description: str, 
    output_structure: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analyze text and extract structured information according to the specified output structure.
    
    Args:
        text (str): The text to analyze
        task_description (str): Description of what analysis to perform
        output_structure (Dict[str, Any]): Example structure of the expected output
    
    Returns:
        Dict[str, Any]: Structured information extracted from the text
    """
    system_message = (
        f"You are an expert text analyzer. {task_description}\n\n"
        f"Please output your analysis as a JSON object with the following structure:\n"
        f"{json.dumps(output_structure, indent=2)}"
    )
    
    return generate_json_completion(text, system_message)

def compare_products(
    original_product: Dict[str, Any], 
    enhanced_product: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compare original and enhanced product specs to highlight improvements.
    
    Args:
        original_product (Dict[str, Any]): The original product specification
        enhanced_product (Dict[str, Any]): The enhanced product specification
    
    Returns:
        Dict[str, Any]: Analysis of improvements and differentiators
    """
    system_message = (
        "You are a product analysis expert specializing in SaaS applications. "
        "Please analyze the original product and the enhanced version, highlighting "
        "the improvements, differentiators, and potential market advantages."
    )
    
    prompt = (
        "Original Product:\n"
        f"{json.dumps(original_product, indent=2)}\n\n"
        "Enhanced Product:\n"
        f"{json.dumps(enhanced_product, indent=2)}\n\n"
        "Please provide a detailed analysis of the improvements and differentiators "
        "in JSON format with the following structure:\n"
        "{\n"
        "  'key_improvements': [...],\n"
        "  'usability_enhancements': [...],\n"
        "  'technical_advantages': [...],\n"
        "  'market_differentiators': [...],\n"
        "  'potential_challenges': [...],\n"
        "  'overall_assessment': '...'\n"
        "}"
    )
    
    return generate_json_completion(prompt, system_message)
