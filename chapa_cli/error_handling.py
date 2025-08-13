"""
Enhanced error handling and retry logic for Chapa CLI.
"""

import time
import requests
from typing import Dict, Any, Optional, Callable
from functools import wraps

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import logging

console = Console()
logger = logging.getLogger(__name__)


class ChapaAPIError(Exception):
    """Custom exception for Chapa API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def with_loading_indicator(message: str = "Processing..."):
    """Decorator to show loading indicator for long operations."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task(message, total=None)
                try:
                    result = func(*args, **kwargs)
                    progress.update(task, description=f"✓ {message}")
                    return result
                except Exception as e:
                    progress.update(task, description=f"✗ {message}")
                    raise
        return wrapper
    return decorator


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout)),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def make_api_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> requests.Response:
    """Make API request with retry logic and proper error handling."""
    
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=json_data,
            timeout=timeout
        )
        
        # Check for HTTP errors
        if not response.ok:
            logger.error(f"API request failed with status code {response.status_code} and response content: {response.text}")
            handle_api_error(response)
        
        return response
        
    except requests.ConnectionError as e:
        error_msg = "Unable to connect to Chapa API. Please check your internet connection."
        logger.error(f"Connection error: {e}")
        raise ChapaAPIError(error_msg) from e
        
    except requests.Timeout as e:
        error_msg = "Request to Chapa API timed out. Please try again."
        logger.error(f"Timeout error: {e}")
        raise ChapaAPIError(error_msg) from e
        
    except requests.RequestException as e:
        error_msg = f"Network error occurred: {str(e)}"
        logger.error(f"Request error: {e}")
        raise ChapaAPIError(error_msg) from e


def handle_api_error(response: requests.Response):
    """Handle API error responses with detailed error messages."""
    
    try:
        error_data = response.json()
    except ValueError:
        error_data = {"message": "Unknown error occurred"}
    
    status_code = response.status_code
    error_message = error_data.get('message', 'Unknown error')
    
    # Specific error handling based on status codes
    if status_code == 400:
        raise ChapaAPIError(
            f"Bad Request: {error_message}. Please check your input parameters.",
            status_code,
            error_data
        )
    elif status_code == 401:
        raise ChapaAPIError(
            "Authentication failed. Please check your API token and login again.",
            status_code,
            error_data
        )
    elif status_code == 403:
        raise ChapaAPIError(
            "Access forbidden. Your account may not have permission for this action.",
            status_code,
            error_data
        )
    elif status_code == 404:
        raise ChapaAPIError(
            f"Resource not found: {error_message}",
            status_code,
            error_data
        )
    elif status_code == 429:
        raise ChapaAPIError(
            "Rate limit exceeded. Please wait a moment before trying again.",
            status_code,
            error_data
        )
    elif status_code >= 500:
        raise ChapaAPIError(
            "Chapa API server error. Please try again later.",
            status_code,
            error_data
        )
    else:
        raise ChapaAPIError(
            f"API error: {error_message}",
            status_code,
            error_data
        )


def handle_json_decode_error(response: requests.Response) -> Dict[str, Any]:
    """Handle JSON decode errors gracefully."""
    
    try:
        return response.json()
    except ValueError as e:
        logger.error(f"Failed to decode JSON response: {e}")
        logger.error(f"Response content: {response.text}")
        
        # Return a structured error response
        return {
            "error": True,
            "message": "Invalid response format from server",
            "status_code": response.status_code,
            "raw_response": response.text[:500]  # Limit to prevent huge logs
        }


def safe_api_call(func: Callable) -> Callable:
    """Decorator for safe API calls with comprehensive error handling."""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ChapaAPIError as e:
            # Re-raise Chapa API errors as-is
            raise
        except click.ClickException:
            # Re-raise Click exceptions - like BadParameter as-is
            raise
        except Exception as e:
            # Catch all other exceptions and convert to user-friendly message
            logger.exception("Unexpected error occurred")
            raise ChapaAPIError(f"Unexpected error: {str(e)}") from e
    
    return wrapper


def display_error(error: ChapaAPIError, verbose: bool = False):
    """Display error message to user with appropriate formatting."""
    
    console.print(f"[red]Error:[/red] {error.message}")
    
    if verbose and error.response_data:
        console.print("\n[yellow]Additional details:[/yellow]")
        for key, value in error.response_data.items():
            console.print(f"  {key}: {value}")
    
    if error.status_code:
        console.print(f"[dim]Status Code: {error.status_code}[/dim]")


def display_success(message: str, data: Optional[Dict[str, Any]] = None):
    """Display success message with optional data."""
    
    console.print(f"[green]✓[/green] {message}")
    
    if data:
        console.print()
        for key, value in data.items():
            if key.lower() in ['url', 'link', 'checkout_url']:
                console.print(f"[blue]{key}:[/blue] [link]{value}[/link]")
            else:
                console.print(f"[blue]{key}:[/blue] {value}")
