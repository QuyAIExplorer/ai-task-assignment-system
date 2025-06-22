from flask import Blueprint, request, jsonify, render_template, current_app
from models.database import db, Employee, Task, TaskAssignment, Notification
from utils.email_service import EmailService
from utils.jira_service import JiraService
from utils.slack_service import SlackService
from agents.task_assignment_agent import TaskAssignmentAgent
from datetime import datetime
import json

# Create blueprints
api_bp = Blueprint('api', __name__)
web_bp = Blueprint('web', __name__)

# Initialize services
email_service = EmailService()
jira_service = JiraService()
slack_service = SlackService()
task_agent = TaskAssignmentAgent()


# API Routes
@api_bp.route('/employees', methods=['GET'])
def get_employees():
    """Get all employees"""
    try:
        employees = Employee.query.all()
        return jsonify([{
            'id': emp.id,
            'name': emp.name,
            'email': emp.email,
            'department': emp.department,
            'skills': emp.skills,
            'availability': emp.availability
        } for emp in employees])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/employees', methods=['POST'])
def create_employee():
    """Create a new employee"""
    try:
        data = request.get_json()
        employee = Employee(
            name=data['name'],
            email=data['email'],
            slack_id=data.get('slack_id'),
            jira_id=data.get('jira_id'),
            department=data.get('department'),
            skills=data.get('skills')
        )
        db.session.add(employee)
        db.session.commit()
        return jsonify({'id': employee.id, 'message': 'Employee created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks"""
    try:
        tasks = Task.query.all()
        return jsonify([{
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'priority': task.priority,
            'status': task.status,
            'created_at': task.created_at.isoformat(),
            'assignments': [{
                'employee_id': ass.employee_id,
                'employee_name': ass.employee.name,
                'status': ass.status
            } for ass in task.assignments]
        } for task in tasks])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', 'medium'),
            source=data.get('source', 'manual'),
            created_by=data.get('created_by', 'system')
        )
        db.session.add(task)
        db.session.commit()
        
        # Auto-assign task if requested
        if data.get('auto_assign', False):
            assignment = task_agent.assign_task({
                'title': task.title,
                'description': task.description,
                'priority': task.priority,
                'source': task.source,
                'created_by': task.created_by
            })
            if assignment:
                return jsonify({
                    'id': task.id,
                    'message': 'Task created and assigned',
                    'assignment_id': assignment.id
                }), 201
        
        return jsonify({'id': task.id, 'message': 'Task created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/tasks/<int:task_id>/assign', methods=['POST'])
def assign_task(task_id):
    """Assign a task to an employee"""
    try:
        data = request.get_json()
        employee_id = data['employee_id']
        
        # Check if task exists
        task = Task.query.get_or_404(task_id)
        employee = Employee.query.get_or_404(employee_id)
        
        # Create assignment
        assignment = TaskAssignment(
            task_id=task_id,
            employee_id=employee_id,
            assigned_by=data.get('assigned_by', 'system'),
            notes=data.get('notes', '')
        )
        db.session.add(assignment)
        
        # Update task status
        task.status = 'assigned'
        db.session.commit()
        
        # Send notification
        email_service.send_task_assignment_notification(
            employee.email,
            task.title,
            task.description
        )
        
        return jsonify({'message': 'Task assigned successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/tasks/<int:task_id>/status', methods=['PUT'])
def update_task_status(task_id):
    """Update task status"""
    try:
        data = request.get_json()
        task = Task.query.get_or_404(task_id)
        task.status = data['status']
        db.session.commit()
        
        return jsonify({'message': 'Task status updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/jira/sync', methods=['POST'])
def sync_jira():
    """Sync tasks from Jira"""
    try:
        issues = jira_service.get_project_issues()
        synced_count = 0
        
        for issue in issues:
            # Check if task already exists
            existing_task = Task.query.filter_by(
                source='jira',
                source_id=issue.key
            ).first()
            
            if not existing_task:
                task = Task(
                    title=issue.fields.summary,
                    description=issue.fields.description or '',
                    priority=issue.fields.priority.name.lower() if issue.fields.priority else 'medium',
                    source='jira',
                    source_id=issue.key,
                    created_by='jira_sync'
                )
                db.session.add(task)
                synced_count += 1
        
        db.session.commit()
        return jsonify({'message': f'Synced {synced_count} tasks from Jira'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/slack/events', methods=['POST'])
def slack_events():
    """Handle Slack events and slash commands"""
    try:
        # Handle Slack events using the Slack service
        return slack_service.handler.handle(request)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/slack/commands', methods=['POST'])
def slack_commands():
    """Handle Slack slash commands (alternative endpoint)"""
    try:
        # This endpoint can be used for additional command processing
        data = request.form.to_dict()
        command = data.get('command', '')
        text = data.get('text', '')
        
        # Log the command for debugging
        current_app.logger.info(f"Slack command received: {command} {text}")
        
        # The actual command processing is handled by the Slack service
        # This endpoint is mainly for logging and additional processing
        return jsonify({'message': 'Command received'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/api/employee-matching/find-best', methods=['POST'])
def find_best_employee():
    """Find the best employee for a given task"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['task_type', 'priority', 'required_domain']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Import the employee matcher
        from utils.employee_matcher import find_best_employee_for_task
        
        # Find best employee
        best_employee = find_best_employee_for_task(
            task_type=data['task_type'],
            priority=data['priority'],
            required_domain=data['required_domain'],
            estimated_hours=data.get('estimated_hours'),
            due_date=data.get('due_date'),
            required_skills=data.get('required_skills')
        )
        
        if best_employee:
            return jsonify({
                'success': True,
                'employee': {
                    'id': best_employee.id,
                    'name': best_employee.name,
                    'email': best_employee.email,
                    'department': best_employee.department,
                    'skills': best_employee.skills
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No suitable employee found'
            })
            
    except Exception as e:
        current_app.logger.error(f"Error finding best employee: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/api/employee-matching/recommendations', methods=['POST'])
def get_employee_recommendations():
    """Get multiple employee recommendations for a task"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['task_type', 'priority', 'required_domain']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Import the employee matcher
        from utils.employee_matcher import EmployeeMatcher
        
        matcher = EmployeeMatcher()
        recommendations = matcher.get_employee_recommendations(
            task_type=data['task_type'],
            priority=data['priority'],
            required_domain=data['required_domain'],
            required_skills=data.get('required_skills'),
            limit=data.get('limit', 5)
        )
        
        # Format recommendations
        formatted_recommendations = []
        for employee, score in recommendations:
            formatted_recommendations.append({
                'id': employee.id,
                'name': employee.name,
                'email': employee.email,
                'department': employee.department,
                'skills': employee.skills,
                'score': round(score, 2)
            })
        
        return jsonify({
            'success': True,
            'recommendations': formatted_recommendations
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/api/employee-matching/assign-task', methods=['POST'])
def assign_task_with_matching():
    """Assign a task using intelligent employee matching"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['title', 'task_type', 'priority', 'required_domain']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Import the task assignment agent
        from agents.task_assignment_agent import TaskAssignmentAgent
        
        agent = TaskAssignmentAgent()
        
        # Prepare task data
        task_data = {
            'title': data['title'],
            'description': data.get('description', ''),
            'task_type': data['task_type'],
            'priority': data['priority'],
            'required_domain': data['required_domain'],
            'required_skills': data.get('required_skills'),
            'estimated_hours': data.get('estimated_hours'),
            'due_date': data.get('due_date'),
            'source': data.get('source', 'api'),
            'created_by': data.get('created_by', 'api_user')
        }
        
        # Assign task
        assignment = agent.assign_task(task_data)
        
        if assignment:
            # Get employee details
            employee = Employee.query.get(assignment.employee_id)
            task = Task.query.get(assignment.task_id)
            
            return jsonify({
                'success': True,
                'assignment': {
                    'id': assignment.id,
                    'task_id': assignment.task_id,
                    'employee_id': assignment.employee_id,
                    'assigned_by': assignment.assigned_by,
                    'status': assignment.status,
                    'notes': assignment.notes
                },
                'employee': {
                    'id': employee.id,
                    'name': employee.name,
                    'email': employee.email,
                    'department': employee.department
                },
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'priority': task.priority,
                    'status': task.status
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to assign task - no suitable employee found'
            }), 404
            
    except Exception as e:
        current_app.logger.error(f"Error assigning task: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/api/jira/create-ticket', methods=['POST'])
def create_jira_ticket_api():
    """Create a Jira ticket via API"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['title', 'task_type', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Import the Jira service
        from utils.jira_service import create_jira_ticket
        
        # Create Jira ticket
        result = create_jira_ticket(
            title=data['title'],
            task_type=data['task_type'],
            description=data['description'],
            assignee=data.get('assignee')
        )
        
        if result:
            return jsonify({
                'success': True,
                'issue_key': result['issue_key'],
                'url': result['url'],
                'issue_type': result['issue_type'],
                'assignee': result['assignee']
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to create Jira ticket'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error creating Jira ticket: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/api/jira/tickets', methods=['GET'])
def get_jira_tickets():
    """Get all Jira tickets for the project"""
    try:
        from utils.jira_service import JiraService
        
        jira_service = JiraService()
        issues = jira_service.get_project_issues()
        
        tickets = []
        for issue in issues:
            tickets.append({
                'key': issue.key,
                'summary': issue.fields.summary,
                'description': issue.fields.description,
                'status': issue.fields.status.name,
                'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None,
                'issue_type': issue.fields.issuetype.name,
                'created': issue.fields.created,
                'updated': issue.fields.updated,
                'url': jira_service.get_issue_url(issue.key)
            })
        
        return jsonify({
            'success': True,
            'tickets': tickets,
            'count': len(tickets)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting Jira tickets: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/api/jira/tickets/<issue_key>', methods=['GET'])
def get_jira_ticket(issue_key):
    """Get a specific Jira ticket"""
    try:
        from utils.jira_service import JiraService
        
        jira_service = JiraService()
        issue = jira_service.get_issue(issue_key)
        
        if not issue:
            return jsonify({'error': 'Ticket not found'}), 404
        
        ticket = {
            'key': issue.key,
            'summary': issue.fields.summary,
            'description': issue.fields.description,
            'status': issue.fields.status.name,
            'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None,
            'issue_type': issue.fields.issuetype.name,
            'priority': issue.fields.priority.name if issue.fields.priority else None,
            'created': issue.fields.created,
            'updated': issue.fields.updated,
            'url': jira_service.get_issue_url(issue.key)
        }
        
        return jsonify({
            'success': True,
            'ticket': ticket
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting Jira ticket: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/api/jira/tickets/<issue_key>/assign', methods=['POST'])
def assign_jira_ticket(issue_key):
    """Assign a Jira ticket to a user"""
    try:
        data = request.get_json()
        
        if not data or 'assignee' not in data:
            return jsonify({'error': 'Assignee is required'}), 400
        
        from utils.jira_service import JiraService
        
        jira_service = JiraService()
        success = jira_service.assign_issue(issue_key, data['assignee'])
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Ticket {issue_key} assigned to {data["assignee"]}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to assign ticket'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error assigning Jira ticket: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/api/email/send-assignment', methods=['POST'])
def send_assignment_email_api():
    """Send assignment email via API"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['employee_email', 'task_title', 'task_description', 'jira_url']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Import the email function
        from utils.email_service import send_assignment_email
        
        # Send assignment email
        success = send_assignment_email(
            employee_email=data['employee_email'],
            task_title=data['task_title'],
            task_description=data['task_description'],
            jira_url=data['jira_url']
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Assignment email sent to {data["employee_email"]}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send assignment email'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error sending assignment email: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/api/email/send-jira-assignment', methods=['POST'])
def send_jira_assignment_email_api():
    """Send Jira assignment email via EmailService"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['employee_email', 'task_title', 'task_description', 'jira_url']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Import the EmailService
        from utils.email_service import EmailService
        
        email_service = EmailService()
        
        # Send Jira assignment email
        success = email_service.send_jira_assignment_notification(
            employee_email=data['employee_email'],
            task_title=data['task_title'],
            task_description=data['task_description'],
            jira_url=data['jira_url']
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Jira assignment email sent to {data["employee_email"]}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send Jira assignment email'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error sending Jira assignment email: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks with assignment information"""
    try:
        # Get all tasks with employee information
        tasks = db.session.query(Task).outerjoin(
            TaskAssignment, Task.id == TaskAssignment.task_id
        ).outerjoin(
            Employee, TaskAssignment.employee_id == Employee.id
        ).all()
        
        task_list = []
        for task in tasks:
            # Get assigned employee name
            assigned_employee = None
            if task.task_assignments:
                assignment = task.task_assignments[0]  # Get first assignment
                if assignment.employee:
                    assigned_employee = assignment.employee.name
            
            task_data = {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status or 'Open',
                'priority': task.priority or 'Medium',
                'assigned_employee': assigned_employee,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'source': task.source,
                'estimated_hours': task.estimated_hours
            }
            task_list.append(task_data)
        
        return jsonify({
            'success': True,
            'tasks': task_list,
            'count': len(task_list)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting tasks: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/api/employees', methods=['GET'])
def get_employees():
    """Get all employees with current task information"""
    try:
        employees = Employee.query.all()
        
        employee_list = []
        for employee in employees:
            # Get current task IDs
            current_tasks = []
            if employee.task_assignments:
                for assignment in employee.task_assignments:
                    if assignment.status in ['assigned', 'accepted']:
                        current_tasks.append(f"#{assignment.task.id}")
            
            employee_data = {
                'id': employee.id,
                'name': employee.name,
                'email': employee.email,
                'department': employee.department,
                'skills': employee.skills,
                'level': employee.level,
                'availability': employee.availability,
                'current_tasks': current_tasks,
                'created_at': employee.created_at.isoformat() if employee.created_at else None
            }
            employee_list.append(employee_data)
        
        return jsonify({
            'success': True,
            'employees': employee_list,
            'count': len(employee_list)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting employees: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/api/employees', methods=['POST'])
def create_employee():
    """Create a new employee"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['name', 'email', 'department', 'skills', 'level']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if employee with same email already exists
        existing_employee = Employee.query.filter_by(email=data['email']).first()
        if existing_employee:
            return jsonify({'error': 'Employee with this email already exists'}), 400
        
        # Create new employee
        employee = Employee(
            name=data['name'],
            email=data['email'],
            department=data['department'],
            skills=data['skills'],
            level=data['level'],
            availability=data.get('availability', True)
        )
        
        db.session.add(employee)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Employee created successfully',
            'employee': {
                'id': employee.id,
                'name': employee.name,
                'email': employee.email,
                'department': employee.department,
                'skills': employee.skills,
                'level': employee.level,
                'availability': employee.availability
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error creating employee: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Get counts
        total_tasks = Task.query.count()
        open_tasks = Task.query.filter_by(status='Open').count()
        in_progress_tasks = Task.query.filter_by(status='In Progress').count()
        closed_tasks = Task.query.filter_by(status='Closed').count()
        
        total_employees = Employee.query.count()
        available_employees = Employee.query.filter_by(availability=True).count()
        busy_employees = Employee.query.filter_by(availability=False).count()
        
        # Get recent tasks
        recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(5).all()
        recent_task_list = []
        for task in recent_tasks:
            recent_task_list.append({
                'id': task.id,
                'title': task.title,
                'status': task.status,
                'created_at': task.created_at.isoformat() if task.created_at else None
            })
        
        # Get recent employees
        recent_employees = Employee.query.order_by(Employee.created_at.desc()).limit(5).all()
        recent_employee_list = []
        for employee in recent_employees:
            recent_employee_list.append({
                'id': employee.id,
                'name': employee.name,
                'department': employee.department,
                'availability': employee.availability
            })
        
        return jsonify({
            'success': True,
            'stats': {
                'tasks': {
                    'total': total_tasks,
                    'open': open_tasks,
                    'in_progress': in_progress_tasks,
                    'closed': closed_tasks
                },
                'employees': {
                    'total': total_employees,
                    'available': available_employees,
                    'busy': busy_employees
                }
            },
            'recent_tasks': recent_task_list,
            'recent_employees': recent_employee_list
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting dashboard stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# Web Routes
@web_bp.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')


@web_bp.route('/tasks')
def task_dashboard():
    """Task management dashboard"""
    tasks = Task.query.all()
    employees = Employee.query.all()
    return render_template('tasks.html', tasks=tasks, employees=employees)


@web_bp.route('/employees')
def employee_dashboard():
    """Employee management dashboard"""
    employees = Employee.query.all()
    return render_template('employees.html', employees=employees)


@web_bp.route('/dashboard')
def dashboard():
    """Serve the main dashboard page"""
    return render_template('dashboard.html') 