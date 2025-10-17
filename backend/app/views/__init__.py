# Views package
from .auth_bp import auth_bp
from .student_bp import student_bp
from .tutor_bp import tutor_bp
from .admin_bp import admin_bp
from .ai_bp import ai_bp

__all__ = ['auth_bp', 'student_bp', 'tutor_bp', 'admin_bp', 'ai_bp']