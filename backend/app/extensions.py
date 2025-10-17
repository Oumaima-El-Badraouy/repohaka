from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
# Socket.IO removed — real-time features deprecated
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from celery import Celery
import logging

# Initialize extensions
mongo = PyMongo()
jwt = JWTManager()
socketio = None  # kept for backwards compatibility if referenced; do not use
redis_client = None
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Celery
celery = Celery(__name__)