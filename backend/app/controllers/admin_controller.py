from app.models.user import User
from app.models.tutor import Tutor
from app.models.chat import Chat
from app.models.message import Message
from app.models.rating import Rating
from datetime import datetime, timedelta
from typing import List, Dict
from app.extensions import mongo
from bson import ObjectId

class AdminController:
    """Controller for admin operations."""

    @staticmethod
    def get_pending_students() -> dict:
        """Get students pending verification."""
        try:
            # Find all users with role='student' and is_verified=False
            pending_students = list(mongo.db.users.find(
                {
                    'role': 'student',
                    'is_verified': False
                },
                {
                    'password': 0  # Exclude password field
                }
            ))

            # Convert ObjectId to string for JSON serialization
            for student in pending_students:
                student['_id'] = str(student['_id'])

            return {
                'success': True,
                'students': pending_students
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }

    @staticmethod
    def verify_student(student_id: str) -> dict:
        """Verify a student account."""
        try:
            result = mongo.db.users.update_one(
                {
                    '_id': ObjectId(student_id),
                    'role': 'student'
                },
                {
                    '$set': {'is_verified': True}
                }
            )

            if result.modified_count > 0:
                return {
                    'success': True,
                    'message': 'Student verified successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Student not found or already verified'
                }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }

    @staticmethod
    def get_profile(admin_id: str) -> dict:
        """Get admin profile with statistics."""
        try:
            admin = User.find_by_id(admin_id)
            if not admin or admin.get('role') != 'admin':
                return {'success': False, 'message': 'Admin not found or unauthorized'}

            total_students = len(User.find_all_students())
            verified_students = len(User.find_all_students(verified_only=True))
            pending_students = total_students - verified_students

            total_tutors = len(Tutor.find_all(active_only=False))
            active_tutors = len(Tutor.find_all(active_only=True))

            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            avg_rating = Rating.get_average_rating()
            token_stats = Message.get_token_usage_stats(date_from=thirty_days_ago)

            return {
                'success': True,
                'profile': {
                    'id': str(admin['_id']),
                    'name': admin['name'],
                    'email': admin['email'],
                    'role': admin['role'],
                    'created_at': admin['created_at']
                },
                'stats': {
                    'students': {
                        'total': total_students,
                        'verified': verified_students,
                        'pending_verification': pending_students
                    },
                    'tutors': {
                        'total': total_tutors,
                        'active': active_tutors
                    },
                    'ai_usage': {
                        'avg_rating': avg_rating,
                        'tokens_used_30d': token_stats.get('total_tokens', 0),
                        'messages_30d': token_stats.get('total_messages', 0)
                    }
                }
            }
        except Exception as e:
            return {'success': False, 'message': f'Failed to get admin profile: {str(e)}'}

    @staticmethod
    def add_tutor(admin_id: str, tutor_data: dict) -> dict:
        """Add a new tutor."""
        try:
            required_fields = ['name', 'subjects', 'hourly_rate', 'school', 'gpa', 'contact_info']
            for field in required_fields:
                if field not in tutor_data:
                    return {'success': False, 'message': f'Missing required field: {field}'}

            if not isinstance(tutor_data['subjects'], list) or not tutor_data['subjects']:
                return {'success': False, 'message': 'Subjects must be a non-empty list'}

            try:
                hourly_rate = float(tutor_data['hourly_rate'])
                if hourly_rate <= 0:
                    raise ValueError()
            except (ValueError, TypeError):
                return {'success': False, 'message': 'Invalid hourly rate'}

            try:
                gpa = float(tutor_data['gpa'])
                if not (0.0 <= gpa <= 4.0):
                    raise ValueError()
            except (ValueError, TypeError):
                return {'success': False, 'message': 'GPA must be between 0.0 and 4.0'}

            contact_info = tutor_data['contact_info']
            if not isinstance(contact_info, dict) or 'email' not in contact_info:
                return {'success': False, 'message': 'Contact info must include email'}

            tutor = Tutor(
                name=tutor_data['name'],
                subjects=tutor_data['subjects'],
                hourly_rate=hourly_rate,
                school=tutor_data['school'],
                gpa=gpa,
                contact_info=contact_info,
                created_by_admin=admin_id
            )

            tutor_id = tutor.save()
            return {'success': True, 'message': 'Tutor added successfully', 'tutor_id': tutor_id}

        except Exception as e:
            return {'success': False, 'message': f'Failed to add tutor: {str(e)}'}

    @staticmethod
    def update_profile(admin_id: str, data: dict) -> dict:
        """Update admin profile (name, email, school) safely."""
        try:
            allowed_fields = ['name', 'email', 'school']
            update_data = {field: data[field] for field in allowed_fields if field in data}

            if not update_data:
                return {'success': False, 'message': 'No valid fields to update'}

            result = mongo.db.users.update_one(
                {'_id': ObjectId(admin_id), 'role': 'admin'},
                {'$set': update_data}
            )

            if result.matched_count == 0:
                return {'success': False, 'message': 'Admin not found or unauthorized'}

            updated_user = mongo.db.users.find_one({'_id': ObjectId(admin_id)}, {'password': 0})
            updated_user['_id'] = str(updated_user['_id'])
            return {'success': True, 'user': updated_user}

        except Exception as e:
            return {'success': False, 'message': str(e)}
