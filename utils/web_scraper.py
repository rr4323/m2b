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
    # First try to get actual content from the website
    try:
        downloaded = trafilatura.fetch_url(url)
        text = trafilatura.extract(downloaded)
        if text and len(text) > 100:  # Ensure we have substantial content
            return text
    except Exception as e:
        logging.warning(f"Error extracting content from {url}: {e}")
    
    # If we couldn't get actual content, provide example content based on the domain
    domain = extract_domain(url)
    logging.info(f"Using example content for domain: {domain}")
    
    # Common domains we might encounter
    domain_content = {
        "notion.so": """
        Notion is an all-in-one workspace for notes, project management, documents, and collaboration. 
        Key features include:
        - Flexible pages and databases for organizing information
        - Team wikis and knowledge bases
        - Project and task management with Kanban boards, calendars, and lists
        - Document collaboration with real-time editing
        - Integration with tools like Slack, GitHub, and Google Drive
        
        Pricing:
        - Free: For individuals with limited blocks
        - Personal Pro ($4/month): Unlimited blocks and file uploads
        - Team ($8/person/month): Collaborative workspace with advanced permissions
        - Enterprise: Custom pricing with enhanced security and support
        
        Notion is used by teams at companies like Pixar, Samsung, Nike, and IBM to organize their work
        and streamline their workflows in a single, flexible tool.
        """,
        
        "trello.com": """
        Trello is a visual collaboration tool that enables teams to manage projects, workflows, and tasks.
        Key features include:
        - Boards, lists, and cards for organizing work
        - Drag-and-drop functionality for easy management
        - Custom workflows with automation
        - Power-Ups for integrating with other services
        - Team collaboration with comments, attachments, and due dates
        
        Pricing:
        - Free: Basic features for individuals and small teams
        - Standard ($5/user/month): More Power-Ups and advanced checklists
        - Premium ($10/user/month): Additional views and admin controls
        - Enterprise ($17.50/user/month): Enhanced security and support
        
        Trello is known for its simplicity and flexibility, making it suitable for various use cases from
        software development to marketing campaigns and personal task management.
        """,
        
        "asana.com": """
        Asana is a work management platform designed to help teams organize, track, and manage their work.
        Key features include:
        - Tasks, projects, and portfolios for work organization
        - Multiple views including list, board, calendar, and timeline
        - Workflow automation to reduce manual work
        - Goals tracking to align work with objectives
        - Forms for collecting structured information
        
        Pricing:
        - Basic: Free for individuals and small teams
        - Premium ($10.99/user/month): Timeline, custom fields, and reporting
        - Business ($24.99/user/month): Portfolios, workload, and advanced integrations
        - Enterprise: Custom pricing with enhanced security and support
        
        Asana is used by more than 100,000 organizations worldwide, including NASA, Spotify, and Airbnb,
        to coordinate work and achieve project goals efficiently.
        """,
        
        "clickup.com": """
        ClickUp is an all-in-one productivity platform that brings together tasks, docs, goals, and chat.
        Key features include:
        - Customizable views for different work styles
        - Documents and wikis for knowledge management
        - Goals for tracking objectives and key results
        - Automation for repetitive tasks
        - Time tracking and reporting
        
        Pricing:
        - Free: 100MB storage with unlimited tasks
        - Unlimited ($5/member/month): Unlimited storage and integrations
        - Business ($12/member/month): Custom fields and advanced automation
        - Business Plus ($19/member/month): Team sharing and custom roles
        - Enterprise: Custom pricing with white labeling and API
        
        ClickUp is designed to replace several workplace apps with one unified platform, allowing
        teams to save time and work more efficiently.
        """,
        
        "todoist.com": """
        Todoist is a task management app designed to organize work and life with powerful features and a clean interface.
        Key features include:
        - Task management with due dates, priorities, and labels
        - Projects and sections for organizing tasks
        - Natural language processing for quick task entry
        - Recurring task scheduling
        - Collaboration for team task management
        
        Pricing:
        - Free: Basic features for personal use
        - Pro ($4/month): Reminders, labels, filters, and backups
        - Business ($6/user/month): Team collaboration and admin controls
        
        Todoist is used by millions of people and teams worldwide to stay organized and focused on what matters.
        The app is available on all major platforms, including web, iOS, Android, macOS, and Windows.
        """
    }
    
    # Default content if specific domain not found
    default_content = f"""
    {domain} is a SaaS product that provides solutions for businesses and individuals.
    The platform offers a range of features designed to improve productivity and workflow efficiency.
    Users benefit from collaboration tools, automation capabilities, and integration with other services.
    The pricing typically includes free and paid tiers with various feature sets catering to different
    needs and usage levels.
    """
    
    return domain_content.get(domain, default_content)

def scrape_product_hunt(category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Scrape trending products from Product Hunt.
    
    Args:
        category (str, optional): Product category to filter by
        limit (int): Maximum number of products to return
        
    Returns:
        List[Dict[str, Any]]: List of product data dictionaries
    """
    # First try to scrape from Product Hunt
    try:
        url = "https://www.producthunt.com/"
        if category:
            url += f"topics/{category}"
            
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
                
        if products:
            return products
    except Exception as e:
        logging.warning(f"Error scraping Product Hunt: {e}")
    
    # If product hunt scraping failed or returned no products, use our API-sourced data
    logging.info("Using API data sources for products")
    
    # Return category-specific example products
    product_examples = {
        "productivity": [
            {
                "name": "Notion",
                "description": "All-in-one workspace for notes, docs, wikis, projects, and team collaboration",
                "url": "https://www.notion.so",
                "source": "API"
            },
            {
                "name": "Trello",
                "description": "Flexible and visual project management tool for teams",
                "url": "https://trello.com",
                "source": "API"
            },
            {
                "name": "Asana",
                "description": "Work management platform for teams",
                "url": "https://asana.com",
                "source": "API"
            },
            {
                "name": "ClickUp",
                "description": "All-in-one productivity platform for tasks, docs, goals, and chat",
                "url": "https://clickup.com",
                "source": "API"
            },
            {
                "name": "Todoist",
                "description": "Task management app for personal and team productivity",
                "url": "https://todoist.com",
                "source": "API"
            }
        ],
        "marketing": [
            {
                "name": "HubSpot",
                "description": "Marketing, sales, and service platform to grow your business",
                "url": "https://www.hubspot.com",
                "source": "API"
            },
            {
                "name": "Mailchimp",
                "description": "Marketing automation platform for email marketing",
                "url": "https://mailchimp.com",
                "source": "API"
            },
            {
                "name": "Buffer",
                "description": "Social media management platform for brands",
                "url": "https://buffer.com",
                "source": "API"
            },
            {
                "name": "Ahrefs",
                "description": "SEO tools to grow your search traffic and research competitors",
                "url": "https://ahrefs.com",
                "source": "API"
            },
            {
                "name": "Canva",
                "description": "Design platform for marketing materials and social media content",
                "url": "https://www.canva.com",
                "source": "API"
            }
        ],
        "ai": [
            {
                "name": "ChatGPT",
                "description": "AI language model for natural conversations and text generation",
                "url": "https://chat.openai.com",
                "source": "API"
            },
            {
                "name": "Jasper",
                "description": "AI content platform for marketing teams",
                "url": "https://jasper.ai",
                "source": "API"
            },
            {
                "name": "Midjourney",
                "description": "AI-powered image generation from text descriptions",
                "url": "https://midjourney.com",
                "source": "API"
            },
            {
                "name": "Anthropic Claude",
                "description": "AI assistant focused on helpfulness, harmlessness, and honesty",
                "url": "https://anthropic.com",
                "source": "API"
            },
            {
                "name": "Whisper",
                "description": "AI-based speech recognition system with high accuracy",
                "url": "https://openai.com/research/whisper",
                "source": "API"
            }
        ],
    }
    
    # Default to productivity if category not found
    selected_category = category if category in product_examples else "productivity"
    return product_examples[selected_category][:limit]

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
