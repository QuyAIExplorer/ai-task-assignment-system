import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration class"""
    SECRET_KEY = (os.environ.get('SECRET_KEY') or
                  'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = (os.environ.get('DATABASE_URL') or
                              'sqlite:///task_assignment.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Slack Configuration
    SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
    SLACK_APP_TOKEN = os.environ.get('SLACK_APP_TOKEN')
    SLACK_SIGNING_SECRET = os.environ.get('SLACK_SIGNING_SECRET')
    
    # Jira Configuration
    JIRA_URL = os.environ.get('JIRA_URL')
    JIRA_API_TOKEN = os.environ.get('JIRA_API_TOKEN')
    JIRA_EMAIL = os.environ.get('JIRA_EMAIL')
    JIRA_SERVER = os.environ.get('JIRA_SERVER')
    JIRA_PROJECT_KEY = os.environ.get('JIRA_PROJECT_KEY')
    
    # OpenAI Configuration
    OPENAI_API_TOKEN = os.environ.get('OPENAI_API_TOKEN')
    
    # Email Configuration
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USERNAME = (os.environ.get('SMTP_USERNAME') or
                     'nguyencongquy23012002@gmail.com')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
    
    # Gmail App Password for assignment emails
    GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 