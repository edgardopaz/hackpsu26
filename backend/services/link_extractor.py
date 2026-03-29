import requests

from core.config import get_settings


class LinkExtractionError(RuntimeError):
    """Raised when text cannot be extracted from a provided URL."""


def extract_text_from_link(link: str) -> str:
    """
    Extract text content from a social media link using Tavily API.
    
    Uses the Tavily API to fetch rich text content from the provided social media URL.
    
    Args:
        link: URL to social media post
        
    Returns:
        Extracted text content from the post
        
    Raises:
        LinkExtractionError: If the API request fails or no content can be extracted
    """
    settings = get_settings()
    
    if not settings.tavily_api_key:
        raise LinkExtractionError(
            "TAVILY_API_KEY is not configured. Please contact support."
        )
    
    # Tavily API endpoint for extracting content from URLs
    url = "https://api.tavily.com/extract"
    
    payload = {
        "api_key": settings.tavily_api_key,
        "urls": [link],
        "include_raw_content": True,
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        # Check if results exist
        if not data.get("results") or len(data["results"]) == 0:
            raise LinkExtractionError(
                "Could not extract content from the provided link. "
                "The page may be protected, private, or not accessible. "
                "Please try uploading a screenshot instead."
            )
        
        result = data["results"][0]
        
        # Try to get raw_content first (full page content), fallback to cleaned_content
        extracted_text = result.get("raw_content") or result.get("cleaned_content")
        
        # If both are empty, provide helpful error
        if not extracted_text or extracted_text.strip() == "":
            raise LinkExtractionError(
                "The link provided does not contain extractable text. "
                "This may be a social media post that requires authentication or a page with protected content. "
                "Please try uploading a screenshot of the post instead."
            )
        
        return extracted_text
            
    except requests.exceptions.Timeout:
        raise LinkExtractionError(
            "The request to fetch content from the link timed out. "
            "Please try again or upload a screenshot instead."
        )
    except requests.exceptions.RequestException as e:
        raise LinkExtractionError(
            "Failed to fetch content from the link. "
            "Please verify the URL is correct and try again, or upload a screenshot instead."
        ) from e
    except LinkExtractionError:
        raise
    except Exception as e:
        error_msg = str(e)
        # Re-raise with our custom message if it's already one of ours
        if "Could not extract" in error_msg or "does not contain" in error_msg:
            raise
        # Otherwise wrap it
        raise LinkExtractionError(
            "An error occurred while processing the link. "
            "Please try uploading a screenshot instead."
        ) from e
