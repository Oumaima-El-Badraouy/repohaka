from flask import Blueprint, request, jsonify
from app.controllers.tutor_controller import TutorController
from app.middlewares import optional_auth
from app.utils.helpers import safe_int

tutor_bp = Blueprint('tutors', __name__)

@tutor_bp.route('/', methods=['GET'])
@optional_auth
def get_all_tutors():
    """Get all tutors (public endpoint with optional auth)."""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        result = TutorController.get_all_tutors(active_only)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get tutors: {str(e)}'
        }), 500

@tutor_bp.route('/<tutor_id>', methods=['GET'])
@optional_auth
def get_tutor_details(tutor_id):
    """Get specific tutor details (public endpoint)."""
    try:
        result = TutorController.get_tutor_by_id(tutor_id)
        
        status_code = 200 if result['success'] else 404
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get tutor: {str(e)}'
        }), 500

@tutor_bp.route('/search', methods=['GET'])
@optional_auth
def search_tutors():
    """Search tutors with filters (public endpoint)."""
    try:
        # Get query parameters
        school = request.args.get('school')
        min_gpa = request.args.get('min_gpa')
        subjects = request.args.getlist('subjects')
        max_rate = request.args.get('max_rate')
        
        # Convert types
        if min_gpa:
            try:
                min_gpa = float(min_gpa)
            except ValueError:
                min_gpa = None
        
        if max_rate:
            try:
                max_rate = float(max_rate)
            except ValueError:
                max_rate = None
        
        result = TutorController.search_tutors(
            school=school,
            min_gpa=min_gpa,
            subjects=subjects,
            max_rate=max_rate
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Search failed: {str(e)}'
        }), 500

@tutor_bp.route('/by-subjects', methods=['GET'])
@optional_auth
def get_tutors_by_subjects():
    """Get tutors by specific subjects (public endpoint)."""
    try:
        subjects = request.args.getlist('subjects')
        limit = min(safe_int(request.args.get('limit', 10), 10), 50)
        
        if not subjects:
            return jsonify({
                'success': False,
                'message': 'At least one subject is required'
            }), 400
        
        result = TutorController.get_tutors_by_subjects(subjects, limit)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get tutors by subjects: {str(e)}'
        }), 500

@tutor_bp.route('/top', methods=['GET'])
@optional_auth
def get_top_tutors():
    """Get top tutors (public endpoint)."""
    try:
        limit = min(safe_int(request.args.get('limit', 10), 10), 50)
        sort_by = request.args.get('sort_by', 'gpa')
        
        # Validate sort_by parameter
        valid_sort_options = ['gpa', 'rating', 'sessions']
        if sort_by not in valid_sort_options:
            sort_by = 'gpa'
        
        result = TutorController.get_top_tutors(limit, sort_by)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get top tutors: {str(e)}'
        }), 500

@tutor_bp.route('/subjects', methods=['GET'])
@optional_auth
def get_available_subjects():
    """Get all available subjects (public endpoint)."""
    try:
        result = TutorController.get_available_subjects()
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get subjects: {str(e)}'
        }), 500