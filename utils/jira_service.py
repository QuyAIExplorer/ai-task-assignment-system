from jira import JIRA
from flask import current_app
from datetime import datetime


def create_jira_ticket(title, task_type, description, assignee=None):
    """
    Simple function to create a Jira ticket.
    
    Args:
        title (str): Task title/summary
        task_type (str): Type of task (bug/story/task/feature/incident)
        description (str): Task description
        assignee (str, optional): Jira username to assign the ticket to
        
    Returns:
        dict: Contains 'issue_key' and 'url', or None if creation failed
    """
    jira_service = JiraService()
    return jira_service.create_jira_ticket(title, task_type, description, assignee)


class JiraService:
    """Jira service for project management integration"""
    
    def __init__(self):
        self.jira = JIRA(
            server=current_app.config['JIRA_SERVER'],
            basic_auth=(
                current_app.config['JIRA_EMAIL'],
                current_app.config['JIRA_API_TOKEN']
            )
        )
        self.project_key = current_app.config['JIRA_PROJECT_KEY']
        
        # Map task types to Jira issue types
        self.task_type_mapping = {
            'bug': 'Bug',
            'story': 'Story',
            'task': 'Task',
            'feature': 'Story',
            'incident': 'Bug',
            'epic': 'Epic',
            'subtask': 'Sub-task'
        }
    
    def create_jira_ticket(self, title, task_type, description, assignee=None):
        """
        Create a Jira ticket with the specified parameters.
        
        Args:
            title (str): Task title/summary
            task_type (str): Type of task (bug/story/task/feature/incident)
            description (str): Task description
            assignee (str, optional): Jira username to assign the ticket to
            
        Returns:
            dict: Contains 'issue_key' and 'url', or None if creation failed
        """
        try:
            # Map task type to Jira issue type
            issue_type = self.task_type_mapping.get(task_type.lower(), 'Task')
            
            # Prepare issue data
            issue_dict = {
                'project': self.project_key,
                'summary': title,
                'description': description,
                'issuetype': {'name': issue_type}
            }
            
            # Add assignee if provided
            if assignee:
                issue_dict['assignee'] = {'name': assignee}
            
            # Create the issue
            new_issue = self.jira.create_issue(fields=issue_dict)
            
            # Construct the URL
            issue_url = f"{current_app.config['JIRA_SERVER']}/browse/{new_issue.key}"
            
            current_app.logger.info(
                f"Created Jira ticket {new_issue.key} for task: {title}"
            )
            
            return {
                'issue_key': new_issue.key,
                'url': issue_url,
                'issue_type': issue_type,
                'assignee': assignee
            }
            
        except Exception as e:
            current_app.logger.error(f"Failed to create Jira ticket: {str(e)}")
            return None
    
    def create_issue(self, summary, description, issue_type='Task', 
                    priority='Medium', assignee=None):
        """Create a new Jira issue"""
        try:
            issue_dict = {
                'project': self.project_key,
                'summary': summary,
                'description': description,
                'issuetype': {'name': issue_type},
                'priority': {'name': priority}
            }
            
            if assignee:
                issue_dict['assignee'] = {'name': assignee}
            
            new_issue = self.jira.create_issue(fields=issue_dict)
            return new_issue.key
            
        except Exception as e:
            current_app.logger.error(f"Failed to create Jira issue: {str(e)}")
            return None
    
    def update_issue(self, issue_key, **fields):
        """Update an existing Jira issue"""
        try:
            issue = self.jira.issue(issue_key)
            issue.update(fields=fields)
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to update Jira issue: {str(e)}")
            return False
    
    def get_issue(self, issue_key):
        """Get issue details"""
        try:
            return self.jira.issue(issue_key)
        except Exception as e:
            current_app.logger.error(f"Failed to get Jira issue: {str(e)}")
            return None
    
    def search_issues(self, jql_query):
        """Search issues using JQL"""
        try:
            return self.jira.search_issues(jql_query)
        except Exception as e:
            current_app.logger.error(f"Failed to search Jira issues: {str(e)}")
            return []
    
    def get_project_issues(self, status=None):
        """Get all issues for the project"""
        try:
            jql = f"project = {self.project_key}"
            if status:
                jql += f" AND status = '{status}'"
            
            return self.jira.search_issues(jql)
        except Exception as e:
            current_app.logger.error(f"Failed to get project issues: {str(e)}")
            return []
    
    def add_comment(self, issue_key, comment):
        """Add comment to an issue"""
        try:
            self.jira.add_comment(issue_key, comment)
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to add comment: {str(e)}")
            return False
    
    def transition_issue(self, issue_key, transition_name):
        """Transition issue to a new status"""
        try:
            issue = self.jira.issue(issue_key)
            transitions = self.jira.transitions(issue)
            
            for transition in transitions:
                if transition['name'].lower() == transition_name.lower():
                    self.jira.transition_issue(issue, transition['id'])
                    return True
            
            return False
        except Exception as e:
            current_app.logger.error(f"Failed to transition issue: {str(e)}")
            return False
    
    def get_issue_url(self, issue_key):
        """Get the URL for a Jira issue"""
        return f"{current_app.config['JIRA_SERVER']}/browse/{issue_key}"
    
    def assign_issue(self, issue_key, assignee):
        """Assign an issue to a user"""
        try:
            issue = self.jira.issue(issue_key)
            self.jira.assign_issue(issue, assignee)
            current_app.logger.info(f"Assigned issue {issue_key} to {assignee}")
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to assign issue: {str(e)}")
            return False 