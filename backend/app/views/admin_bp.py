from flask import Blueprint, request, jsonify, g
from app.utils.helpers import jwt_current_user
from app.controllers.admin_controller import AdminController
from app.middlewares import require_role, validate_json, log_user_action
from app.extensions import limiter
from app.utils.helpers import safe_int

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/students/pending', methods=['GET'])
@require_role('admin')
def get_pending_students():
    """Get students pending verification."""
    try:
        result = AdminController.get_pending_students()
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get pending students: {str(e)}'
        }), 500

@admin_bp.route('/students/<student_id>/verify', methods=['POST'])
@require_role('admin')
@log_user_action('verify_student')
def verify_student(student_id):
    """Verify a student account."""
    try:
        result = AdminController.verify_student(student_id)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to verify student: {str(e)}'
        }), 500

@admin_bp.route('/users', methods=['GET'])
@require_role('admin')
def get_all_users():
    """Get paginated list of all users."""
    try:
        page = safe_int(request.args.get('page', 1), 1)
        per_page = min(safe_int(request.args.get('per_page', 20), 20), 100)
        
        result = AdminController.get_all_users(page, per_page)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get users: {str(e)}'
        }), 500

@admin_bp.route('/tutors', methods=['GET'])
@require_role('admin')
def get_all_tutors():
    """Get list of all tutors."""
    try:
        result = AdminController.get_all_tutors()
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get tutors: {str(e)}'
        }), 500

@admin_bp.route('/tutors', methods=['POST'])
@require_role('admin')
@validate_json(required_fields=['name', 'subjects', 'hourly_rate', 'school', 'gpa', 'contact_info'])
@log_user_action('add_tutor')
def add_tutor():
    """Add a new tutor."""
    try:
        current_user = jwt_current_user()
        admin_id = current_user.get('user_id') if current_user else None
        
        data = g.json_data
        result = AdminController.add_tutor(admin_id, data)
        
        status_code = 201 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to add tutor: {str(e)}'
        }), 500

@admin_bp.route('/stats', methods=['GET'])
@require_role('admin')
def get_platform_stats():
    """Get platform statistics."""
    try:
        result = AdminController.get_platform_stats()
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get platform stats: {str(e)}'
        }), 500

@admin_bp.route('/activity', methods=['GET'])
@require_role('admin')
def get_recent_activity():
    """Get recent platform activity."""
    try:
        limit = min(safe_int(request.args.get('limit', 50), 50), 200)
        
        result = AdminController.get_recent_activity(limit)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get recent activity: {str(e)}'
        }), 500
@admin_bp.route('/me', methods=['GET'])
@require_role('admin')
def get_admin_profile():
    """Get admin profile with statistics."""
    try:
        current_user = jwt_current_user()
        admin_id = current_user.get('user_id') if current_user else None

        result = AdminController.get_profile(admin_id)

        status_code = 200 if result['success'] else 404
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get admin profile: {str(e)}'
        }), 500
@admin_bp.route('/update', methods=['PUT'])
@require_role('admin')
@validate_json(required_fields=['name', 'email', 'school'])
@log_user_action('update_admin_profile')
def update_admin_profile():
    """Update admin profile (name, email, school)."""
    try:
        current_user = jwt_current_user()
        admin_id = current_user.get('user_id') if current_user else None
        
        if not admin_id:
            return jsonify({
                'success': False,
                'message': 'Unauthorized'
            }), 401

        data = g.json_data
        result = AdminController.update_profile(admin_id, data)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to update admin profile: {str(e)}'
        }), 500

@admin_bp.route('/tutors/<tutor_id>/deactivate', methods=['POST'])
@require_role('admin')
@log_user_action('deactivate_tutor')
def deactivate_tutor(tutor_id):
    """Deactivate a tutor."""
    try:
        from app.extensions import mongo
        from bson import ObjectId
        
        result = mongo.db.tutors.update_one(
            {'_id': ObjectId(tutor_id)},
            {'$set': {'is_active': False}}
        )
        
        if result.modified_count > 0:
            return jsonify({
                'success': True,
                'message': 'Tutor deactivated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Tutor not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to deactivate tutor: {str(e)}'
        }), 500

@admin_bp.route('/tutors/<tutor_id>/activate', methods=['POST'])
@require_role('admin')
@log_user_action('activate_tutor')
def activate_tutor(tutor_id):
    """Activate a tutor."""
    try:
        from app.extensions import mongo
        from bson import ObjectId
        
        result = mongo.db.tutors.update_one(
            {'_id': ObjectId(tutor_id)},
            {'$set': {'is_active': True}}
        )
        
        if result.modified_count > 0:
            return jsonify({
                'success': True,
                'message': 'Tutor activated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Tutor not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to activate tutor: {str(e)}'
        }), 500

@admin_bp.route('/maintenance/cleanup', methods=['POST'])
@require_role('admin')
@limiter.limit("1 per hour")
@log_user_action('manual_cleanup')
def manual_cleanup():
    """Manually trigger cleanup tasks."""
    try:
        from app.tasks.ai_tasks import cleanup_old_chats_task
        
        task = cleanup_old_chats_task.delay()
        
        return jsonify({
            'success': True,
            'message': 'Cleanup task started',
            'task_id': task.id
        }), 202
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to start cleanup: {str(e)}'
        }), 500