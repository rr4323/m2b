"""
Web scraping utilities for the SaaS Cloner system.
"""
import logging
import re
import requests
from typing import Dict, List, Any, Optional, Tuple
from bs4 import BeautifulSoup
import trafilatura
from urllib.parse import urlparse

def get_website_text_content(url: str) -> str:
    """
    Extract the main text content from a website.
    
    Args:
        url (str): The URL to scrape
        
    Returns:
        str: The extracted text content
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        text = trafilatura.extract(downloaded)
        if text:
            return text
        else:
            return "No text content could be extracted from the URL."
    except Exception as e:
        logging.error(f"Error extracting content from {url}: {e}")
        return f"Error extracting content: {str(e)}"

def scrape_product_hunt(category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Scrape trending products from Product Hunt.
    
    Args:
        category (str, optional): Product category to filter by
        limit (int): Maximum number of products to return
        
    Returns:
        List[Dict[str, Any]]: List of product data dictionaries
    """
    url = "https://www.producthunt.com/"
    if category:
        url += f"topics/{category}"
        
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        products = []
        
        # Extract product information (this is a simplified version)
        # Product Hunt's structure may change, so this might need updates
        product_elements = soup.select('.styles_item__Dk_Sm')[:limit]
        
        for element in product_elements:
            try:
                name_element = element.select_one('.styles_title__jWi91')
                desc_element = element.select_one('.styles_tagline__tSQhI')
                
                product = {
                    "name": name_element.text.strip() if name_element else "Unknown",
                    "description": desc_element.text.strip() if desc_element else "",
                    "url": "https://www.producthunt.com" + element.select_one('a')['href'] if element.select_one('a') else "",
                    "source": "Product Hunt"
                }
                products.append(product)
            except Exception as e:
                logging.warning(f"Error extracting product data: {e}")
                
        return products
    except Exception as e:
        logging.error(f"Error scraping Product Hunt: {e}")
        return []

def scrape_g2_reviews(product_slug: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Scrape G2 reviews for a specific product.
    
    Args:
        product_slug (str): The G2 product slug (e.g., 'slack', 'asana')
        limit (int): Maximum number of reviews to return
        
    Returns:
        List[Dict[str, Any]]: List of review data dictionaries
    """
    url = f"https://www.g2.com/products/{product_slug}/reviews"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        reviews = []
        
        # Extract review information
        review_elements = soup.select('.review')[:limit]
        
        for element in review_elements:
            try:
                title_element = element.select_one('.review__title')
                content_element = element.select_one('.review__content')
                rating_element = element.select_one('.stars')
                
                # Extract rating (e.g., "4.5 out of 5")
                rating_text = rating_element.get('aria-label', '') if rating_element else ""
                rating_match = re.search(r'(\d+(\.\d+)?)', rating_text)
                rating = float(rating_match.group(1)) if rating_match else None
                
                review = {
                    "title": title_element.text.strip() if title_element else "Untitled Review",
                    "content": content_element.text.strip() if content_element else "",
                    "rating": rating,
                    "url": url,
                    "source": "G2"
                }
                reviews.append(review)
            except Exception as e:
                logging.warning(f"Error extracting review data: {e}")
                
        return reviews
    except Exception as e:
        logging.error(f"Error scraping G2 reviews: {e}")
        return []

def extract_domain(url: str) -> str:
    """Extract the domain name from a URL"""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    
    # Remove 'www.' if present
    if domain.startswith('www.'):
        domain = domain[4:]
        
    return domain

def find_reddit_discussions(product_name: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Find Reddit discussions about a specific product.
    
    Args:
        product_name (str): The name of the product to search for
        limit (int): Maximum number of discussions to return
        
    Returns:
        List[Dict[str, Any]]: List of discussion data dictionaries
    """
    search_url = f"https://www.google.com/search?q=site:reddit.com+{product_name}+review+OR+alternative+OR+problem"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        discussions = []
        
        # Extract Reddit links from Google search results
        for result in soup.select('a'):
            href = result.get('href', '')
            if 'reddit.com' in href and '/search?' not in href:
                # Extract actual URL from Google redirect URL
                match = re.search(r'(?:url\?q=)(.*?)(?:&sa=)', href)
                if match:
                    url = match.group(1)
                    if '/comments/' in url and len(discussions) < limit:
                        discussions.append({
                            "url": url,
                            "source": "Reddit",
                            "product": product_name
                        })
        
        return discussions
    except Exception as e:
        logging.error(f"Error finding Reddit discussions: {e}")
        return []
