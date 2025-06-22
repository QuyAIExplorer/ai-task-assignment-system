from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Integer

db = SQLAlchemy()
Base = declarative_base()


class Employee(db.Model):
    """Employee model for storing employee information"""
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    expertise = db.Column(db.String(500), nullable=False)  # String of expertise/skills
    level = db.Column(db.String(20), nullable=False)  # junior, mid, senior
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, 
                          onupdate=datetime.now)
    
    # Relationships
    assigned_tasks = db.relationship('Task', backref='assigned_employee',
                                    lazy=True, foreign_keys='Task.assigned_employee_id')
    
    def __repr__(self):
        return f'<Employee {self.name}>'
    
    @property
    def current_tasks(self):
        """Get list of current task IDs for this employee"""
        return [task.id for task in self.assigned_tasks if task.status != 'Closed']
    
    def to_dict(self):
        """Convert employee to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'expertise': self.expertise,
            'level': self.level,
            'is_available': self.is_available,
            'current_tasks': self.current_tasks,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Task(db.Model):
    """Task model for storing task information"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Open')  # Open, In Progress, Closed
    assigned_employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now,
                          onupdate=datetime.now)
    
    def __repr__(self):
        return f'<Task {self.title}>'
    
    def to_dict(self):
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'assigned_employee_id': self.assigned_employee_id,
            'assigned_employee_name': self.assigned_employee.name if self.assigned_employee else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Supporting functions for database operations
def add_new_employee(name, email, expertise, level, is_available=True):
    """
    Add a new employee to the database
    
    Args:
        name (str): Employee name
        email (str): Employee email
        expertise (str): Employee expertise/skills
        level (str): Employee level (junior, mid, senior)
        is_available (bool): Whether employee is available for tasks
    
    Returns:
        Employee: The created employee object
    """
    try:
        # Check if employee with same email already exists
        existing_employee = Employee.query.filter_by(email=email).first()
        if existing_employee:
            raise ValueError(f"Employee with email {email} already exists")
        
        # Validate level
        valid_levels = ['junior', 'mid', 'senior']
        if level.lower() not in valid_levels:
            raise ValueError(f"Level must be one of: {', '.join(valid_levels)}")
        
        # Create new employee
        employee = Employee(
            name=name,
            email=email,
            expertise=expertise,
            level=level.lower(),
            is_available=is_available
        )
        
        db.session.add(employee)
        db.session.commit()
        
        return employee
        
    except Exception as e:
        db.session.rollback()
        raise e


def assign_task_to_employee(task_id, employee_id):
    """
    Assign a task to an employee
    
    Args:
        task_id (int): ID of the task to assign
        employee_id (int): ID of the employee to assign the task to
    
    Returns:
        Task: The updated task object
    """
    try:
        # Get task and employee
        task = Task.query.get(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        employee = Employee.query.get(employee_id)
        if not employee:
            raise ValueError(f"Employee with ID {employee_id} not found")
        
        # Check if employee is available
        if not employee.is_available:
            raise ValueError(f"Employee {employee.name} is not available")
        
        # Check if task is already assigned
        if task.assigned_employee_id:
            raise ValueError(f"Task '{task.title}' is already assigned to employee ID {task.assigned_employee_id}")
        
        # Assign task to employee
        task.assigned_employee_id = employee_id
        task.status = 'In Progress'  # Update status when assigned
        
        db.session.commit()
        
        return task
        
    except Exception as e:
        db.session.rollback()
        raise e


def update_task_status(task_id, new_status):
    """
    Update the status of a task
    
    Args:
        task_id (int): ID of the task to update
        new_status (str): New status (Open, In Progress, Closed)
    
    Returns:
        Task: The updated task object
    """
    try:
        # Validate status
        valid_statuses = ['Open', 'In Progress', 'Closed']
        if new_status not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        
        # Get task
        task = Task.query.get(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        # Update status
        task.status = new_status
        
        # If task is closed, make employee available again
        if new_status == 'Closed' and task.assigned_employee_id:
            employee = Employee.query.get(task.assigned_employee_id)
            if employee:
                # Check if employee has other active tasks
                active_tasks = Task.query.filter_by(
                    assigned_employee_id=employee.id,
                    status='In Progress'
                ).count()
                
                if active_tasks <= 1:  # This task is the only active one
                    employee.is_available = True
        
        db.session.commit()
        
        return task
        
    except Exception as e:
        db.session.rollback()
        raise e


def get_available_employees():
    """
    Get all available employees
    
    Returns:
        list: List of available Employee objects
    """
    return Employee.query.filter_by(is_available=True).all()


def get_employee_tasks(employee_id):
    """
    Get all tasks assigned to an employee
    
    Args:
        employee_id (int): ID of the employee
    
    Returns:
        list: List of Task objects assigned to the employee
    """
    return Task.query.filter_by(assigned_employee_id=employee_id).all()


def get_unassigned_tasks():
    """
    Get all tasks that are not assigned to any employee
    
    Returns:
        list: List of unassigned Task objects
    """
    return Task.query.filter_by(assigned_employee_id=None).all()


def get_tasks_by_status(status):
    """
    Get all tasks with a specific status
    
    Args:
        status (str): Task status to filter by
    
    Returns:
        list: List of Task objects with the specified status
    """
    return Task.query.filter_by(status=status).all()


# Legacy models for backward compatibility
class TaskAssignment(db.Model):
    """TaskAssignment model for managing task assignments (legacy)"""
    __tablename__ = 'task_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'),
                           nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.now)
    assigned_by = db.Column(db.String(100))
    status = db.Column(db.String(20), default='assigned')  # assigned, accepted, declined
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<TaskAssignment {self.task_id} -> {self.employee_id}>'


class Notification(db.Model):
    """Notification model for storing email notifications"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    recipient_email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default='sent')  # sent, failed, pending
    error_message = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Notification {self.recipient_email}>' 