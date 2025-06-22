from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_migrate import Migrate
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import config
from models.database import db
from utils.slack_service import SlackService
from utils.jira_service import JiraService
from utils.email_service import EmailService
from agents.task_assignment_agent import TaskAssignmentAgent


def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    Migrate(app, db)
    
    # Initialize services
    slack_service = SlackService()
    jira_service = JiraService()
    email_service = EmailService()
    task_agent = TaskAssignmentAgent()
    
    # Register blueprints
    from backend.routes import api_bp, web_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(web_bp)
    
    # Slack event endpoint
    @app.route('/slack/events', methods=['POST'])
    def slack_events():
        """Handle Slack events"""
        return slack_service.handler.handle(request)
    
    # Health check
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy'})
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000) 