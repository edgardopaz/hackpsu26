import requests

from core.config import get_settings


def extract_text_from_link(link: str) -> str:
    """
    Extract text content from a social media link using Tavily API.
    
    Uses the Tavily API to fetch rich text content from the provided social media URL.
    
    Args:
        link: URL to social media post
        
    Returns:
        Extracted text content from the post
        
    Raises:
        Exception: If the API request fails or returns an error
    """
    settings = get_settings()
    
    if not settings.tavily_api_key:
        raise Exception("TAVILY_API_KEY environment variable is not set")
    
    # Tavily API endpoint for extracting content from URLs
    url = "https://api.tavily.com/extract"
    
    payload = {
        "api_key": settings.tavily_api_key,
        "urls": [link],
        "include_raw_content": True,
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract the raw content from the response
        if data.get("results") and len(data["results"]) > 0:
            result = data["results"][0]
            
            # Try to get raw_content first (full page content), fallback to cleaned_content
            extracted_text = result.get("raw_content") or result.get("cleaned_content")
            
            if not extracted_text:
                raise Exception("No content could be extracted from the provided URL")
            
            return extracted_text
        else:
            raise Exception("No results returned from Tavily API")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch content from link: {str(e)}")
