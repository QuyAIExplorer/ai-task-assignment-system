#!/usr/bin/env python3
"""
Example script demonstrating the employee matching functionality.
This script shows how to use the find_best_employee_for_task function.
"""

from utils.employee_matcher import find_best_employee_for_task, EmployeeMatcher
from models.database import db, Employee, Task, TaskAssignment
from flask import Flask
from config.config import Config
import datetime


def create_app():
    """Create a Flask app for testing"""
    app = Flask(__name__)
    app.config.from_object(Config)
    return app


def setup_sample_data():
    """Create sample employees for testing"""
    # Sample employees with different skills and departments
    employees_data = [
        {
            'name': 'Alice Johnson',
            'email': 'alice@company.com',
            'department': 'Frontend Engineering',
            'skills': 'javascript,react,vue,html,css,ui design',
            'availability': True
        },
        {
            'name': 'Bob Smith',
            'email': 'bob@company.com',
            'department': 'Backend Engineering',
            'skills': 'python,java,node.js,api,database,sql',
            'availability': True
        },
        {
            'name': 'Carol Davis',
            'email': 'carol@company.com',
            'department': 'DevOps',
            'skills': 'docker,kubernetes,aws,ci/cd,deployment,infrastructure',
            'availability': True
        },
        {
            'name': 'David Wilson',
            'email': 'david@company.com',
            'department': 'Mobile Development',
            'skills': 'ios,android,react native,flutter,mobile development',
            'availability': True
        },
        {
            'name': 'Eva Brown',
            'email': 'eva@company.com',
            'department': 'Data Science',
            'skills': 'python,sql,machine learning,ai,analytics,data science',
            'availability': True
        },
        {
            'name': 'Frank Miller',
            'email': 'frank@company.com',
            'department': 'Security',
            'skills': 'security,authentication,authorization,encryption,penetration testing',
            'availability': True
        }
    ]
    
    # Create employees in database
    for emp_data in employees_data:
        employee = Employee(**emp_data)
        db.session.add(employee)
    
    db.session.commit()
    print("Sample employees created successfully!")


def test_employee_matching():
    """Test the employee matching functionality"""
    print("\n=== Testing Employee Matching ===\n")
    
    # Test cases
    test_cases = [
        {
            'name': 'Frontend Bug Fix',
            'task_type': 'bug',
            'priority': 'high',
            'required_domain': 'frontend',
            'description': 'Fix responsive design issue on mobile devices'
        },
        {
            'name': 'Backend API Feature',
            'task_type': 'feature',
            'priority': 'medium',
            'required_domain': 'backend',
            'description': 'Implement new REST API endpoint for user management'
        },
        {
            'name': 'DevOps Incident',
            'task_type': 'incident',
            'priority': 'high',
            'required_domain': 'devops',
            'description': 'Server deployment failure in production environment'
        },
        {
            'name': 'Mobile App Feature',
            'task_type': 'feature',
            'priority': 'low',
            'required_domain': 'mobile',
            'description': 'Add push notification functionality to mobile app'
        },
        {
            'name': 'Data Analysis Task',
            'task_type': 'task',
            'priority': 'medium',
            'required_domain': 'data',
            'description': 'Analyze user behavior data and create reports'
        },
        {
            'name': 'Security Audit',
            'task_type': 'task',
            'priority': 'high',
            'required_domain': 'security',
            'description': 'Conduct security audit of authentication system'
        }
    ]
    
    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print(f"  Task Type: {test_case['task_type']}")
        print(f"  Priority: {test_case['priority']}")
        print(f"  Domain: {test_case['required_domain']}")
        print(f"  Description: {test_case['description']}")
        
        # Find best employee
        best_employee = find_best_employee_for_task(
            task_type=test_case['task_type'],
            priority=test_case['priority'],
            required_domain=test_case['required_domain'],
            required_skills=None
        )
        
        if best_employee:
            print(f"  → Best Match: {best_employee.name} ({best_employee.department})")
            print(f"  → Skills: {best_employee.skills}")
        else:
            print("  → No suitable employee found")
        
        print()


def test_employee_recommendations():
    """Test getting multiple employee recommendations"""
    print("\n=== Testing Employee Recommendations ===\n")
    
    # Test getting recommendations for a complex task
    matcher = EmployeeMatcher()
    recommendations = matcher.get_employee_recommendations(
        task_type='feature',
        priority='high',
        required_domain='backend',
        required_skills=['python', 'api'],
        limit=3
    )
    
    print("Top 3 recommendations for high-priority backend feature:")
    for i, (employee, score) in enumerate(recommendations, 1):
        print(f"{i}. {employee.name} (Score: {score:.2f})")
        print(f"   Department: {employee.department}")
        print(f"   Skills: {employee.skills}")
        print()


def test_workload_consideration():
    """Test how workload affects employee selection"""
    print("\n=== Testing Workload Consideration ===\n")
    
    # Create some task assignments to simulate workload
    employees = Employee.query.all()
    
    # Assign some tasks to create workload
    for i, employee in enumerate(employees[:3]):  # First 3 employees
        task = Task(
            title=f"Sample Task {i+1}",
            description="Sample task for workload testing",
            priority="medium",
            source="test",
            status="assigned"
        )
        db.session.add(task)
        db.session.flush()  # Get task ID
        
        assignment = TaskAssignment(
            task_id=task.id,
            employee_id=employee.id,
            assigned_by="test",
            status="assigned"
        )
        db.session.add(assignment)
    
    db.session.commit()
    
    # Test matching with workload consideration
    print("Testing employee matching with workload consideration...")
    best_employee = find_best_employee_for_task(
        task_type='bug',
        priority='high',
        required_domain='frontend'
    )
    
    if best_employee:
        print(f"Selected employee: {best_employee.name}")
        print(f"Department: {best_employee.department}")
        print(f"Current workload: {len(best_employee.task_assignments)} tasks")
    else:
        print("No suitable employee found")


def main():
    """Main function to run the example"""
    app = create_app()
    
    with app.app_context():
        # Initialize database
        db.create_all()
        
        # Setup sample data
        setup_sample_data()
        
        # Run tests
        test_employee_matching()
        test_employee_recommendations()
        test_workload_consideration()
        
        print("\n=== Example completed successfully! ===")
        print("\nKey features demonstrated:")
        print("1. Domain-based employee matching")
        print("2. Priority-aware assignment")
        print("3. Workload consideration")
        print("4. Multiple employee recommendations")
        print("5. Skills-based matching")


if __name__ == "__main__":
    main() 