"""
OpenAI utilities for the SaaS Cloner system.
"""
import json
import logging
import os
from typing import Dict, Any, List, Optional, Union

import openai

# Setup the OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def generate_completion(prompt: str, system_message: Optional[str] = None, 
                         model: str = "gpt-4o", max_tokens: int = 1000) -> str:
    """
    Generate a text completion using OpenAI.
    
    Args:
        prompt: The prompt for the completion
        system_message: Optional system message to set the context
        model: The model to use for the completion
        max_tokens: The maximum number of tokens to generate
        
    Returns:
        str: The generated text
    """
    # This is just an alias for generate_text_completion
    return generate_text_completion(prompt, system_message, model, max_tokens)

def generate_text_completion(prompt: str, system_message: Optional[str] = None, 
                             model: str = "gpt-4o", max_tokens: int = 1000) -> str:
    """
    Generate a text completion using OpenAI.
    
    Args:
        prompt: The prompt for the completion
        system_message: Optional system message to set the context
        model: The model to use for the completion
        max_tokens: The maximum number of tokens to generate
        
    Returns:
        str: The generated text
    """
    if not client:
        logging.warning("OpenAI client not initialized. Using fallback.")
        return f"[FALLBACK] Response for: {prompt[:50]}..."
    
    try:
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
            
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logging.error(f"Error generating text completion: {e}")
        return f"[ERROR] Failed to generate completion: {str(e)}"

def generate_json_completion(prompt: str, system_message: Optional[str] = None, 
                            model: str = "gpt-4o", max_tokens: int = 1000) -> Dict[str, Any]:
    """
    Generate a JSON completion using OpenAI.
    
    Args:
        prompt: The prompt for the completion
        system_message: Optional system message to set the context
        model: The model to use for the completion
        max_tokens: The maximum number of tokens to generate
        
    Returns:
        Dict[str, Any]: The generated JSON
    """
    if not client:
        logging.warning("OpenAI client not initialized. Using fallback.")
        return {"error": "OpenAI client not initialized", "fallback": True}
    
    try:
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
            
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        
        # Parse the JSON response
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON response: {e}")
            return {"error": f"Failed to parse JSON response: {str(e)}", "raw_content": content}
        
    except Exception as e:
        logging.error(f"Error generating JSON completion: {e}")
        return {"error": f"Failed to generate JSON completion: {str(e)}"}

def analyze_text_with_openai(text: str, analysis_prompt: str, 
                            model: str = "gpt-4o") -> Dict[str, Any]:
    """
    Analyze text using OpenAI.
    
    Args:
        text: The text to analyze
        analysis_prompt: The prompt for the analysis
        model: The model to use for the analysis
        
    Returns:
        Dict[str, Any]: The analysis result
    """
    if not client:
        logging.warning("OpenAI client not initialized. Using fallback.")
        return {"error": "OpenAI client not initialized", "fallback": True}
    
    try:
        # Combine the analysis prompt with the text
        full_prompt = f"{analysis_prompt}\n\nText to analyze:\n{text}"
        
        # Generate the analysis
        result = generate_json_completion(
            prompt=full_prompt,
            system_message="You are an expert text analyst. Analyze the following text and provide a structured response.",
            model=model
        )
        
        return result
        
    except Exception as e:
        logging.error(f"Error analyzing text: {e}")
        return {"error": f"Failed to analyze text: {str(e)}"}

def analyze_text_with_structure(text: str, analysis_prompt: str, 
                                 structure: Dict[str, Any] = None, 
                                 model: str = "gpt-4o") -> Dict[str, Any]:
    """
    Analyze text with a specific output structure.
    
    Args:
        text: The text to analyze
        analysis_prompt: The prompt for the analysis
        structure: The expected structure of the output
        model: The model to use for the analysis
        
    Returns:
        Dict[str, Any]: The structured analysis result
    """
    if not client:
        logging.warning("OpenAI client not initialized. Using fallback.")
        return {"error": "OpenAI client not initialized", "fallback": True}
    
    try:
        # Create structure description if provided
        structure_desc = ""
        if structure:
            structure_desc = "Return your analysis as a JSON object with the following structure:\n"
            structure_desc += json.dumps(structure, indent=2)
        
        # Combine the analysis prompt with the text and structure
        full_prompt = f"{analysis_prompt}\n\nText to analyze:\n{text}\n\n{structure_desc}"
        
        # Generate the analysis
        result = generate_json_completion(
            prompt=full_prompt,
            system_message="You are an expert text analyst. Analyze the following text and provide a structured response.",
            model=model
        )
        
        return result
        
    except Exception as e:
        logging.error(f"Error analyzing text with structure: {e}")
        return {"error": f"Failed to analyze text with structure: {str(e)}"}

def compare_products_with_openai(product1: Dict[str, Any], product2: Dict[str, Any],
                                model: str = "gpt-4o") -> Dict[str, Any]:
    """
    Compare two products using OpenAI.
    
    Args:
        product1: The first product data
        product2: The second product data
        model: The model to use for the comparison
        
    Returns:
        Dict[str, Any]: The comparison result
    """
    if not client:
        logging.warning("OpenAI client not initialized. Using fallback.")
        return {"error": "OpenAI client not initialized", "fallback": True}
    
    try:
        # Create a structured prompt for the comparison
        prompt = f"""
        Compare the following two SaaS products:
        
        Product 1: {product1.get('name', 'Unknown')}
        Description: {product1.get('description', 'N/A')}
        Features: {', '.join(product1.get('feature_list', []))}
        
        Product 2: {product2.get('name', 'Unknown')}
        Description: {product2.get('description', 'N/A')}
        Features: {', '.join(product2.get('feature_list', []))}
        
        Provide a detailed comparison including:
        1. Feature differences
        2. Strengths of each product
        3. Weaknesses of each product
        4. Potential enhancement opportunities
        
        Return your analysis in a structured JSON format.
        """
        
        # Generate the comparison
        result = generate_json_completion(
            prompt=prompt,
            system_message="You are an expert product analyst specializing in SaaS products.",
            model=model
        )
        
        return result
        
    except Exception as e:
        logging.error(f"Error comparing products: {e}")
        return {"error": f"Failed to compare products: {str(e)}"}