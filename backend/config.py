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

    # SMTP / contact form
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    SMTP_USE_TLS = (os.getenv('SMTP_USE_TLS', 'true').lower() in ('1', 'true', 'yes'))
    CONTACT_RECIPIENT = os.getenv('CONTACT_RECIPIENT')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(os.getenv('DATABASE_URL'))
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
