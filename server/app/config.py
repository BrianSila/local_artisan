import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    
    _JWT_days = int(os.getenv("JWT_ACCESS_TOKENS_EXPIRES_DAYS", 7))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=_JWT_days)
    
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads", "artisans")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300

    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", 10))
    BUSINESS_HOURS_START = int(os.getenv("BUSINESS_HOURS_START", 8))
    BUSINESS_HOURS_END = int(os.getenv("BUSINESS_HOURS_END" ,18))
    
    MPESA_ENVIRONMENT = os.getenv("MPESA_ENVIRONMENT")
    MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
    MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
    MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE")
    MPESA_PASSKEY = os.getenv("MPESA_PASSKEY")
    MPESA_CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL")
    
    DEFAULT_ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    DEFAULT_ADMIN_NAME = os.getenv("ADMIN_NAME")
    DEFAULT_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    ALLOW_WEAK_ADMIN_SEED = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ALLOW_WEAK_ADMIN_SEED = True
    DEFAULT_ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    DEFAULT_ADMIN_NAME = os.getenv("ADMIN_NAME")
    DEFAULT_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://developer:dev2026@localhost:5432/artisan_db",
    )


class StagingConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/1")


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.getenv("REDIS_URL")


config_by_name = {
    "development": DevelopmentConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
}