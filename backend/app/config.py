import os
from datetime import timedelta

class Config:
    """Base configuration class."""
    
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Database
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/learning_platform')
    
    # Redis removed — no default Redis URL
    REDIS_URL = None
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 1)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 30)))
    JWT_ALGORITHM = 'HS256'
    
    # API Configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Rate limiting (in-memory or extension configured elsewhere)
    RATELIMIT_DEFAULT = "100 per hour"
    
    # Celery Configuration (not configured by default — set via environment if used)
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
    
    # File upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # CORS
    CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    
class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    MONGO_URI = 'mongodb://localhost:27017/learning_platform_test'
    
class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Add production-specific settings
    
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}