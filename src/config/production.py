import os

class ProductionConfig:
    """Production configuration for Loginexia"""
    
    # Database configuration for MySQL
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get("MYSQL_USER", "loginexia_manus")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "#VUglDp1js?imb67")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "loginexia_db")
    
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'loginexia_production_secret_key_change_this_in_production')
    
    # API Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    OPENAI_API_BASE = os.environ.get('OPENAI_API_BASE', 'https://api.openai.com/v1')
    
    # Delivery Hero API Configuration (for production use)
    DELIVERY_HERO_API_KEY = os.environ.get('DELIVERY_HERO_API_KEY', '')
    DELIVERY_HERO_BASE_URL = os.environ.get('DELIVERY_HERO_BASE_URL', 'https://api.deliveryhero.com')
    
    # Application settings
    DEBUG = False
    TESTING = False
    
    # CORS settings
    CORS_ORIGINS = [
        'https://loginexia.com',
        'https://www.loginexia.com',
        'http://loginexia.com',
        'http://www.loginexia.com'
    ]
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/var/log/loginexia/app.log'

