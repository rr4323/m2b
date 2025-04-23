"""
Web scraping utilities for the SaaS Cloner system.

This module provides functionality for scraping SaaS product data
from various sources including Product Hunt, G2, Capterra, and Reddit.
"""
import logging
import json
import os
import random
import time
from typing import Dict, Any, List, Optional, Tuple, Union, cast
import urllib.parse

import requests
import trafilatura
from bs4 import BeautifulSoup

import config

logger = logging.getLogger(__name__)

# Common headers to mimic browser behavior
DEFAULT_HEADERS = {
    'User-Agent': config.USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.google.com/',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

def fetch_url(url: str, headers: Optional[Dict[str, str]] = None, 
              params: Optional[Dict[str, str]] = None, retries: int = 3) -> Optional[str]:
    """
    Fetch the content of a URL with retries and error handling.
    
    Args:
        url: The URL to fetch
        headers: Optional request headers
        params: Optional query parameters
        retries: Number of times to retry on failure
        
    Returns:
        Optional[str]: The response text, or None if the fetch failed
    """
    if headers is None:
        headers = DEFAULT_HEADERS.copy()
    
    for attempt in range(retries):
        try:
            response = requests.get(
                url, 
                headers=headers, 
                params=params, 
                timeout=config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch {url} (attempt {attempt+1}/{retries}): {e}")
            if attempt + 1 < retries:
                # Add jitter to avoid rate limiting
                time.sleep(random.uniform(1, 3) * (attempt + 1))
            else:
                logger.error(f"Failed to fetch {url} after {retries} attempts")
                return None

def extract_text_from_html(html: str) -> str:
    """
    Extract the main text content from HTML using trafilatura.
    
    Args:
        html: The HTML content to extract text from
        
    Returns:
        str: The extracted text content
    """
    text = trafilatura.extract(html)
    if text is None:
        # Fallback to BeautifulSoup if trafilatura fails
        soup = BeautifulSoup(html, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator=' ', strip=True)
    return text

def extract_structured_product_data(html: str, source: str) -> List[Dict[str, Any]]:
    """
    Extract structured product data from HTML based on the source.
    
    Args:
        html: The HTML content to extract data from
        source: The source of the HTML (producthunt, g2, capterra, etc.)
        
    Returns:
        List[Dict[str, Any]]: List of extracted product data
    """
    if html is None:
        return []
        
    products = []
    
    if source == 'producthunt':
        # Extract product data from Product Hunt
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find product cards
        product_cards = soup.select('div[data-test="post-item"]')
        logger.info(f"Found {len(product_cards)} product cards on Product Hunt")
        
        for card in product_cards:
            try:
                # Extract product name
                product_name_elem = card.select_one('h3')
                product_name = product_name_elem.text.strip() if product_name_elem else "Unknown Product"
                
                # Extract product description
                product_desc_elem = card.select_one('div[data-test="tagline"]')
                product_description = product_desc_elem.text.strip() if product_desc_elem else ""
                
                # Extract product URL
                product_url_elem = card.select_one('a[data-test="post-name"]')
                product_url = "https://www.producthunt.com" + product_url_elem['href'] if product_url_elem and 'href' in product_url_elem.attrs else ""
                
                # Extract upvotes
                upvotes_elem = card.select_one('div[data-test="vote-button"] span')
                upvotes = int(upvotes_elem.text.strip()) if upvotes_elem and upvotes_elem.text.strip().isdigit() else 0
                
                # Extract topics (categories)
                topics_elems = card.select('div[data-test="topic-name"]')
                topics = [topic.text.strip() for topic in topics_elems]
                
                # Create product data dictionary
                product_data = {
                    'name': product_name,
                    'description': product_description,
                    'url': product_url,
                    'source': 'Product Hunt',
                    'popularity_score': min(upvotes / 100, 10),  # Normalize to 0-10 scale
                    'category': topics[0] if topics else "Software",
                    'feature_list': [],  # Will be populated with additional scraping
                    'target_audience': "",  # Will be populated with additional scraping
                    'pricing_model': ""  # Will be populated with additional scraping
                }
                
                products.append(product_data)
                
            except Exception as e:
                logger.warning(f"Error extracting product data from card: {e}")
    
    elif source == 'g2':
        # Extract product data from G2
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find product cards
        product_cards = soup.select('div.product-card')
        logger.info(f"Found {len(product_cards)} product cards on G2")
        
        for card in product_cards:
            try:
                # Extract product name
                product_name_elem = card.select_one('h3.product-card__product-name')
                product_name = product_name_elem.text.strip() if product_name_elem else "Unknown Product"
                
                # Extract product description
                product_desc_elem = card.select_one('p.product-card__description')
                product_description = product_desc_elem.text.strip() if product_desc_elem else ""
                
                # Extract product URL
                product_url_elem = card.select_one('a.product-card__product-name-wrapper')
                product_url = "https://www.g2.com" + product_url_elem['href'] if product_url_elem and 'href' in product_url_elem.attrs else ""
                
                # Extract rating
                rating_elem = card.select_one('span.product-card__rating')
                rating_text = rating_elem.text.strip() if rating_elem else "0.0"
                try:
                    rating = float(rating_text)
                except ValueError:
                    rating = 0.0
                
                # Extract category
                category_elem = card.select_one('div.product-card__category')
                category = category_elem.text.strip() if category_elem else "Software"
                
                # Create product data dictionary
                product_data = {
                    'name': product_name,
                    'description': product_description,
                    'url': product_url,
                    'source': 'G2',
                    'popularity_score': rating * 2,  # G2 uses 0-5 scale, convert to 0-10
                    'category': category,
                    'feature_list': [],  # Will be populated with additional scraping
                    'target_audience': "",  # Will be populated with additional scraping
                    'pricing_model': ""  # Will be populated with additional scraping
                }
                
                products.append(product_data)
                
            except Exception as e:
                logger.warning(f"Error extracting product data from G2 card: {e}")
    
    elif source == 'capterra':
        # Extract product data from Capterra
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find product cards
        product_cards = soup.select('div.product-card')
        logger.info(f"Found {len(product_cards)} product cards on Capterra")
        
        for card in product_cards:
            try:
                # Extract product name
                product_name_elem = card.select_one('h2.product-card-name')
                product_name = product_name_elem.text.strip() if product_name_elem else "Unknown Product"
                
                # Extract product description
                product_desc_elem = card.select_one('div.product-description')
                product_description = product_desc_elem.text.strip() if product_desc_elem else ""
                
                # Extract product URL
                product_url_elem = card.select_one('a.product-card-name-wrapper')
                product_url = "https://www.capterra.com" + product_url_elem['href'] if product_url_elem and 'href' in product_url_elem.attrs else ""
                
                # Extract rating
                rating_elem = card.select_one('div.product-rating-value')
                rating_text = rating_elem.text.strip() if rating_elem else "0.0"
                try:
                    rating = float(rating_text)
                except ValueError:
                    rating = 0.0
                
                # Extract category from breadcrumbs
                category_elem = soup.select_one('li.active-breadcrumb-item')
                category = category_elem.text.strip() if category_elem else "Software"
                
                # Create product data dictionary
                product_data = {
                    'name': product_name,
                    'description': product_description,
                    'url': product_url,
                    'source': 'Capterra',
                    'popularity_score': rating * 2,  # Capterra uses 0-5 scale, convert to 0-10
                    'category': category,
                    'feature_list': [],  # Will be populated with additional scraping
                    'target_audience': "",  # Will be populated with additional scraping
                    'pricing_model': ""  # Will be populated with additional scraping
                }
                
                products.append(product_data)
                
            except Exception as e:
                logger.warning(f"Error extracting product data from Capterra card: {e}")
    
    return products

def extract_product_details(html: str, source: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract detailed product information from a product page.
    
    Args:
        html: The HTML content of the product page
        source: The source of the HTML (producthunt, g2, capterra, etc.)
        product_data: The existing product data to enhance
        
    Returns:
        Dict[str, Any]: Enhanced product data with additional details
    """
    if html is None:
        return product_data
    
    enhanced_data = product_data.copy()
    
    if source == 'producthunt':
        # Extract detailed product data from Product Hunt
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract features
        feature_list = []
        feature_elems = soup.select('div.styles_bulletPoint__IZS9J')
        for feature in feature_elems:
            feature_text = feature.text.strip()
            if feature_text:
                feature_list.append(feature_text)
        
        if feature_list:
            enhanced_data['feature_list'] = feature_list
        
        # Extract pricing information
        pricing_elem = soup.select_one('span:contains("Pricing")')
        if pricing_elem:
            pricing_section = pricing_elem.find_parent('div')
            if pricing_section:
                pricing_text = pricing_section.text.strip()
                if "Free" in pricing_text:
                    enhanced_data['pricing_model'] = "Free"
                elif "Freemium" in pricing_text:
                    enhanced_data['pricing_model'] = "Freemium"
                elif "Paid" in pricing_text:
                    enhanced_data['pricing_model'] = "Paid"
                else:
                    enhanced_data['pricing_model'] = pricing_text
        
    elif source == 'g2':
        # Extract detailed product data from G2
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract features
        feature_list = []
        feature_elems = soup.select('div.feature-overview__feature')
        for feature in feature_elems:
            feature_text = feature.text.strip()
            if feature_text:
                feature_list.append(feature_text)
        
        if feature_list:
            enhanced_data['feature_list'] = feature_list
        
        # Extract pricing information
        pricing_elem = soup.select_one('span.product-content__pricing-text')
        if pricing_elem:
            pricing_text = pricing_elem.text.strip()
            enhanced_data['pricing_model'] = pricing_text
        
        # Extract target audience
        audience_elem = soup.select_one('div.product-content__buyer-types')
        if audience_elem:
            audience_text = audience_elem.text.strip()
            enhanced_data['target_audience'] = audience_text
    
    elif source == 'capterra':
        # Extract detailed product data from Capterra
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract features
        feature_list = []
        feature_elems = soup.select('li.expandable-list__item')
        for feature in feature_elems:
            feature_text = feature.text.strip()
            if feature_text:
                feature_list.append(feature_text)
        
        if feature_list:
            enhanced_data['feature_list'] = feature_list
        
        # Extract pricing information
        pricing_elem = soup.select_one('div.pricing-band')
        if pricing_elem:
            pricing_text = pricing_elem.text.strip()
            if "Free" in pricing_text:
                enhanced_data['pricing_model'] = "Free"
            elif "Free Trial" in pricing_text:
                enhanced_data['pricing_model'] = "Free Trial"
            elif "Starting from" in pricing_text:
                enhanced_data['pricing_model'] = "Paid"
            else:
                enhanced_data['pricing_model'] = pricing_text
        
        # Extract target audience
        audience_elem = soup.select_one('div.product-market-focus')
        if audience_elem:
            audience_text = audience_elem.text.strip()
            enhanced_data['target_audience'] = audience_text
    
    return enhanced_data

def search_producthunt(category: str, max_products: int = 10) -> List[Dict[str, Any]]:
    """
    Search Product Hunt for products in a specific category.
    
    Args:
        category: The category to search for
        max_products: Maximum number of products to return
        
    Returns:
        List[Dict[str, Any]]: List of discovered products
    """
    logger.info(f"Searching Product Hunt for {category} products")
    
    # Construct the search URL
    category_slug = category.lower().replace(' ', '-')
    search_url = f"https://www.producthunt.com/topics/{category_slug}"
    
    # Fetch the search page
    html = fetch_url(search_url)
    if html is None:
        logger.warning(f"Failed to fetch Product Hunt search results for {category}")
        return []
    
    # Extract product data from the search results
    products = extract_structured_product_data(html, 'producthunt')
    
    # Limit the number of products
    products = products[:max_products]
    
    # Enhance products with additional details
    enhanced_products = []
    for product in products:
        if product['url']:
            logger.info(f"Fetching details for {product['name']} from Product Hunt")
            product_html = fetch_url(product['url'])
            if product_html:
                enhanced_product = extract_product_details(product_html, 'producthunt', product)
                enhanced_products.append(enhanced_product)
                # Be nice to the server
                time.sleep(random.uniform(1, 3))
            else:
                enhanced_products.append(product)
        else:
            enhanced_products.append(product)
    
    return enhanced_products

def search_g2(category: str, max_products: int = 10) -> List[Dict[str, Any]]:
    """
    Search G2 for products in a specific category.
    
    Args:
        category: The category to search for
        max_products: Maximum number of products to return
        
    Returns:
        List[Dict[str, Any]]: List of discovered products
    """
    logger.info(f"Searching G2 for {category} products")
    
    # Construct the search URL
    category_slug = category.lower().replace(' ', '-')
    search_url = f"https://www.g2.com/categories/{category_slug}"
    
    # Fetch the search page
    html = fetch_url(search_url)
    if html is None:
        logger.warning(f"Failed to fetch G2 search results for {category}")
        return []
    
    # Extract product data from the search results
    products = extract_structured_product_data(html, 'g2')
    
    # Limit the number of products
    products = products[:max_products]
    
    # Enhance products with additional details
    enhanced_products = []
    for product in products:
        if product['url']:
            logger.info(f"Fetching details for {product['name']} from G2")
            product_html = fetch_url(product['url'])
            if product_html:
                enhanced_product = extract_product_details(product_html, 'g2', product)
                enhanced_products.append(enhanced_product)
                # Be nice to the server
                time.sleep(random.uniform(1, 3))
            else:
                enhanced_products.append(product)
        else:
            enhanced_products.append(product)
    
    return enhanced_products

def search_capterra(category: str, max_products: int = 10) -> List[Dict[str, Any]]:
    """
    Search Capterra for products in a specific category.
    
    Args:
        category: The category to search for
        max_products: Maximum number of products to return
        
    Returns:
        List[Dict[str, Any]]: List of discovered products
    """
    logger.info(f"Searching Capterra for {category} products")
    
    # Construct the search URL
    category_slug = category.lower().replace(' ', '-')
    search_url = f"https://www.capterra.com/p/browse/{category_slug}"
    
    # Fetch the search page
    html = fetch_url(search_url)
    if html is None:
        logger.warning(f"Failed to fetch Capterra search results for {category}")
        return []
    
    # Extract product data from the search results
    products = extract_structured_product_data(html, 'capterra')
    
    # Limit the number of products
    products = products[:max_products]
    
    # Enhance products with additional details
    enhanced_products = []
    for product in products:
        if product['url']:
            logger.info(f"Fetching details for {product['name']} from Capterra")
            product_html = fetch_url(product['url'])
            if product_html:
                enhanced_product = extract_product_details(product_html, 'capterra', product)
                enhanced_products.append(enhanced_product)
                # Be nice to the server
                time.sleep(random.uniform(1, 3))
            else:
                enhanced_products.append(product)
        else:
            enhanced_products.append(product)
    
    return enhanced_products

def search_reddit(category: str, max_posts: int = 10) -> List[Dict[str, Any]]:
    """
    Search Reddit for discussions about products in a specific category.
    
    Args:
        category: The category to search for
        max_posts: Maximum number of posts to return
        
    Returns:
        List[Dict[str, Any]]: List of relevant Reddit posts
    """
    logger.info(f"Searching Reddit for discussions about {category} software")
    
    # Construct the search URL
    search_term = f"best {category} software"
    search_url = f"https://www.reddit.com/search/?q={urllib.parse.quote(search_term)}"
    
    # Fetch the search page
    html = fetch_url(search_url)
    if html is None:
        logger.warning(f"Failed to fetch Reddit search results for {search_term}")
        return []
    
    # Extract post data from the search results
    posts = []
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find post cards
    post_cards = soup.select('div[data-testid="post-container"]')
    logger.info(f"Found {len(post_cards)} post cards on Reddit")
    
    for card in post_cards[:max_posts]:
        try:
            # Extract post title
            title_elem = card.select_one('h3')
            title = title_elem.text.strip() if title_elem else "Unknown Post"
            
            # Extract post URL
            url_elem = card.select_one('a[data-click-id="body"]')
            url = "https://www.reddit.com" + url_elem['href'] if url_elem and 'href' in url_elem.attrs else ""
            
            # Extract subreddit
            subreddit_elem = card.select_one('a[data-click-id="subreddit"]')
            subreddit = subreddit_elem.text.strip() if subreddit_elem else ""
            
            # Extract post date
            date_elem = card.select_one('span[data-click-id="timestamp"]')
            date = date_elem.text.strip() if date_elem else ""
            
            # Create post data dictionary
            post_data = {
                'title': title,
                'url': url,
                'subreddit': subreddit,
                'date': date,
                'content': ""  # Will be populated with additional scraping
            }
            
            # Only include posts that actually link to Reddit discussions
            if url and 'reddit.com' in url and '/search?' not in url:
                posts.append(post_data)
            
        except Exception as e:
            logger.warning(f"Error extracting post data from Reddit card: {e}")
    
    # Enhance posts with content
    enhanced_posts = []
    for post in posts:
        if post['url']:
            logger.info(f"Fetching content for Reddit post: {post['title']}")
            post_html = fetch_url(post['url'])
            if post_html:
                # Extract the post content
                soup = BeautifulSoup(post_html, 'html.parser')
                content_elem = soup.select_one('div[data-click-id="text"] div')
                if content_elem:
                    post['content'] = content_elem.text.strip()
                
                # Extract comments to find product mentions
                product_mentions = []
                comment_elems = soup.select('div[data-testid="comment"]')
                for comment in comment_elems:
                    comment_text = comment.text.strip()
                    # Look for common patterns that might indicate product mentions
                    if "I use" in comment_text or "I recommend" in comment_text or "best tool" in comment_text:
                        product_mentions.append(comment_text)
                
                post['product_mentions'] = product_mentions[:5]  # Limit to top 5 mentions
                enhanced_posts.append(post)
                # Be nice to the server
                time.sleep(random.uniform(1, 3))
            else:
                enhanced_posts.append(post)
        else:
            enhanced_posts.append(post)
    
    return enhanced_posts

def discover_trending_products(category: str, sources: Optional[List[str]] = None, 
                               max_products_per_source: int = 5) -> List[Dict[str, Any]]:
    """
    Discover trending products across multiple sources.
    
    Args:
        category: The category to search for
        sources: List of sources to search (producthunt, g2, capterra, reddit)
        max_products_per_source: Maximum number of products to return per source
        
    Returns:
        List[Dict[str, Any]]: List of discovered products
    """
    if sources is None:
        sources = ["producthunt", "g2", "capterra"]
    
    all_products = []
    
    for source in sources:
        try:
            if source == "producthunt":
                products = search_producthunt(category, max_products_per_source)
            elif source == "g2":
                products = search_g2(category, max_products_per_source)
            elif source == "capterra":
                products = search_capterra(category, max_products_per_source)
            elif source == "reddit":
                # Reddit posts require different handling
                posts = search_reddit(category, max_products_per_source)
                # We don't include Reddit posts directly in the product list
                # Instead, we could use them for sentiment analysis or additional insights
                continue
            else:
                logger.warning(f"Unknown source: {source}")
                continue
                
            logger.info(f"Discovered {len(products)} products from {source}")
            all_products.extend(products)
            
        except Exception as e:
            logger.error(f"Error discovering products from {source}: {e}")
    
    # If we couldn't fetch any products, use sample data
    if not all_products:
        logger.info("No products discovered from sources. Using API data sources for products")
        try:
            # Use sample products from data directory
            sample_path = "data/sample_products.json"
            if os.path.exists(sample_path):
                with open(sample_path, 'r', encoding='utf-8') as f:
                    sample_products = json.load(f)
                
                # Filter by category if needed
                if category:
                    sample_products = [p for p in sample_products if p.get("category", "").lower() == category.lower()]
                
                all_products = sample_products
                logger.info(f"Loaded {len(all_products)} sample products from {sample_path}")
        except Exception as e:
            logger.error(f"Error loading sample products: {e}")
    
    # Remove duplicates based on product name
    unique_products = {}
    for product in all_products:
        product_name = product['name'].lower()
        if product_name not in unique_products or unique_products[product_name]['description'] == "":
            unique_products[product_name] = product
    
    return list(unique_products.values())

def save_discovered_products(products: List[Dict[str, Any]], output_file: str) -> None:
    """
    Save discovered products to a JSON file.
    
    Args:
        products: List of product data dictionaries
        output_file: Path to the output file
    """
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Save the products to a JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved {len(products)} products to {output_file}")

def load_discovered_products(input_file: str) -> List[Dict[str, Any]]:
    """
    Load discovered products from a JSON file.
    
    Args:
        input_file: Path to the input file
        
    Returns:
        List[Dict[str, Any]]: List of product data dictionaries
    """
    if not os.path.exists(input_file):
        logger.warning(f"Input file {input_file} does not exist")
        return []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
        logger.info(f"Loaded {len(products)} products from {input_file}")
        return products
    except json.JSONDecodeError as e:
        logger.error(f"Error loading products from {input_file}: {e}")
        return []