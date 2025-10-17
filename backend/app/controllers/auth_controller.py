from flask_jwt_extended import create_access_token, create_refresh_token
from app.utils.helpers import jwt_current_user
from app.models.user import User
from app.utils.validators import validate_email, validate_password
from datetime import datetime

class AuthController:
    """Controller for authentication operations."""
    
    @staticmethod
    def register_student(data: dict) -> dict:
        """Register a new student."""
        try:
            # Extract and validate data
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            name = data.get('name', '').strip()
            school = data.get('school', '').strip()
            student_id = data.get('student_id', '').strip()
            
            # Validation
            if not all([email, password, name, school, student_id]):
                return {
                    'success': False,
                    'message': 'All fields are required'
                }
            
            if not validate_email(email):
                return {
                    'success': False,
                    'message': 'Invalid email format'
                }
            
            # Check school email domain (basic validation)
            if not email.endswith('.edu') and not email.endswith('.ac.uk'):
                return {
                    'success': False,
                    'message': 'Please use your school email address'
                }
            
            password_validation = validate_password(password)
            if not password_validation['valid']:
                return {
                    'success': False,
                    'message': password_validation['message']
                }
            
            # Check if email already exists
            if User.email_exists(email):
                return {
                    'success': False,
                    'message': 'Email already registered'
                }
            
            # Create user
            user = User(
                email=email,
                password=password,
                name=name,
                role='student',
                school=school,
                student_id=student_id,
                is_verified=False  # Requires admin verification
            )
            
            user_id = user.save()
            
            return {
                'success': True,
                'message': 'Registration successful. Please wait for admin verification.',
                'user_id': user_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Registration failed: {str(e)}'
            }
    
    @staticmethod
    def login(data: dict) -> dict:
        """Authenticate user and return tokens."""
        try:
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            if not email or not password:
                return {
                    'success': False,
                    'message': 'Email and password are required'
                }
            
            # Find user
            user_data = User.find_by_email(email)
            if not user_data:
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }
            
            # Create user instance to check password
            user = User(
                email=user_data['email'],
                password='',  # We don't need the actual password
                name=user_data['name'],
                role=user_data['role'],
                school=user_data['school'],
                student_id=user_data['student_id']
            )
            user.password_hash = user_data['password_hash']
            
            if not user.check_password(password):
                return {
                    'success': False,
                    'message': 'Invalid email or password'
                }
            
            # Check if student is verified
            if user_data['role'] == 'student' and not user_data['is_verified']:
                return {
                    'success': False,
                    'message': 'Account pending admin verification'
                }
            
            # Update last login
            user.update_last_login()
            
            # Create tokens
            # Use string identity for 'sub' and store other info as additional claims
            uid_str = str(user_data['_id'])
            additional = {'email': user_data['email'], 'role': user_data['role']}

            access_token = create_access_token(identity=uid_str, additional_claims=additional)
            refresh_token = create_refresh_token(identity=uid_str, additional_claims=additional)
            
            # Prepare user data (without password)
            user_info = {
                'id': str(user_data['_id']),
                'email': user_data['email'],
                'name': user_data['name'],
                'role': user_data['role'],
                'school': user_data['school'],
                'student_id': user_data['student_id'],
                'is_verified': user_data['is_verified']
            }
            
            return {
                'success': True,
                'message': 'Login successful',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Login failed: {str(e)}'
            }
    
    @staticmethod
    def refresh_token() -> dict:
        """Refresh access token."""
        try:
            current_user = jwt_current_user()
            
            # Verify user still exists and is verified
            user_data = User.find_by_id(current_user['user_id'])
            if not user_data:
                return {
                    'success': False,
                    'message': 'User not found'
                }
            
            if user_data['role'] == 'student' and not user_data['is_verified']:
                return {
                    'success': False,
                    'message': 'Account no longer verified'
                }
            
            # Create new access token using string identity and recreate additional claims
            uid = current_user.get('user_id') if isinstance(current_user, dict) else current_user
            if not uid:
                return {
                    'success': False,
                    'message': 'Invalid token identity'
                }

            additional = {
                'email': current_user.get('email') if isinstance(current_user, dict) else None,
                'role': current_user.get('role') if isinstance(current_user, dict) else None
            }

            access_token = create_access_token(identity=str(uid), additional_claims=additional)
            
            return {
                'success': True,
                'access_token': access_token
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Token refresh failed: {str(e)}'
            }
    
    @staticmethod
    def get_current_user(user_id: str) -> dict:
        """Get current user information."""
        try:
            user_data = User.find_by_id(user_id)
            if not user_data:
                return {
                    'success': False,
                    'message': 'User not found'
                }
            
            user_info = {
                'id': str(user_data['_id']),
                'email': user_data['email'],
                'name': user_data['name'],
                'role': user_data['role'],
                'school': user_data['school'],
                'student_id': user_data['student_id'],
                'is_verified': user_data['is_verified'],
                'created_at': user_data['created_at'],
                'last_login': user_data['last_login']
            }
            
            return {
                'success': True,
                'user': user_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to get user: {str(e)}'
            }