"""Safe JSON parsing utilities to handle EOF and incomplete JSON errors"""

import json
import re
from typing import Any, Optional, Dict


def safe_json_loads(text: str, default: Optional[Dict] = None) -> Dict:
    """
    Safely parse JSON string, handling EOF errors and incomplete JSON
    
    Args:
        text: JSON string to parse
        default: Default value to return if parsing fails
        
    Returns:
        Parsed JSON dictionary or default value
    """
    if not text or not isinstance(text, str):
        return default or {}
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    if not text:
        return default or {}
    
    try:
        # Try direct parsing first
        return json.loads(text)
    except json.JSONDecodeError as e:
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except (json.JSONDecodeError, ValueError):
                pass
        
        # Try to fix common JSON issues
        try:
            # Remove trailing commas
            text = re.sub(r',\s*}', '}', text)
            text = re.sub(r',\s*]', ']', text)
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # If all else fails, return default
        return default or {}


def safe_json_parse_response(response_text: str, default: Optional[Dict] = None) -> Dict:
    """
    Safely parse JSON from API response, handling incomplete responses
    
    Args:
        response_text: Response text from API
        default: Default value to return if parsing fails
        
    Returns:
        Parsed JSON dictionary or default value
    """
    if not response_text:
        return default or {}
    
    # Try to extract JSON object
    json_match = re.search(r'\{[\s\S]*\}', response_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, ValueError, EOFError) as e:
            # Try to fix incomplete JSON
            try:
                # Close unclosed brackets
                open_braces = json_str.count('{')
                close_braces = json_str.count('}')
                if open_braces > close_braces:
                    json_str += '}' * (open_braces - close_braces)
                
                open_brackets = json_str.count('[')
                close_brackets = json_str.count(']')
                if open_brackets > close_brackets:
                    json_str += ']' * (open_brackets - close_brackets)
                
                return json.loads(json_str)
            except (json.JSONDecodeError, ValueError, EOFError):
                return default or {}
    
    return default or {}


def safe_extract_json_from_text(text: str) -> Optional[Dict]:
    """
    Extract and parse JSON from text that may contain other content
    
    Args:
        text: Text that may contain JSON
        
    Returns:
        Parsed JSON dictionary or None
    """
    if not text:
        return None
    
    # Try to find JSON object in text
    json_match = re.search(r'\{[\s\S]*\}', text, re.DOTALL)
    if json_match:
        return safe_json_loads(json_match.group(0))
    
    return None


