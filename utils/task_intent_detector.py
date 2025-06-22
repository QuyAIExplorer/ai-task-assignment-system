import openai
from flask import current_app
import re


class TaskIntentDetector:
    """Enhanced task intent detector using OpenAI GPT"""
    
    def __init__(self):
        openai.api_key = current_app.config['OPENAI_API_TOKEN']
    
    def detect_task_intent(self, text):
        """Detect if text contains a task request (legacy method)"""
        return self.detect_task_type(text) is not None
    
    def detect_task_type(self, text):
        """Detect the type of actionable item in the text"""
        try:
            # Simple keyword-based detection first
            task_type = self._simple_task_type_detection(text)
            if task_type:
                return task_type
            
            # Use GPT for more sophisticated detection
            return self._gpt_task_type_detection(text)
            
        except Exception as e:
            current_app.logger.error(f"Error in task type detection: {str(e)}")
            return None
    
    def _simple_task_type_detection(self, text):
        """Simple keyword-based task type detection"""
        text_lower = text.lower()
        
        # Bug-related keywords
        bug_keywords = [
            'bug', 'error', 'broken', 'not working', 'fails', 'crash', 'exception',
            'issue', 'problem', 'defect', 'glitch', 'malfunction', 'doesn\'t work'
        ]
        
        # Feature request keywords
        feature_keywords = [
            'feature', 'new', 'add', 'implement', 'create', 'build', 'develop',
            'enhancement', 'improvement', 'request', 'suggestion', 'idea'
        ]
        
        # Story/task keywords
        story_keywords = [
            'task', 'work', 'do', 'need to', 'have to', 'should', 'must',
            'create', 'update', 'modify', 'change', 'fix', 'review', 'check'
        ]
        
        # Incident keywords
        incident_keywords = [
            'incident', 'outage', 'down', 'emergency', 'urgent', 'critical',
            'alert', 'alarm', 'service down', 'system down', 'broken'
        ]
        
        # Check for specific types
        if any(keyword in text_lower for keyword in bug_keywords):
            return 'bug'
        elif any(keyword in text_lower for keyword in incident_keywords):
            return 'incident'
        elif any(keyword in text_lower for keyword in feature_keywords):
            return 'feature'
        elif any(keyword in text_lower for keyword in story_keywords):
            return 'task'
        
        return None
    
    def _gpt_task_type_detection(self, text):
        """Use GPT to detect task type"""
        try:
            prompt = f"""
            Analyze the following text and determine if it contains an actionable item.
            
            Text: "{text}"
            
            If it's actionable, respond with the type: bug, incident, feature, task, or none.
            
            Consider:
            - bug: software defects, errors, things that don't work
            - incident: urgent issues, outages, system problems
            - feature: new functionality requests, enhancements
            - task: general work items, to-dos, assignments
            - none: not actionable (chat, questions, etc.)
            
            Respond with only the type or 'none'.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a task classification assistant. Respond only with: bug, incident, feature, task, or none."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip().lower()
            
            # Validate response
            valid_types = ['bug', 'incident', 'feature', 'task', 'none']
            if result in valid_types:
                return None if result == 'none' else result
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"GPT task type detection failed: {str(e)}")
            return None
    
    def _simple_detection(self, text):
        """Simple keyword-based task detection (legacy method)"""
        text_lower = text.lower()
        
        # Task-related keywords
        task_keywords = [
            'need to', 'have to', 'should', 'must', 'task', 'work on',
            'create', 'build', 'develop', 'implement', 'fix', 'update',
            'review', 'check', 'analyze', 'investigate', 'prepare',
            'organize', 'plan', 'schedule', 'arrange', 'coordinate'
        ]
        
        # Urgency indicators
        urgency_keywords = [
            'urgent', 'asap', 'emergency', 'critical', 'important',
            'deadline', 'due', 'priority', 'immediate'
        ]
        
        # Check for task keywords
        has_task_keyword = any(keyword in text_lower for keyword in task_keywords)
        has_urgency = any(keyword in text_lower for keyword in urgency_keywords)
        
        # Check for action verbs at the beginning
        action_verbs = ['create', 'build', 'fix', 'update', 'review', 'check']
        words = text_lower.split()
        starts_with_action = words and words[0] in action_verbs
        
        return has_task_keyword or has_urgency or starts_with_action
    
    def _gpt_detection(self, text):
        """Use GPT to detect task intent (legacy method)"""
        try:
            prompt = f"""
            Analyze the following text and determine if it contains a task request or work assignment.
            
            Text: "{text}"
            
            Respond with only 'YES' if it's a task request, or 'NO' if it's not.
            Consider:
            - Does it ask for something to be done?
            - Does it assign work to someone?
            - Does it request a specific action or deliverable?
            - Is it actionable and specific?
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a task detection assistant. Respond only with YES or NO."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip().upper()
            return result == 'YES'
            
        except Exception as e:
            current_app.logger.error(f"GPT detection failed: {str(e)}")
            return False
    
    def extract_task_details(self, text):
        """Extract task details from text using GPT"""
        try:
            prompt = f"""
            Extract task details from the following text:
            
            Text: "{text}"
            
            Return a JSON object with the following fields:
            - title: A concise task title (max 80 characters)
            - description: Detailed task description
            - priority: low, medium, or high
            - estimated_hours: estimated time in hours (number, null if unknown)
            - skills_required: array of required skills (empty array if none)
            - due_date: due date if mentioned (ISO format or null)
            
            Only return the JSON object, no other text.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a task analysis assistant. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            import json
            result = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            try:
                task_details = json.loads(result)
                
                # Validate and clean up the response
                if not isinstance(task_details, dict):
                    return None
                
                # Ensure required fields exist
                required_fields = ['title', 'description', 'priority']
                for field in required_fields:
                    if field not in task_details:
                        return None
                
                # Validate priority
                if task_details['priority'] not in ['low', 'medium', 'high']:
                    task_details['priority'] = 'medium'
                
                # Ensure title is not too long
                if len(task_details['title']) > 80:
                    task_details['title'] = task_details['title'][:77] + "..."
                
                return task_details
                
            except json.JSONDecodeError:
                current_app.logger.error(f"Failed to parse JSON from GPT response: {result}")
                return None
            
        except Exception as e:
            current_app.logger.error(f"Failed to extract task details: {str(e)}")
            return None 