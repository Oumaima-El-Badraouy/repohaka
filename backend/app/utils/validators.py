import re
from typing import Dict, List

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> Dict[str, any]:
    """Validate password strength."""
    if len(password) < 8:
        return {
            'valid': False,
            'message': 'Password must be at least 8 characters long'
        }
    
    if not re.search(r'[A-Z]', password):
        return {
            'valid': False,
            'message': 'Password must contain at least one uppercase letter'
        }
    
    if not re.search(r'[a-z]', password):
        return {
            'valid': False,
            'message': 'Password must contain at least one lowercase letter'
        }
    
    if not re.search(r'\d', password):
        return {
            'valid': False,
            'message': 'Password must contain at least one number'
        }
    
    return {
        'valid': True,
        'message': 'Password is valid'
    }

def validate_student_id(student_id: str) -> bool:
    """Validate student ID format (basic validation)."""
    # Basic validation: alphanumeric, 3-20 characters
    pattern = r'^[a-zA-Z0-9]{3,20}$'
    return bool(re.match(pattern, student_id))

def validate_gpa(gpa: float) -> bool:
    """Validate GPA range."""
    return 0.0 <= gpa <= 4.0

def validate_rating(rating: int) -> bool:
    """Validate rating range (1-5 stars)."""
    return isinstance(rating, int) and 1 <= rating <= 5

def validate_subjects(subjects: List[str]) -> Dict[str, any]:
    """Validate subjects list."""
    if not isinstance(subjects, list):
        return {
            'valid': False,
            'message': 'Subjects must be a list'
        }
    
    if not subjects:
        return {
            'valid': False,
            'message': 'At least one subject is required'
        }
    
    # Check each subject
    for subject in subjects:
        if not isinstance(subject, str) or not subject.strip():
            return {
                'valid': False,
                'message': 'All subjects must be non-empty strings'
            }
        
        if len(subject.strip()) > 50:
            return {
                'valid': False,
                'message': 'Subject names must be 50 characters or less'
            }
    
    return {
        'valid': True,
        'message': 'Subjects are valid'
    }

def validate_hourly_rate(rate: float) -> Dict[str, any]:
    """Validate hourly rate."""
    try:
        rate = float(rate)
        if rate <= 0:
            return {
                'valid': False,
                'message': 'Hourly rate must be greater than 0'
            }
        
        if rate > 1000:
            return {
                'valid': False,
                'message': 'Hourly rate seems unreasonably high'
            }
        
        return {
            'valid': True,
            'message': 'Hourly rate is valid'
        }
    except (ValueError, TypeError):
        return {
            'valid': False,
            'message': 'Hourly rate must be a valid number'
        }

def validate_contact_info(contact_info: Dict) -> Dict[str, any]:
    """Validate contact information."""
    if not isinstance(contact_info, dict):
        return {
            'valid': False,
            'message': 'Contact info must be an object'
        }
    
    if 'email' not in contact_info:
        return {
            'valid': False,
            'message': 'Email is required in contact info'
        }
    
    if not validate_email(contact_info['email']):
        return {
            'valid': False,
            'message': 'Invalid email in contact info'
        }
    
    # Validate phone if provided
    if 'phone' in contact_info:
        phone = contact_info['phone'].strip()
        if phone and not re.match(r'^[+]?[1-9]?\d{1,14}$', phone.replace(' ', '').replace('-', '')):
            return {
                'valid': False,
                'message': 'Invalid phone number format'
            }
    
    return {
        'valid': True,
        'message': 'Contact info is valid'
    }

def sanitize_text(text: str, max_length: int = None) -> str:
    """Sanitize text input."""
    if not isinstance(text, str):
        return ''
    
    # Remove dangerous characters and normalize whitespace
    text = re.sub(r'[<>"\'\/\\]', '', text)
    text = ' '.join(text.split())  # Normalize whitespace
    
    if max_length and len(text) > max_length:
        text = text[:max_length].rsplit(' ', 1)[0] + '...'
    
    return text

def validate_search_query(query: str) -> Dict[str, any]:
    """Validate search query."""
    if not isinstance(query, str):
        return {
            'valid': False,
            'message': 'Query must be a string'
        }
    
    query = query.strip()
    
    if not query:
        return {
            'valid': False,
            'message': 'Query cannot be empty'
        }
    
    if len(query) < 2:
        return {
            'valid': False,
            'message': 'Query must be at least 2 characters long'
        }
    
    if len(query) > 200:
        return {
            'valid': False,
            'message': 'Query must be 200 characters or less'
        }
    
    return {
        'valid': True,
        'message': 'Query is valid',
        'sanitized_query': sanitize_text(query)
    }