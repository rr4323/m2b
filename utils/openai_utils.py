"""
OpenAI utilities for the SaaS Cloner system.

This module provides functionality for generating text and analyzing data using OpenAI models.
"""
import logging
import json
import os
from typing import Dict, Any, List, Optional

import openai
from openai import OpenAI

import config

logger = logging.getLogger(__name__)

# Initialize the OpenAI client
# Check if the API key is available and not empty
if config.OPENAI_API_KEY:
    client = OpenAI(api_key=config.OPENAI_API_KEY)
else:
    client = None
    logger.warning("OpenAI API key not found. OpenAI functions will not work.")

def generate_completion(prompt: str, model: str = None, max_tokens: int = None) -> str:
    """
    Generate a text completion using OpenAI.
    
    Args:
        prompt: The prompt to generate a completion for
        model: Optional model to use (defaults to config.DEFAULT_MODEL)
        max_tokens: Optional maximum number of tokens to generate
        
    Returns:
        str: The generated completion
    """
    if not model:
        model = config.DEFAULT_MODEL
    
    if not max_tokens:
        max_tokens = config.MAX_TOKENS
    
    # Check if client is available
    if client is None:
        logger.error("OpenAI client is not initialized. Cannot generate completion.")
        return "Error: OpenAI API key not configured. Please set up your API key."
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating completion: {e}")
        return ""

def generate_json_completion(prompt: str, model: str = None, max_tokens: int = None) -> Dict[str, Any]:
    """
    Generate a JSON completion using OpenAI.
    
    Args:
        prompt: The prompt to generate a completion for
        model: Optional model to use (defaults to config.DEFAULT_MODEL)
        max_tokens: Optional maximum number of tokens to generate
        
    Returns:
        Dict[str, Any]: The generated JSON completion
    """
    if not model:
        model = config.DEFAULT_MODEL
    
    if not max_tokens:
        max_tokens = config.MAX_TOKENS
    
    # Check if client is available
    if client is None:
        logger.error("OpenAI client is not initialized. Cannot generate JSON completion.")
        return {"error": "OpenAI API key not configured. Please set up your API key."}
    
    try:
        # Add instructions to format as JSON
        json_prompt = f"{prompt}\n\nResponse must be in valid JSON format."
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": json_prompt}],
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        
        json_response = response.choices[0].message.content
        
        # Try to parse the JSON response
        try:
            return json.loads(json_response)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON response: {e}")
            return {"error": "Failed to decode JSON response", "raw_response": json_response}
    
    except Exception as e:
        logger.error(f"Error generating JSON completion: {e}")
        return {"error": str(e)}

def analyze_product_data(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze product data to extract key information and insights.
    
    Args:
        product_data: The product data to analyze
        
    Returns:
        Dict[str, Any]: Analysis results
    """
    # Create a prompt for analyzing the product
    product_name = product_data.get("name", "Unknown Product")
    product_description = product_data.get("description", "")
    product_features = product_data.get("feature_list", [])
    product_category = product_data.get("category", "")
    
    features_text = "\n".join([f"- {feature}" for feature in product_features])
    
    prompt = f"""
    Analyze the following SaaS product:
    
    Name: {product_name}
    Category: {product_category}
    Description: {product_description}
    
    Features:
    {features_text}
    
    Please provide the following analysis in JSON format:
    1. A summary of the product (1-2 sentences)
    2. The primary target audience
    3. The key value propositions (max 3)
    4. The main problems it solves (max 3)
    5. Technical complexity estimate (low, medium, high)
    6. Market saturation estimate (low, medium, high)
    7. Potential areas for improvement or gaps (max 3)
    """
    
    return generate_json_completion(prompt)

def identify_market_gaps(products: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
    """
    Identify market gaps based on analyzed products in a category.
    
    Args:
        products: List of analyzed product data
        category: The category to identify gaps for
        
    Returns:
        List[Dict[str, Any]]: List of identified market gaps
    """
    # Prepare a summary of the products for the prompt
    product_summaries = []
    for product in products:
        name = product.get("name", "Unknown Product")
        description = product.get("description", "")
        features = product.get("feature_list", [])
        features_text = ", ".join(features[:5])  # Limit to first 5 features for brevity
        
        summary = f"Name: {name}\nDescription: {description}\nKey Features: {features_text}\n"
        product_summaries.append(summary)
    
    products_text = "\n".join(product_summaries)
    
    prompt = f"""
    You are a market analyst specializing in SaaS products. I'll provide you with information about multiple products in the {category} category, and I'd like you to identify potential market gaps, unmet user needs, or opportunities for innovation.

    Products in the {category} category:
    {products_text}

    Based on these products, please identify:
    1. Feature gaps: Important features or capabilities missing across multiple products
    2. User segment gaps: Underserved user segments or use cases
    3. Experience gaps: Areas where the user experience could be significantly improved
    4. Integration gaps: Opportunities for better integration with other tools or platforms
    5. Pricing/business model gaps: Opportunities for innovative pricing or business models

    For each gap, provide:
    - A name for the gap
    - A description of the gap
    - The potential impact of addressing this gap (high, medium, low)
    - Which existing products could be enhanced by addressing this gap

    Format your response as a JSON array with objects for each identified gap.
    """
    
    response = generate_json_completion(prompt)
    
    # If the response is a dictionary with a 'gaps' key, return the gaps
    if isinstance(response, dict) and "gaps" in response:
        return response["gaps"]
    
    # If the response is already a list, return it
    if isinstance(response, list):
        return response
    
    # Otherwise, return an empty list
    return []

def generate_product_blueprint(product_name: str, product_description: str, 
                              target_gaps: List[Dict[str, Any]], 
                              inspiration_products: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a blueprint for a new product based on identified gaps and inspiration.
    
    Args:
        product_name: The name of the new product
        product_description: A brief description of the new product
        target_gaps: List of gaps the new product will address
        inspiration_products: List of products that serve as inspiration
        
    Returns:
        Dict[str, Any]: Product blueprint
    """
    # Prepare gaps text for the prompt
    gaps_text = []
    for gap in target_gaps:
        gap_name = gap.get("name", "Unknown Gap")
        gap_description = gap.get("description", "")
        gaps_text.append(f"Gap: {gap_name}\nDescription: {gap_description}")
    
    gaps_combined = "\n".join(gaps_text)
    
    # Prepare inspiration products text for the prompt
    inspiration_text = []
    for product in inspiration_products:
        name = product.get("name", "Unknown Product")
        description = product.get("description", "")
        features = product.get("feature_list", [])
        features_text = ", ".join(features[:5])  # Limit to first 5 features for brevity
        
        summary = f"Name: {name}\nDescription: {description}\nKey Features: {features_text}"
        inspiration_text.append(summary)
    
    inspiration_combined = "\n".join(inspiration_text)
    
    prompt = f"""
    You are a product development expert. I'll provide you with information about a new product concept, the market gaps it aims to address, and existing products for inspiration. Please create a detailed product blueprint.

    New Product Concept:
    Name: {product_name}
    Description: {product_description}

    Market Gaps to Address:
    {gaps_combined}

    Inspiration Products:
    {inspiration_combined}

    Please generate a comprehensive product blueprint in JSON format with the following sections:
    1. Product Overview: A refined description and positioning statement
    2. Value Proposition: The core value propositions of the product
    3. Target Audience: Primary and secondary user segments
    4. Core Features: Detailed descriptions of 5-10 core features
    5. User Experience: Description of the overall UX approach and key workflows
    6. Technical Architecture: High-level overview of the technical components
    7. Monetization Strategy: Pricing model and revenue streams
    8. Market Positioning: How the product will be positioned relative to competitors
    9. Roadmap: A phased approach to development and feature releases
    10. KPIs: Key performance indicators to measure success
    """
    
    return generate_json_completion(prompt)

def extract_key_features(text: str) -> List[str]:
    """
    Extract key features from product description text.
    
    Args:
        text: The product description text
        
    Returns:
        List[str]: List of extracted features
    """
    prompt = f"""
    Extract the key features from the following product description. 
    
    Product Description:
    {text}
    
    Format your response as a JSON array of strings, with each string being a distinct feature.
    Only include clear, specific features, not vague claims or marketing language.
    """
    
    response = generate_json_completion(prompt)
    
    # If the response is a dictionary with a 'features' key, return the features
    if isinstance(response, dict) and "features" in response:
        return response["features"]
    
    # If the response is already a list, return it
    if isinstance(response, list):
        return response
    
    # Otherwise, return an empty list
    return []

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze sentiment in text.
    
    Args:
        text: The text to analyze
        
    Returns:
        Dict[str, Any]: Sentiment analysis results
    """
    try:
        prompt = f"""
        Analyze the sentiment in the following text and provide a rating from 1 to 5 stars
        and a confidence score between 0 and 1.
        
        Text:
        {text}
        
        Format your response as a JSON object with the following structure:
        {{
            "rating": <number between 1 and 5>,
            "confidence": <number between 0 and 1>,
            "sentiment": <"positive", "neutral", or "negative">,
            "key_themes": [<list of key positive and negative themes mentioned>]
        }}
        """
        
        response = generate_json_completion(prompt)
        return response
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        return {"error": str(e)}