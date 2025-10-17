from datetime import datetime
from typing import Optional, List, Dict
from bson import ObjectId
from app.extensions import mongo

class Tutor:
    """Tutor model for human tutors."""
    
    def __init__(self, name: str, subjects: List[str], hourly_rate: float,
                 school: str, gpa: float, contact_info: Dict[str, str],
                 created_by_admin: str):
        self.name = name.strip()
        self.subjects = [subject.strip().lower() for subject in subjects]
        self.hourly_rate = hourly_rate
        self.school = school.strip()
        self.gpa = gpa
        self.contact_info = contact_info  # {'email': '', 'phone': ''}
        self.created_by_admin = ObjectId(created_by_admin)
        self.created_at = datetime.utcnow()
        self.is_active = True
        self.rating_average = 0.0
        self.total_sessions = 0
    
    def save(self):
        """Save tutor to database."""
        tutor_data = {
            'name': self.name,
            'subjects': self.subjects,
            'hourly_rate': self.hourly_rate,
            'school': self.school,
            'gpa': self.gpa,
            'contact_info': self.contact_info,
            'created_by_admin': self.created_by_admin,
            'created_at': self.created_at,
            'is_active': self.is_active,
            'rating_average': self.rating_average,
            'total_sessions': self.total_sessions
        }
        result = mongo.db.tutors.insert_one(tutor_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_id(tutor_id: str) -> Optional[dict]:
        """Find tutor by ID."""
        try:
            return mongo.db.tutors.find_one({'_id': ObjectId(tutor_id)})
        except:
            return None
    
    @staticmethod
    def find_all(active_only: bool = True) -> List[dict]:
        """Find all tutors."""
        query = {}
        if active_only:
            query['is_active'] = True
        return list(mongo.db.tutors.find(query).sort('gpa', -1))
    
    @staticmethod
    def find_by_subjects(subjects: List[str], limit: int = 10) -> List[dict]:
        """Find tutors by subjects."""
        normalized_subjects = [subject.strip().lower() for subject in subjects]
        query = {
            'subjects': {'$in': normalized_subjects},
            'is_active': True
        }
        return list(
            mongo.db.tutors.find(query)
            .sort([('gpa', -1), ('rating_average', -1)])
            .limit(limit)
        )
    
    @staticmethod
    def search_tutors(school: str = None, min_gpa: float = None, 
                     subjects: List[str] = None) -> List[dict]:
        """Advanced tutor search."""
        query = {'is_active': True}
        
        if school:
            query['school'] = {'$regex': school, '$options': 'i'}
        
        if min_gpa:
            query['gpa'] = {'$gte': min_gpa}
        
        if subjects:
            normalized_subjects = [subject.strip().lower() for subject in subjects]
            query['subjects'] = {'$in': normalized_subjects}
        
        return list(
            mongo.db.tutors.find(query)
            .sort([('gpa', -1), ('rating_average', -1)])
        )
    
    @staticmethod
    def get_recommendations(user_subjects: List[str], limit: int = 5) -> List[dict]:
        """Get tutor recommendations based on subjects."""
        if not user_subjects:
            # Return top-rated tutors
            return list(
                mongo.db.tutors.find({'is_active': True})
                .sort([('rating_average', -1), ('gpa', -1)])
                .limit(limit)
            )
        
        normalized_subjects = [subject.strip().lower() for subject in user_subjects]
        pipeline = [
            {
                '$match': {
                    'is_active': True,
                    'subjects': {'$in': normalized_subjects}
                }
            },
            {
                '$addFields': {
                    'subject_match_count': {
                        '$size': {
                            '$setIntersection': ['$subjects', normalized_subjects]
                        }
                    }
                }
            },
            {
                '$sort': {
                    'subject_match_count': -1,
                    'gpa': -1,
                    'rating_average': -1
                }
            },
            {'$limit': limit}
        ]
        
        return list(mongo.db.tutors.aggregate(pipeline))
    
    @staticmethod
    def update_stats(tutor_id: str, new_rating: float = None):
        """Update tutor statistics."""
        try:
            updates = {'$inc': {'total_sessions': 1}}
            
            if new_rating is not None:
                # Recalculate average rating (simplified approach)
                tutor = mongo.db.tutors.find_one({'_id': ObjectId(tutor_id)})
                if tutor:
                    current_avg = tutor.get('rating_average', 0.0)
                    total_sessions = tutor.get('total_sessions', 0)
                    
                    # Simple average update (in production, you'd want more sophisticated rating)
                    new_avg = ((current_avg * total_sessions) + new_rating) / (total_sessions + 1)
                    updates['$set'] = {'rating_average': round(new_avg, 2)}
            
            mongo.db.tutors.update_one(
                {'_id': ObjectId(tutor_id)},
                updates
            )
            return True
        except:
            return False
    
    def to_dict(self) -> dict:
        """Convert tutor to dictionary."""
        return {
            'name': self.name,
            'subjects': self.subjects,
            'hourly_rate': self.hourly_rate,
            'school': self.school,
            'gpa': self.gpa,
            'contact_info': self.contact_info,
            'created_at': self.created_at,
            'is_active': self.is_active,
            'rating_average': self.rating_average,
            'total_sessions': self.total_sessions
        }