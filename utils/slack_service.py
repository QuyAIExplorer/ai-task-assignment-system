from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import current_app, request
import re
import json
from utils.task_intent_detector import TaskIntentDetector
from utils.jira_service import JiraService
from models.database import db, Task, Employee
from datetime import datetime


class SlackService:
    """Enhanced Slack service for monitoring messages and task detection"""
    
    def __init__(self):
        self.app = App(
            token=current_app.config['SLACK_BOT_TOKEN'],
            signing_secret=current_app.config['SLACK_SIGNING_SECRET']
        )
        self.handler = SlackRequestHandler(self.app)
        self.intent_detector = TaskIntentDetector()
        self.jira_service = JiraService()
        
        # Register event handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register Slack event handlers"""
        
        # Handle slash commands
        @self.app.command("/task")
        def handle_task_command(ack, command):
            """Handle /task slash command"""
            ack()
            self._process_task_command(command)
        
        @self.app.command("/bug")
        def handle_bug_command(ack, command):
            """Handle /bug slash command"""
            ack()
            self._process_bug_command(command)
        
        @self.app.command("/story")
        def handle_story_command(ack, command):
            """Handle /story slash command"""
            ack()
            self._process_story_command(command)
        
        # Handle message events
        @self.app.message(re.compile(r".*"))
        def handle_message(message, say):
            """Handle incoming messages and detect task intents"""
            try:
                # Skip bot messages
                if message.get('bot_id'):
                    return
                
                text = message.get('text', '')
                user_id = message.get('user')
                channel_id = message.get('channel')
                
                # Check for command-based parsing first
                if self._is_command_based_message(text):
                    self._process_command_based_message(text, user_id, channel_id, say)
                    return
                
                # Use AI detection for regular messages
                if self._should_process_message(text):
                    self._process_ai_detected_message(text, user_id, channel_id, say)
                    
            except Exception as e:
                current_app.logger.error(f"Error handling Slack message: {str(e)}")
        
        @self.app.event("app_mention")
        def handle_mention(event, say):
            """Handle bot mentions"""
            try:
                text = event.get('text', '')
                user_id = event.get('user')
                
                # Remove bot mention from text
                text = re.sub(r'<@[A-Z0-9]+>', '', text).strip()
                
                if text.lower() in ['help', 'status', 'tasks']:
                    say("I can help you with task management! Use commands like `/task`, `/bug`, `/story` or mention me with task requests.")
                else:
                    # Process the mentioned text as a potential task
                    self._process_ai_detected_message(text, user_id, event.get('channel'), say)
                    
            except Exception as e:
                current_app.logger.error(f"Error handling mention: {str(e)}")
    
    def _is_command_based_message(self, text):
        """Check if message starts with command prefixes"""
        command_prefixes = ['!bug', '!story', '!task', '!incident', '!feature']
        return any(text.lower().startswith(prefix) for prefix in command_prefixes)
    
    def _should_process_message(self, text):
        """Determine if a message should be processed for task detection"""
        # Skip very short messages or obvious non-tasks
        if len(text.strip()) < 10:
            return False
        
        # Skip common non-task patterns
        non_task_patterns = [
            r'^(hi|hello|hey|good morning|good afternoon|good evening)',
            r'^(thanks|thank you|thx)',
            r'^(ok|okay|sure|yes|no)',
            r'^(lol|haha|:)',
            r'^(how are you|how\'s it going)',
            r'^(bye|goodbye|see you)'
        ]
        
        text_lower = text.lower().strip()
        for pattern in non_task_patterns:
            if re.match(pattern, text_lower):
                return False
        
        return True
    
    def _process_command_based_message(self, text, user_id, channel_id, say):
        """Process messages with command prefixes"""
        text_lower = text.lower()
        
        if text_lower.startswith('!bug'):
            self._create_ticket_from_command(text, 'bug', user_id, channel_id, say)
        elif text_lower.startswith('!story'):
            self._create_ticket_from_command(text, 'story', user_id, channel_id, say)
        elif text_lower.startswith('!task'):
            self._create_ticket_from_command(text, 'task', user_id, channel_id, say)
        elif text_lower.startswith('!incident'):
            self._create_ticket_from_command(text, 'incident', user_id, channel_id, say)
        elif text_lower.startswith('!feature'):
            self._create_ticket_from_command(text, 'feature', user_id, channel_id, say)
    
    def _process_ai_detected_message(self, text, user_id, channel_id, say):
        """Process messages using AI detection"""
        try:
            # Use OpenAI GPT to detect if it's actionable
            task_type = self.intent_detector.detect_task_type(text)
            
            if task_type:
                # Extract task details using GPT
                task_details = self.intent_detector.extract_task_details(text)
                
                if task_details:
                    self._create_task_from_ai_detection(text, task_type, task_details, user_id, channel_id, say)
                else:
                    current_app.logger.warning(f"Failed to extract task details from: {text}")
            else:
                # Not actionable - ignore silently
                current_app.logger.info(f"Ignoring non-actionable message: {text[:50]}...")
                
        except Exception as e:
            current_app.logger.error(f"Error processing AI detected message: {str(e)}")
    
    def _process_task_command(self, command):
        """Process /task slash command"""
        text = command.get('text', '')
        user_id = command.get('user_id')
        channel_id = command.get('channel_id')
        
        if not text.strip():
            self._send_ephemeral_message(channel_id, user_id, 
                "Please provide a task description. Usage: `/task <description>`")
            return
        
        self._create_ticket_from_command(text, 'task', user_id, channel_id, None, command=True)
    
    def _process_bug_command(self, command):
        """Process /bug slash command"""
        text = command.get('text', '')
        user_id = command.get('user_id')
        channel_id = command.get('channel_id')
        
        if not text.strip():
            self._send_ephemeral_message(channel_id, user_id, 
                "Please provide a bug description. Usage: `/bug <description>`")
            return
        
        self._create_ticket_from_command(text, 'bug', user_id, channel_id, None, command=True)
    
    def _process_story_command(self, command):
        """Process /story slash command"""
        text = command.get('text', '')
        user_id = command.get('user_id')
        channel_id = command.get('channel_id')
        
        if not text.strip():
            self._send_ephemeral_message(channel_id, user_id, 
                "Please provide a story description. Usage: `/story <description>`")
            return
        
        self._create_ticket_from_command(text, 'story', user_id, channel_id, None, command=True)
    
    def _create_ticket_from_command(self, text, ticket_type, user_id, channel_id, say, command=False):
        """Create ticket from command-based input"""
        try:
            # Remove command prefix if present
            if text.lower().startswith(f'!{ticket_type}'):
                text = text[len(f'!{ticket_type}'):].strip()
            
            # Generate title from text
            title = self._generate_title_from_text(text, ticket_type)
            
            # Create task in database
            task = Task(
                title=title,
                description=text,
                priority=self._extract_priority(text),
                source='slack_command',
                source_id=f"{user_id}_{datetime.now().timestamp()}",
                created_by=user_id
            )
            db.session.add(task)
            db.session.commit()
            
            # Create Jira ticket
            jira_key = self._create_jira_ticket(title, text, ticket_type)
            
            # Send confirmation
            message = f"✅ Created {ticket_type}: *{title}*"
            if jira_key:
                message += f"\n🔗 Jira: {jira_key}"
            message += f"\n📝 Description: {text[:100]}{'...' if len(text) > 100 else ''}"
            
            if command:
                self._send_ephemeral_message(channel_id, user_id, message)
            else:
                say(message)
                
        except Exception as e:
            error_msg = f"❌ Failed to create {ticket_type}: {str(e)}"
            current_app.logger.error(error_msg)
            if command:
                self._send_ephemeral_message(channel_id, user_id, error_msg)
            else:
                say(error_msg)
    
    def _create_task_from_ai_detection(self, original_text, task_type, task_details, user_id, channel_id, say):
        """Create task from AI-detected actionable message"""
        try:
            title = task_details.get('title', self._generate_title_from_text(original_text, task_type))
            description = task_details.get('description', original_text)
            priority = task_details.get('priority', self._extract_priority(original_text))
            
            # Create task in database
            task = Task(
                title=title,
                description=description,
                priority=priority,
                source='slack_ai_detected',
                source_id=f"{user_id}_{datetime.now().timestamp()}",
                created_by=user_id
            )
            db.session.add(task)
            db.session.commit()
            
            # Create Jira ticket
            jira_key = self._create_jira_ticket(title, description, task_type)
            
            # Send confirmation
            message = f"🤖 AI detected {task_type}: *{title}*"
            if jira_key:
                message += f"\n🔗 Jira: {jira_key}"
            message += f"\n📝 Description: {description[:100]}{'...' if len(description) > 100 else ''}"
            
            say(message)
            
        except Exception as e:
            error_msg = f"❌ Failed to create AI-detected task: {str(e)}"
            current_app.logger.error(error_msg)
            say(error_msg)
    
    def _generate_title_from_text(self, text, task_type):
        """Generate a concise title from text"""
        # Simple title generation - first sentence or first line
        lines = text.split('\n')
        first_line = lines[0].strip()
        
        # Limit to reasonable length
        if len(first_line) > 80:
            return first_line[:77] + "..."
        
        return first_line
    
    def _extract_priority(self, text):
        """Extract priority from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['urgent', 'asap', 'emergency', 'critical', 'blocker']):
            return 'high'
        elif any(word in text_lower for word in ['low priority', 'when possible', 'no rush', 'nice to have']):
            return 'low'
        else:
            return 'medium'
    
    def _create_jira_ticket(self, title, description, issue_type):
        """Create Jira ticket and return the key"""
        try:
            # Map task types to Jira issue types
            jira_issue_type = {
                'bug': 'Bug',
                'story': 'Story',
                'task': 'Task',
                'incident': 'Incident',
                'feature': 'New Feature'
            }.get(issue_type, 'Task')
            
            # Create Jira issue
            jira_key = self.jira_service.create_issue(
                summary=title,
                description=description,
                issue_type=jira_issue_type,
                priority=self._map_priority_to_jira(self._extract_priority(description))
            )
            
            return jira_key
            
        except Exception as e:
            current_app.logger.error(f"Failed to create Jira ticket: {str(e)}")
            return None
    
    def _map_priority_to_jira(self, priority):
        """Map internal priority to Jira priority"""
        priority_map = {
            'high': 'High',
            'medium': 'Medium',
            'low': 'Low'
        }
        return priority_map.get(priority, 'Medium')
    
    def _send_ephemeral_message(self, channel_id, user_id, message):
        """Send ephemeral message to user"""
        try:
            self.app.client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text=message
            )
        except Exception as e:
            current_app.logger.error(f"Failed to send ephemeral message: {str(e)}")
    
    def send_notification(self, channel_id, message):
        """Send notification to Slack channel"""
        try:
            self.app.client.chat_postMessage(
                channel=channel_id,
                text=message
            )
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to send Slack notification: {str(e)}")
            return False
    
    def get_user_info(self, user_id):
        """Get user information from Slack"""
        try:
            response = self.app.client.users_info(user=user_id)
            if response['ok']:
                return response['user']
            return None
        except Exception as e:
            current_app.logger.error(f"Failed to get user info: {str(e)}")
            return None 