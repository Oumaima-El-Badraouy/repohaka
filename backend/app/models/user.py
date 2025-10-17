from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from app.extensions import mongo
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    """User model for students and admins."""
    
    def __init__(self, email: str, password: str, name: str, role: str, 
                 school: str, student_id: str, is_verified: bool = False):
        self.email = email.lower().strip()
        self.password_hash = generate_password_hash(password)
        self.name = name.strip()
        self.role = role  # 'student' or 'admin'
        self.school = school.strip()
        self.student_id = student_id.strip()
        self.is_verified = is_verified
        self.created_at = datetime.utcnow()
        self.last_login = None
    
    def save(self):
        """Save user to database."""
        user_data = {
            'email': self.email,
            'password_hash': self.password_hash,
            'name': self.name,
            'role': self.role,
            'school': self.school,
            'student_id': self.student_id,
            'is_verified': self.is_verified,
            'created_at': self.created_at,
            'last_login': self.last_login
        }
        result = mongo.db.users.insert_one(user_data)
        return str(result.inserted_id)
    
    def update_last_login(self):
        """Update last login timestamp."""
        mongo.db.users.update_one(
            {'email': self.email},
            {'$set': {'last_login': datetime.utcnow()}}
        )
    
    def check_password(self, password: str) -> bool:
        """Check if provided password matches."""
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def find_by_email(email: str) -> Optional[dict]:
        """Find user by email."""
        return mongo.db.users.find_one({'email': email.lower().strip()})
    
    @staticmethod
    def find_by_id(user_id: str) -> Optional[dict]:
        """Find user by ID."""
        try:
            return mongo.db.users.find_one({'_id': ObjectId(user_id)})
        except:
            return None
    
    @staticmethod
    def find_all_students(verified_only: bool = False) -> List[dict]:
        """Find all students."""
        query = {'role': 'student'}
        if verified_only:
            query['is_verified'] = True
        return list(mongo.db.users.find(query).sort('created_at', -1))
    
    @staticmethod
    def verify_student(user_id: str) -> bool:
        """Verify a student account."""
        try:
            result = mongo.db.users.update_one(
                {'_id': ObjectId(user_id), 'role': 'student'},
                {'$set': {'is_verified': True}}
            )
            return result.modified_count > 0
        except:
            return False
    
    @staticmethod
    def email_exists(email: str) -> bool:
        """Check if email already exists."""
        return mongo.db.users.find_one({'email': email.lower().strip()}) is not None
    
    def to_dict(self) -> dict:
        """Convert user to dictionary (excluding password)."""
        return {
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'school': self.school,
            'student_id': self.student_id,
            'is_verified': self.is_verified,
            'created_at': self.created_at,
            'last_login': self.last_login
        }