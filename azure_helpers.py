"""
Azure OpenAI helper functions for Ask Druk
"""

import logging
import json
import re
from typing import Dict, Any, Optional
from druk_system_prompt import DRUK_SYSTEM_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def parse_azure_error(error_text: str) -> Dict[str, Any]:
    """
    Parse Azure OpenAI error messages into a structured format
    
    Args:
        error_text: The error text from Azure OpenAI
        
    Returns:
        Structured error information
    """
    result = {
        "error_type": "unknown",
        "error_code": None,
        "error_message": error_text,
        "content_filter": {
            "triggered": False,
            "jailbreak": False,
            "hate": False,
            "sexual": False,
            "violence": False,
            "self_harm": False,
        }
    }
    
    try:
        # Try to extract JSON from the error message
        json_match = re.search(r'\{.*\}', error_text, re.DOTALL)
        if json_match:
            error_json = json.loads(json_match.group(0))
            
            # Extract error details
            if "error" in error_json:
                error = error_json["error"]
                result["error_type"] = error.get("type", "unknown")
                result["error_code"] = error.get("code", None)
                result["error_message"] = error.get("message", error_text)
                
                # Check for content filtering
                if error.get("code") == "content_filter" and "innererror" in error:
                    inner_error = error["innererror"]
                    result["content_filter"]["triggered"] = True
                    
                    if "content_filter_result" in inner_error:
                        filter_results = inner_error["content_filter_result"]
                        
                        # Check each filter type
                        if "jailbreak" in filter_results and filter_results["jailbreak"].get("filtered", False):
                            result["content_filter"]["jailbreak"] = True
                            
                        if "hate" in filter_results and filter_results["hate"].get("filtered", False):
                            result["content_filter"]["hate"] = True
                            
                        if "sexual" in filter_results and filter_results["sexual"].get("filtered", False):
                            result["content_filter"]["sexual"] = True
                            
                        if "violence" in filter_results and filter_results["violence"].get("filtered", False):
                            result["content_filter"]["violence"] = True
                            
                        if "self_harm" in filter_results and filter_results["self_harm"].get("filtered", False):
                            result["content_filter"]["self_harm"] = True
    except Exception as e:
        logging.error(f"Error parsing Azure error: {str(e)}")
        # Fall back to basic text matching if JSON parsing fails
        if "content_filter" in error_text or "policy" in error_text:
            result["content_filter"]["triggered"] = True
            
        if "jailbreak" in error_text:
            result["content_filter"]["jailbreak"] = True
    
    return result

def get_user_friendly_error_message(error_info: Dict[str, Any]) -> str:
    """
    Generate a user-friendly error message for Druk users
    
    Args:
        error_info: Structured error information from parse_azure_error
        
    Returns:
        User-friendly error message
    """
    if error_info["content_filter"]["triggered"]:
        return "I understand your question, but I need you to ask it in a different way. Please try rephrasing your question more simply."
    
    # For other types of errors
    if error_info["error_code"] == "model_error":
        return "I'm having trouble processing your request right now. Please try asking again or contact our support team."
    
    if error_info["error_code"] == "rate_limit_exceeded":
        return "I'm experiencing high demand right now. Please wait a moment and try again."
    
    # Generic fallback
    return "I'm having difficulty understanding your request. Could you please try asking your question in a different way?"

def create_safe_system_prompt() -> str:
    """
    Create a system prompt that's safe for Azure OpenAI content filters
    
    Returns:
        A safe system prompt for Druk
    """
    return DRUK_SYSTEM_PROMPT

def create_safe_chat_prompt(user_message: str) -> str:
    """
    Create a safe chat prompt for user messages
    
    Args:
        user_message: The user's message
        
    Returns:
        A safely formatted prompt
    """
    return f"Please help me with this question about Bhutanese government services or citizen rights: {user_message}"
