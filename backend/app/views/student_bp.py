from flask import Blueprint, request, jsonify, g
from app.utils.helpers import jwt_current_user
from app.controllers.student_controller import StudentController
from app.controllers.tutor_controller import TutorController
from app.middlewares import require_verified_student, validate_json, log_user_action
from app.extensions import limiter
from app.utils.helpers import safe_int

student_bp = Blueprint('students', __name__)

@student_bp.route('/me', methods=['GET'])
@require_verified_student
def get_profile():
    """Get student profile with statistics."""
    try:
        current_user = jwt_current_user()
        user_id = current_user.get('user_id') if current_user else None

        result = StudentController.get_profile(user_id)

        status_code = 200 if result['success'] else 404
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get profile: {str(e)}'
        }), 500

@student_bp.route('/chats', methods=['GET'])
@require_verified_student
def get_chat_history():
    """Get student's chat history."""
    try:
        current_user = jwt_current_user()
        user_id = current_user.get('user_id') if current_user else None

        # Get query parameters
        chat_id = request.args.get('chat_id')
        page = safe_int(request.args.get('page', 1), 1)
        per_page = min(safe_int(request.args.get('per_page', 50), 50), 100)

        result = StudentController.get_chat_history(user_id, chat_id, page, per_page)

        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get chat history: {str(e)}'
        }), 500

@student_bp.route('/chats/<chat_id>', methods=['DELETE'])
@require_verified_student
@log_user_action('delete_chat')
def delete_chat(chat_id):
    """Delete a chat."""
    try:
        current_user = jwt_current_user()
        user_id = current_user.get('user_id') if current_user else None

        result = StudentController.delete_chat(user_id, chat_id)

        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to delete chat: {str(e)}'
        }), 500

@student_bp.route('/chats/<chat_id>/title', methods=['PUT'])
@require_verified_student
@validate_json(required_fields=['title'])
@log_user_action('update_chat_title')
def update_chat_title(chat_id):
    """Update chat title."""
    try:
        current_user = jwt_current_user()
        user_id = current_user.get('user_id') if current_user else None

        data = g.json_data
        title = data['title']

        result = StudentController.update_chat_title(user_id, chat_id, title)

        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to update chat title: {str(e)}'
        }), 500

@student_bp.route('/search', methods=['GET'])
@require_verified_student
@limiter.limit("30 per minute")
def search_messages():
    """Search student's messages."""
    try:
        current_user = jwt_current_user()
        user_id = current_user.get('user_id') if current_user else None

        query = request.args.get('q', '').strip()
        limit = min(safe_int(request.args.get('limit', 20), 20), 50)

        if not query:
            return jsonify({
                'success': False,
                'message': 'Search query is required'
            }), 400

        result = StudentController.search_messages(user_id, query, limit)

        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Search failed: {str(e)}'
        }), 500

@student_bp.route('/tutors/recommended', methods=['GET'])
@require_verified_student
def get_recommended_tutors():
    """Get recommended tutors for student."""
    try:
        current_user = jwt_current_user()
        user_id = current_user.get('user_id') if current_user else None

        # Get query parameters
        subjects = request.args.getlist('subjects')  # Can pass multiple subjects
        limit = min(safe_int(request.args.get('limit', 5), 5), 20)

        result = StudentController.get_recommended_tutors(user_id, subjects, limit)

        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get recommendations: {str(e)}'
        }), 500

@student_bp.route('/tutors', methods=['GET'])
@require_verified_student
def get_tutors():
    """Get tutors with optional filtering."""
    try:
        # Get query parameters for filtering
        school = request.args.get('school')
        min_gpa = request.args.get('min_gpa')
        subjects = request.args.getlist('subjects')
        max_rate = request.args.get('max_rate')
        sort_by = request.args.get('sort_by', 'gpa')

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

        if subjects or school or min_gpa or max_rate:
            # Use search with filters
            result = TutorController.search_tutors(
                school=school,
                min_gpa=min_gpa,
                subjects=subjects,
                max_rate=max_rate
            )
        else:
            # Get top tutors
            limit = min(safe_int(request.args.get('limit', 10), 10), 50)
            result = TutorController.get_top_tutors(limit, sort_by)

        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get tutors: {str(e)}'
        }), 500

@student_bp.route('/tutors/<tutor_id>', methods=['GET'])
@require_verified_student
def get_tutor_details(tutor_id):
    """Get specific tutor details."""
    try:
        result = TutorController.get_tutor_by_id(tutor_id)

        status_code = 200 if result['success'] else 404
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get tutor details: {str(e)}'
        }), 500

@student_bp.route('/subjects', methods=['GET'])
@require_verified_student
def get_available_subjects():
    """Get all available subjects from tutors."""
    try:
        result = TutorController.get_available_subjects()

        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get subjects: {str(e)}'
        }), 500

@student_bp.route('/update', methods=['PUT'])
@require_verified_student
@validate_json(required_fields=['name', 'email', 'school'])
@log_user_action('update_student_profile')
def update_student_profile():
    """Update student profile (name, email, school)."""
    try:
        current_user = jwt_current_user()
        user_id = current_user.get('user_id') if current_user else None

        if not user_id:
            return jsonify({
                'success': False,
                'message': 'Unauthorized'
            }), 401

        data = g.json_data
        from app.controllers.student_controller import StudentController
        result = StudentController.update_profile(user_id, data)

        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to update student profile: {str(e)}'
        }), 500