from flask import request, jsonify, g
from flask_jwt_extended import jwt_required, verify_jwt_in_request
from flask_limiter import Limiter
from functools import wraps
import logging
import traceback
from app.utils.helpers import generate_request_id, format_datetime
from datetime import datetime

def register_middlewares(app):
    """Register all middleware with the app."""
    
    # Request ID middleware
    @app.before_request
    def before_request():
        g.request_id = generate_request_id()
        g.start_time = datetime.utcnow()
        # Capture a masked version of the Authorization header for diagnostics
        try:
            auth = request.headers.get('Authorization')
            if auth:
                # keep only first/last few chars to avoid logging secrets
                g.auth_header = auth[:10] + '...' + auth[-6:] if len(auth) > 20 else auth
            else:
                g.auth_header = None
        except Exception:
            g.auth_header = None
    
    # Response middleware
    @app.after_request
    def after_request(response):
        # Add request ID to response headers
        response.headers['X-Request-ID'] = g.request_id
        
        # Add CORS headers (helpful for local development and stray clients)
        # Keep permissive for local/dev; in production you may want to tighten this.
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        
        # Log request
        duration = (datetime.utcnow() - g.start_time).total_seconds()
        app.logger.info(
            f"{request.method} {request.path} - {response.status_code} - {duration:.3f}s - {g.request_id}"
        )
        
        return response
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'message': 'Bad request',
            'error': str(error),
            'request_id': getattr(g, 'request_id', None)
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'message': 'Unauthorized access',
            'request_id': getattr(g, 'request_id', None)
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'message': 'Access forbidden',
            'request_id': getattr(g, 'request_id', None)
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Resource not found',
            'request_id': getattr(g, 'request_id', None)
        }), 404
    
    @app.errorhandler(429)
    def rate_limit_handler(error):
        return jsonify({
            'success': False,
            'message': 'Rate limit exceeded. Please try again later.',
            'request_id': getattr(g, 'request_id', None)
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal error: {str(error)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'request_id': getattr(g, 'request_id', None)
        }), 500
    
    # Global exception handler
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f"Unhandled exception: {str(error)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred',
            'request_id': getattr(g, 'request_id', None)
        }), 500

def require_role(required_role):
    """Decorator to require specific user role."""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            from app.utils.helpers import jwt_current_user
            current_user = jwt_current_user()
            
            if not current_user or current_user.get('role') != required_role:
                return jsonify({
                    'success': False,
                    'message': f'Access denied. {required_role.title()} role required.'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_verified_student(f):
    """Decorator to require verified student."""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        from app.utils.helpers import jwt_current_user
        current_user = jwt_current_user()

        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401

        if current_user.get('role') != 'student':
            return jsonify({
                'success': False,
                'message': 'Student access required'
            }), 403

        # Additional verification check could be added here
        # For now, we rely on JWT creation logic to only create tokens for verified students

        return f(*args, **kwargs)

    return decorated_function

def optional_auth(f):
    """Decorator for optional authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
            from app.utils.helpers import jwt_current_user
            current_user = jwt_current_user()
        except:
            current_user = None
        
        g.current_user = current_user
        return f(*args, **kwargs)
    return decorated_function

def validate_json(required_fields=None, optional_fields=None):
    """Decorator to validate JSON request data."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Try to obtain JSON robustly. Some clients send slightly different
            # Content-Type headers (e.g. with charset) or forget the header.
            data = None
            try:
                # Preferred: rely on Flask parsing when possible
                data = request.get_json(silent=True)
            except Exception:
                data = None

            # If Flask couldn't parse JSON, try to parse raw body as fallback
            if data is None:
                try:
                    raw = request.get_data(as_text=True)
                    if raw:
                        import json
                        data = json.loads(raw)
                except Exception as ex:
                    # parsing failed; leave data as None and log details
                    logging.debug(f"validate_json: raw body parse failed: {ex}")

            if data is None:
                # Log request headers and body for easier debugging
                try:
                    raw_body = request.get_data(as_text=True)
                except Exception:
                    raw_body = '<unreadable body>'

                logging.warning(
                    f"Invalid JSON request: path={request.path} headers={dict(request.headers)} body={raw_body}"
                )

                return jsonify({
                    'success': False,
                    'message': 'Invalid or missing JSON data',
                    'hint': 'Ensure Content-Type: application/json and a valid JSON body',
                    'request_path': request.path
                }), 400
            
            # Check required fields
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        'success': False,
                        'message': f'Missing required fields: {", ".join(missing_fields)}'
                    }), 400
            
            # Store validated data in g for use in the route
            g.json_data = data
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_user_action(action):
    """Decorator to log user actions."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Try to verify JWT if present (optional). If no valid JWT, proceed as anonymous.
            try:
                verify_jwt_in_request(optional=True)
                from app.utils.helpers import jwt_current_user
                current_user = jwt_current_user()
            except Exception:
                current_user = None

            # expose current user to handlers via g
            g.current_user = current_user
            user_id = current_user.get('user_id') if current_user else 'anonymous'

            # Log the action
            logging.info(
                f"User action: {action} - User: {user_id} - Request: {getattr(g, 'request_id', None)}"
            )

            result = f(*args, **kwargs)

            # Log the result
            try:
                status = result.status_code
            except Exception:
                status = 200  # Assume success if no status code

            logging.info(
                f"Action result: {action} - User: {user_id} - Status: {status} - Request: {getattr(g, 'request_id', None)}"
            )

            return result
        return decorated_function
    return decorator