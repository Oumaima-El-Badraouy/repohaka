from flask import Flask, g, jsonify
from flask_cors import CORS
import os

def create_app(config_name=None):
    """Application factory pattern."""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from app.config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    from app.extensions import mongo, jwt, limiter, celery

    mongo.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    # Register JWTManager callbacks to ensure JWT related errors return
    # consistent JSON responses (avoids silent 422 responses from default handlers)
    @jwt.unauthorized_loader
    def _jwt_unauthorized_callback(reason):
        app.logger.warning(f"JWT unauthorized: {reason} - auth={getattr(g, 'auth_header', None)} - req={getattr(g, 'request_id', None)}")
        return jsonify({
            'success': False,
            'message': 'Missing Authorization token',
            'detail': reason,
            'request_id': getattr(g, 'request_id', None)
        }), 401

    @jwt.invalid_token_loader
    def _jwt_invalid_token_callback(reason):
        app.logger.warning(f"JWT invalid token: {reason} - auth={getattr(g, 'auth_header', None)} - req={getattr(g, 'request_id', None)}")
        return jsonify({
            'success': False,
            'message': 'Invalid token',
            'detail': reason,
            'request_id': getattr(g, 'request_id', None)
        }), 401

    @jwt.expired_token_loader
    def _jwt_expired_token_callback(jwt_header, jwt_payload):
        app.logger.warning(f"JWT expired token - auth={getattr(g, 'auth_header', None)} - req={getattr(g, 'request_id', None)}")
        return jsonify({
            'success': False,
            'message': 'Token has expired',
            'request_id': getattr(g, 'request_id', None)
        }), 401

    @jwt.revoked_token_loader
    def _jwt_revoked_token_callback(jwt_header, jwt_payload):
        app.logger.warning(f"JWT revoked token - auth={getattr(g, 'auth_header', None)} - req={getattr(g, 'request_id', None)}")
        return jsonify({
            'success': False,
            'message': 'Token has been revoked',
            'request_id': getattr(g, 'request_id', None)
        }), 401

    @jwt.needs_fresh_token_loader
    def _jwt_needs_fresh_token_callback(jwt_header, jwt_payload):
        app.logger.warning(f"JWT needs fresh token - auth={getattr(g, 'auth_header', None)} - req={getattr(g, 'request_id', None)}")
        return jsonify({
            'success': False,
            'message': 'Fresh token required',
            'request_id': getattr(g, 'request_id', None)
        }), 401
    
    # Configure Celery
    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND'],
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
    )
    
    # Enable CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Register blueprints
    from app.views.auth_bp import auth_bp
    from app.views.student_bp import student_bp
    from app.views.tutor_bp import tutor_bp
    from app.views.admin_bp import admin_bp
    from app.views.ai_bp import ai_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(student_bp, url_prefix='/api/students')
    app.register_blueprint(tutor_bp, url_prefix='/api/tutors')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    
    # Register middleware
    from app.middlewares import register_middlewares
    register_middlewares(app)

    # JWT error handlers: provide clear JSON responses instead of default 422
    from flask_jwt_extended.exceptions import NoAuthorizationError, JWTExtendedException
    
    @app.errorhandler(NoAuthorizationError)
    def handle_no_authorization(error):
        app.logger.warning(f"JWT NoAuthorizationError: {error} - auth={getattr(g, 'auth_header', None)} - req={getattr(g, 'request_id', None)}")
        return ({
            'success': False,
            'message': 'Missing Authorization token',
            'request_id': getattr(g, 'request_id', None)
        }, 401)

    @app.errorhandler(JWTExtendedException)
    def handle_jwt_errors(error):
        # Capture and log masked auth header to help debugging invalid tokens
        app.logger.warning(f"JWT error: {error} - auth={getattr(g, 'auth_header', None)} - req={getattr(g, 'request_id', None)}")
        return ({
            'success': False,
            'message': 'Invalid or expired token',
            'detail': str(error),
            'request_id': getattr(g, 'request_id', None)
        }, 401)
    
    # Socket.IO and Redis removed: real-time socket events disabled
    
    return app

# Import for Celery worker
from app.extensions import celery