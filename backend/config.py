import os
from datetime import timedelta


def _normalize_database_url(url: str | None) -> str | None:
    if not url:
        return url
    if url.startswith('postgres://'):
        return 'postgresql://' + url[len('postgres://') :]
    return url


class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(
        os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/skill_certification')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # Admin credentials
    ADMIN_EMAIL = 'admin@skilltest.com'
    ADMIN_PASSWORD = 'admin123'  # Will be hashed in production

    # EmailJS configuration (preferred)
    EMAILJS_SERVICE_ID = os.getenv('EMAILJS_SERVICE_ID')
    EMAILJS_TEMPLATE_ID = os.getenv('EMAILJS_TEMPLATE_ID')
    EMAILJS_PUBLIC_KEY = os.getenv('EMAILJS_PUBLIC_KEY')
    EMAILJS_PRIVATE_KEY = os.getenv('EMAILJS_PRIVATE_KEY')
    EMAILJS_ORIGIN = os.getenv('EMAILJS_ORIGIN', 'http://localhost')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(os.getenv('DATABASE_URL'))
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
