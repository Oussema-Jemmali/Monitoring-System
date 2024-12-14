import os
from datetime import timedelta

class Config:
    SECRET_KEY = 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_REGISTRATION_CODE = 'admin123'  # This is the secret code for admin registration
    
    # Monitoring settings
    PING_INTERVAL = 60  # seconds
    SSH_TIMEOUT = 10    # seconds
    MAX_RETRIES = 3
    
    # Admin settings
    ADMIN_CODE = 'admin123'  # Change this in production!
    
    # Security settings
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # Email configuration for alerts
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Monitoring thresholds
    CPU_THRESHOLD = 80  # percentage
    MEMORY_THRESHOLD = 80  # percentage
    DISK_THRESHOLD = 90  # percentage
