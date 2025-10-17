import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List
import json

def generate_request_id() -> str:
    """Generate unique request ID for logging."""
    return str(uuid.uuid4())

def generate_hash(text: str) -> str:
    """Generate SHA-256 hash of text."""
    return hashlib.sha256(text.encode()).hexdigest()

def format_datetime(dt: datetime) -> str:
    """Format datetime for API responses."""
    if dt:
        return dt.isoformat() + 'Z'
    return None

def parse_datetime(dt_str: str) -> datetime:
    """Parse datetime string."""
    try:
        # Remove 'Z' if present
        if dt_str.endswith('Z'):
            dt_str = dt_str[:-1]
        return datetime.fromisoformat(dt_str)
    except:
        return None

def paginate_results(data: List[Any], page: int, per_page: int) -> Dict:
    """Paginate a list of results."""
    total = len(data)
    start = (page - 1) * per_page
    end = start + per_page
    
    return {
        'data': data[start:end],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page if per_page > 0 else 0,
            'has_next': end < total,
            'has_prev': page > 1
        }
    }

def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to integer."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_bool(value: Any, default: bool = False) -> bool:
    """Safely convert value to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on')
    if isinstance(value, (int, float)):
        return bool(value)
    return default

def clean_dict(data: Dict, remove_none: bool = True, remove_empty: bool = False) -> Dict:
    """Clean dictionary by removing None/empty values."""
    cleaned = {}
    
    for key, value in data.items():
        if remove_none and value is None:
            continue
        if remove_empty and value in ('', [], {}):
            continue
        
        if isinstance(value, dict):
            cleaned_value = clean_dict(value, remove_none, remove_empty)
            if cleaned_value or not remove_empty:
                cleaned[key] = cleaned_value
        else:
            cleaned[key] = value
    
    return cleaned

def truncate_text(text: str, max_length: int, suffix: str = '...') -> str:
    """Truncate text to maximum length."""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """Extract keywords from text."""
    import re
    
    # Remove special characters and split into words
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    # Filter by minimum length and remove common stop words
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
    }
    
    keywords = [word for word in words if len(word) >= min_length and word not in stop_words]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for word in keywords:
        if word not in seen:
            seen.add(word)
            unique_keywords.append(word)
    
    return unique_keywords

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate basic text similarity (Jaccard similarity)."""
    keywords1 = set(extract_keywords(text1))
    keywords2 = set(extract_keywords(text2))
    
    if not keywords1 and not keywords2:
        return 1.0
    
    intersection = keywords1.intersection(keywords2)
    union = keywords1.union(keywords2)
    
    return len(intersection) / len(union) if union else 0.0

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return '0 B'
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f'{size:.1f} {units[unit_index]}'

def generate_chat_title(first_message: str, max_length: int = 50) -> str:
    """Generate a chat title from the first message."""
    if not first_message:
        return 'New Chat'
    
    # Clean and truncate the message
    title = ' '.join(first_message.split())  # Normalize whitespace
    title = truncate_text(title, max_length - 3)  # Leave room for '...'
    
    # Capitalize first letter
    if title:
        title = title[0].upper() + title[1:]
    
    return title or 'New Chat'

def time_ago(dt: datetime) -> str:
    """Get human-readable time difference."""
    if not dt:
        return 'Never'
    
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 0:
        if diff.days == 1:
            return '1 day ago'
        elif diff.days < 7:
            return f'{diff.days} days ago'
        elif diff.days < 30:
            weeks = diff.days // 7
            return f'{weeks} week{"s" if weeks > 1 else ""} ago'
        else:
            months = diff.days // 30
            return f'{months} month{"s" if months > 1 else ""} ago'
    
    hours = diff.seconds // 3600
    if hours > 0:
        return f'{hours} hour{"s" if hours > 1 else ""} ago'
    
    minutes = diff.seconds // 60
    if minutes > 0:
        return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
    
    return 'Just now'


def jwt_current_user():
    """Return a normalized current_user dict from JWT.

    flask_jwt_extended historically allowed arbitrary identity objects, but
    recent JWT libraries require the JWT 'sub' (subject) claim to be a string.
    This helper returns a consistent dict with keys 'user_id', 'email', 'role'
    whether the token's identity was stored as a dict (legacy) or as a string
    identity + additional claims.
    """
    try:
        # Import here to avoid top-level import cycles
        from flask_jwt_extended import get_jwt_identity, get_jwt

        identity = get_jwt_identity()
        if isinstance(identity, dict) and identity.get('user_id'):
            return identity

        # identity is likely a string (user id). Pull additional claims from JWT.
        claims = get_jwt() or {}
        return {
            'user_id': str(identity) if identity is not None else None,
            'email': claims.get('email'),
            'role': claims.get('role')
        }
    except Exception:
        return None