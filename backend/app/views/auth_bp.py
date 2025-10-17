from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required
from app.utils.helpers import jwt_current_user
from app.controllers.auth_controller import AuthController
from app.middlewares import validate_json, log_user_action
from app.extensions import limiter

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
@validate_json(required_fields=['email', 'password', 'name', 'school', 'student_id'])
@log_user_action('student_registration')
def register():
    """Register a new student."""
    try:
        data = g.json_data
        result = AuthController.register_student(data)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Registration failed: {str(e)}'
        }), 500

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
@validate_json(required_fields=['email', 'password'])
@log_user_action('user_login')
def login():
    """Authenticate user and return tokens."""
    try:
        data = g.json_data
        result = AuthController.login(data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Login failed: {str(e)}'
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@limiter.limit("20 per minute")
def refresh():
    """Refresh access token."""
    try:
        result = AuthController.refresh_token()
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Token refresh failed: {str(e)}'
        }), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information."""
    try:
        current_user = jwt_current_user()
        user_id = current_user.get('user_id') if current_user else None
        
        result = AuthController.get_current_user(user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get user info: {str(e)}'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
@log_user_action('user_logout')
def logout():
    """Logout user (client should discard tokens)."""
    try:
        # In a more advanced implementation, you would blacklist the token
        # For now, we just return a success message
        # The client should discard the tokens
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Logout failed: {str(e)}'
        }), 500

@auth_bp.route('/check-email', methods=['POST'])
@limiter.limit("20 per minute")
@validate_json(required_fields=['email'])
def check_email():
    """Check if email is already registered."""
    try:
        from app.models.user import User
        
        email = g.json_data['email']
        exists = User.email_exists(email)
        
        return jsonify({
            'success': True,
            'email_exists': exists
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Email check failed: {str(e)}'
        }), 500