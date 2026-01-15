"""
Utility helper functions.
"""
import re
from datetime import datetime
from typing import Any, Dict, Optional


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format amount as currency.
    
    Args:
        amount: Amount to format
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    return f"${amount:.2f}"


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number string
        
    Returns:
        True if valid, False otherwise
    """
    # Simple validation - accepts formats like: +1-234-567-8900, (234) 567-8900, 234-567-8900
    pattern = r'^[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}$'
    return bool(re.match(pattern, phone))


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address string
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    return filename


def parse_data_size(size_str: str) -> Optional[float]:
    """
    Parse data size string to GB.
    
    Args:
        size_str: Size string (e.g., "5GB", "500MB", "Unlimited")
        
    Returns:
        Size in GB or None if unlimited
    """
    size_str = size_str.upper().strip()
    
    if "UNLIMITED" in size_str:
        return None
    
    # Extract number
    match = re.search(r'(\d+(?:\.\d+)?)', size_str)
    if not match:
        return None
    
    value = float(match.group(1))
    
    # Convert to GB
    if "MB" in size_str:
        return value / 1024
    elif "TB" in size_str:
        return value * 1024
    elif "GB" in size_str:
        return value
    
    return value


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object.
    
    Args:
        dt: Datetime object
        format_str: Format string
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two dictionaries recursively.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result
