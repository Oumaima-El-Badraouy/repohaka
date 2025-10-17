from flask import Blueprint, request, jsonify, g
from app.utils.helpers import jwt_current_user
from app.controllers.ai_controller import AIController
from app.middlewares import require_verified_student, validate_json, log_user_action
from app.extensions import limiter
from app.tasks.ai_tasks import generate_summary_task, generate_quiz_task

ai_bp = Blueprint('ai', __name__)

# Lazy AI controller initialization to ensure app context is available
ai_controller = None

def get_ai_controller():
    global ai_controller
    if ai_controller is None:
        ai_controller = AIController()
    return ai_controller

@ai_bp.route('/chat', methods=['POST'])
@require_verified_student
@limiter.limit("50 per hour")
@validate_json(required_fields=['message'])
@log_user_action('ai_chat')
def chat():
    """Send message to AI tutor."""
    try:
        current_user = jwt_current_user()
        user_id = current_user.get('user_id') if current_user else None
        
        data = g.json_data
        message = data['message']
        chat_id = data.get('chat_id')
        
        # Create new chat if no chat_id provided
        if not chat_id:
            chat_result = get_ai_controller().create_chat(user_id)
            if not chat_result['success']:
                return jsonify(chat_result), 400
            chat_id = chat_result['chat_id']
        
        # Process AI chat
        result = get_ai_controller().chat_with_ai(user_id, chat_id, message)
        
        # Add chat_id to response
        if result['success']:
            result['chat_id'] = chat_id
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Chat failed: {str(e)}'
        }), 500

@ai_bp.route('/chats', methods=['GET'])
@require_verified_student
def get_chats():
    """Get user's chat history."""
    try:
        current_user = jwt_current_user()
        user_id = current_user.get('user_id') if current_user else None
        
        result = get_ai_controller().get_user_chats(user_id)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get chats: {str(e)}'
        }), 500

@ai_bp.route('/chats', methods=['POST'])
@require_verified_student
@validate_json()
@log_user_action('create_chat')
def create_chat():
    """Create a new chat session."""
    try:
        current_user = jwt_current_user()
        user_id = current_user.get('user_id') if current_user else None
        
        data = g.json_data
        title = data.get('title', 'New Chat')
        
        result = get_ai_controller().create_chat(user_id, title)
        
        status_code = 201 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to create chat: {str(e)}'
        }), 500

@ai_bp.route('/summary/<chat_id>', methods=['POST'])
@require_verified_student
@limiter.limit("10 per hour")
@log_user_action('request_summary')
def request_summary(chat_id):
    """Request AI-generated summary of chat."""
    try:
        current_user = jwt_current_user()
        user_id = current_user.get('user_id') if current_user else None
        
        # Verify chat ownership
        from app.models.chat import Chat
        chat_data = Chat.find_by_id(chat_id)
        if not chat_data or str(chat_data['user_id']) != user_id:
            return jsonify({
                'success': False,
                'message': 'Chat not found or access denied'
            }), 404
        
        # Start async summary generation
        task = generate_summary_task.delay(chat_id)
        
        return jsonify({
            'success': True,
            'message': 'Summary generation started',
            'task_id': task.id,
            'chat_id': chat_id
        }), 202
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to request summary: {str(e)}'
        }), 500

@ai_bp.route('/quiz/<chat_id>', methods=['POST'])
@require_verified_student
@limiter.limit("5 per hour")
@validate_json()
@log_user_action('request_quiz')
def request_quiz(chat_id):
    """Request AI-generated quiz based on chat content."""
    try:
        current_user = jwt_current_user()
        user_id = current_user.get('user_id') if current_user else None
        
        # Verify chat ownership
        from app.models.chat import Chat
        chat_data = Chat.find_by_id(chat_id)
        if not chat_data or str(chat_data['user_id']) != user_id:
            return jsonify({
                'success': False,
                'message': 'Chat not found or access denied'
            }), 404
        
        data = g.json_data
        topic = data.get('topic')  # Optional topic focus
        
        # Start async quiz generation
        task = generate_quiz_task.delay(chat_id, topic)
        
        return jsonify({
            'success': True,
            'message': 'Quiz generation started',
            'task_id': task.id,
            'chat_id': chat_id,
            'topic': topic
        }), 202
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to request quiz: {str(e)}'
        }), 500

@ai_bp.route('/task/<task_id>', methods=['GET'])
@require_verified_student
def get_task_result(task_id):
    """Get result of async task."""
    try:
        from app.extensions import celery
        
        task = celery.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'success': True,
                'state': task.state,
                'status': 'Task is waiting to be processed'
            }
        elif task.state == 'PROGRESS':
            response = {
                'success': True,
                'state': task.state,
                'status': task.info.get('status', 'Processing...'),
                'progress': task.info.get('progress', 0)
            }
        elif task.state == 'SUCCESS':
            response = {
                'success': True,
                'state': task.state,
                'result': task.result
            }
        else:  # FAILURE
            response = {
                'success': False,
                'state': task.state,
                'error': str(task.info)
            }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get task result: {str(e)}'
        }), 500

@ai_bp.route('/rate', methods=['POST'])
@require_verified_student
@validate_json(required_fields=['message_id', 'rating'])
@log_user_action('rate_ai_response')
def rate_response():
    """Rate an AI response."""
    try:
        current_user = jwt_current_user()
        user_id = current_user.get('user_id') if current_user else None
        
        data = g.json_data
        message_id = data['message_id']
        rating = data['rating']
        feedback = data.get('feedback')
        
        from app.controllers.student_controller import StudentController
        result = StudentController.rate_ai_response(user_id, message_id, rating, feedback)
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to rate response: {str(e)}'
        }), 500