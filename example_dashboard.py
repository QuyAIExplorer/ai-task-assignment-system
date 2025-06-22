#!/usr/bin/env python3
"""
Example script to test the dashboard functionality.
This script creates sample data and tests the API endpoints.
"""

from flask import Flask
from config.config import Config
from models.database import db, Employee, Task, TaskAssignment
from datetime import datetime


def create_app():
    """Create a Flask app for testing"""
    app = Flask(__name__)
    app.config.from_object(Config)
    return app


def setup_sample_data():
    """Create sample employees and tasks for testing"""
    print("Setting up sample data...")
    
    # Create sample employees
    employees_data = [
        {
            'name': 'Alice Johnson',
            'email': 'alice@company.com',
            'department': 'Frontend Engineering',
            'skills': 'javascript,react,vue,html,css,ui design',
            'level': 'Senior',
            'availability': True
        },
        {
            'name': 'Bob Smith',
            'email': 'bob@company.com',
            'department': 'Backend Engineering',
            'skills': 'python,java,node.js,api,database,sql',
            'level': 'Mid-level',
            'availability': True
        },
        {
            'name': 'Carol Davis',
            'email': 'carol@company.com',
            'department': 'DevOps',
            'skills': 'docker,kubernetes,aws,ci/cd,deployment',
            'level': 'Senior',
            'availability': False
        },
        {
            'name': 'David Wilson',
            'email': 'david@company.com',
            'department': 'Mobile Development',
            'skills': 'ios,android,react native,flutter',
            'level': 'Junior',
            'availability': True
        },
        {
            'name': 'Eva Brown',
            'email': 'eva@company.com',
            'department': 'Data Science',
            'skills': 'python,sql,machine learning,ai,analytics',
            'level': 'Lead',
            'availability': True
        }
    ]
    
    employees = []
    for emp_data in employees_data:
        employee = Employee(**emp_data)
        db.session.add(employee)
        employees.append(employee)
    
    db.session.commit()
    print(f"Created {len(employees)} employees")
    
    # Create sample tasks
    tasks_data = [
        {
            'title': 'Fix Login Button Bug',
            'description': 'Users are unable to log in using the login button on the homepage.',
            'status': 'Open',
            'priority': 'High',
            'source': 'manual',
            'created_at': datetime.now()
        },
        {
            'title': 'Implement User Dashboard',
            'description': 'Create a new dashboard page that displays user analytics and activities.',
            'status': 'In Progress',
            'priority': 'Medium',
            'source': 'manual',
            'created_at': datetime.now()
        },
        {
            'title': 'Update API Documentation',
            'description': 'Update the API documentation to include new endpoints.',
            'status': 'Open',
            'priority': 'Low',
            'source': 'manual',
            'created_at': datetime.now()
        },
        {
            'title': 'Add Push Notifications',
            'description': 'Implement push notification functionality for mobile app.',
            'status': 'Closed',
            'priority': 'Medium',
            'source': 'manual',
            'created_at': datetime.now()
        },
        {
            'title': 'Database Performance Optimization',
            'description': 'Optimize slow database queries and add proper indexing.',
            'status': 'In Progress',
            'priority': 'High',
            'source': 'manual',
            'created_at': datetime.now()
        }
    ]
    
    tasks = []
    for task_data in tasks_data:
        task = Task(**task_data)
        db.session.add(task)
        tasks.append(task)
    
    db.session.commit()
    print(f"Created {len(tasks)} tasks")
    
    # Create some task assignments
    assignments = [
        (tasks[1], employees[0]),  # Dashboard task assigned to Alice
        (tasks[4], employees[1]),  # Database task assigned to Bob
        (tasks[3], employees[3]),  # Push notifications assigned to David (closed)
    ]
    
    for task, employee in assignments:
        assignment = TaskAssignment(
            task_id=task.id,
            employee_id=employee.id,
            assigned_by='system',
            status='assigned' if task.status != 'Closed' else 'completed'
        )
        db.session.add(assignment)
    
    db.session.commit()
    print(f"Created {len(assignments)} task assignments")
    
    print("Sample data setup completed!")


def test_api_endpoints():
    """Test the API endpoints"""
    print("\n=== Testing API Endpoints ===\n")
    
    import requests
    
    base_url = "http://localhost:5000"
    
    # Test tasks endpoint
    print("Testing /api/tasks endpoint...")
    try:
        response = requests.get(f"{base_url}/api/tasks")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Tasks endpoint working - {data['count']} tasks found")
            for task in data['tasks'][:3]:  # Show first 3 tasks
                print(f"  - {task['title']} (Status: {task['status']})")
        else:
            print(f"❌ Tasks endpoint failed - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Tasks endpoint error: {e}")
    
    print()
    
    # Test employees endpoint
    print("Testing /api/employees endpoint...")
    try:
        response = requests.get(f"{base_url}/api/employees")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Employees endpoint working - {data['count']} employees found")
            for employee in data['employees'][:3]:  # Show first 3 employees
                print(f"  - {employee['name']} ({employee['department']})")
        else:
            print(f"❌ Employees endpoint failed - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Employees endpoint error: {e}")
    
    print()
    
    # Test dashboard stats endpoint
    print("Testing /api/dashboard/stats endpoint...")
    try:
        response = requests.get(f"{base_url}/api/dashboard/stats")
        if response.status_code == 200:
            data = response.json()
            stats = data['stats']
            print(f"✅ Dashboard stats endpoint working")
            print(f"  - Tasks: {stats['tasks']['total']} total, {stats['tasks']['open']} open")
            print(f"  - Employees: {stats['employees']['total']} total, {stats['employees']['available']} available")
        else:
            print(f"❌ Dashboard stats endpoint failed - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard stats endpoint error: {e}")
    
    print()


def test_create_employee():
    """Test creating a new employee via API"""
    print("=== Testing Employee Creation ===\n")
    
    import requests
    
    base_url = "http://localhost:5000"
    
    new_employee = {
        'name': 'Frank Miller',
        'email': 'frank@company.com',
        'department': 'Security',
        'skills': 'security,authentication,authorization,encryption',
        'level': 'Senior',
        'availability': True
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/employees",
            json=new_employee,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Employee created successfully: {data['employee']['name']}")
        else:
            print(f"❌ Employee creation failed - Status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Employee creation error: {e}")
    
    print()


def main():
    """Main function to run the example"""
    app = create_app()
    
    with app.app_context():
        # Initialize database
        db.create_all()
        
        print("🚀 Dashboard Example")
        print("=" * 50)
        
        # Setup sample data
        setup_sample_data()
        
        print("\n" + "=" * 50)
        print("✅ Sample data created successfully!")
        print("\nNext steps:")
        print("1. Start the Flask server: python run.py")
        print("2. Open the dashboard: http://localhost:5000/dashboard")
        print("3. Test the API endpoints manually")
        print("\nAPI Endpoints:")
        print("- GET /api/tasks - Get all tasks")
        print("- GET /api/employees - Get all employees")
        print("- POST /api/employees - Create new employee")
        print("- GET /api/dashboard/stats - Get dashboard statistics")


if __name__ == "__main__":
    main() 