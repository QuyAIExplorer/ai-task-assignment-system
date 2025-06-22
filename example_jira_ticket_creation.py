#!/usr/bin/env python3
"""
Example script demonstrating Jira ticket creation functionality.
This script shows how to use the create_jira_ticket function.
"""

from utils.jira_service import create_jira_ticket, JiraService
from flask import Flask
from config.config import Config


def create_app():
    """Create a Flask app for testing"""
    app = Flask(__name__)
    app.config.from_object(Config)
    return app


def test_basic_ticket_creation():
    """Test basic ticket creation without assignee"""
    print("\n=== Testing Basic Ticket Creation ===\n")
    
    # Test cases for different task types
    test_cases = [
        {
            'title': 'Fix Login Button Not Working',
            'task_type': 'bug',
            'description': 'Users are unable to log in using the login button on the homepage. The button appears to be unresponsive.',
            'assignee': None
        },
        {
            'title': 'Implement User Dashboard',
            'task_type': 'story',
            'description': 'Create a new dashboard page that displays user analytics, recent activities, and quick actions.',
            'assignee': None
        },
        {
            'title': 'Update Documentation',
            'task_type': 'task',
            'description': 'Update the API documentation to include the new endpoints and fix outdated examples.',
            'assignee': None
        },
        {
            'title': 'Add Push Notifications',
            'task_type': 'feature',
            'description': 'Implement push notification functionality for mobile app users to receive real-time updates.',
            'assignee': None
        },
        {
            'title': 'Server Down - Production Issue',
            'task_type': 'incident',
            'description': 'Production server is down. Users cannot access the application. Immediate attention required.',
            'assignee': None
        }
    ]
    
    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['title']}")
        print(f"  Task Type: {test_case['task_type']}")
        print(f"  Description: {test_case['description'][:50]}...")
        
        # Create Jira ticket
        result = create_jira_ticket(
            title=test_case['title'],
            task_type=test_case['task_type'],
            description=test_case['description'],
            assignee=test_case['assignee']
        )
        
        if result:
            print(f"  ✅ Success! Issue Key: {result['issue_key']}")
            print(f"  📋 Issue Type: {result['issue_type']}")
            print(f"  🔗 URL: {result['url']}")
        else:
            print("  ❌ Failed to create ticket")
        
        print()


def test_ticket_with_assignee():
    """Test ticket creation with assignee"""
    print("\n=== Testing Ticket Creation with Assignee ===\n")
    
    # Test with assignee
    result = create_jira_ticket(
        title='Code Review - User Authentication Module',
        task_type='task',
        description='Please review the new user authentication module implementation. Check for security vulnerabilities and code quality.',
        assignee='john.doe'  # Replace with actual Jira username
    )
    
    if result:
        print("✅ Ticket created with assignee!")
        print(f"  Issue Key: {result['issue_key']}")
        print(f"  Assignee: {result['assignee']}")
        print(f"  URL: {result['url']}")
    else:
        print("❌ Failed to create ticket with assignee")
    
    print()


def test_jira_service_class():
    """Test using the JiraService class directly"""
    print("\n=== Testing JiraService Class ===\n")
    
    jira_service = JiraService()
    
    # Test different methods
    test_cases = [
        {
            'title': 'Database Performance Issue',
            'task_type': 'bug',
            'description': 'Database queries are taking too long to execute. Need to optimize the slow queries.',
            'assignee': 'database.admin'
        },
        {
            'title': 'Mobile App Redesign',
            'task_type': 'epic',
            'description': 'Complete redesign of the mobile application to improve user experience and add new features.',
            'assignee': 'mobile.lead'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['title']}")
        
        result = jira_service.create_jira_ticket(
            title=test_case['title'],
            task_type=test_case['task_type'],
            description=test_case['description'],
            assignee=test_case['assignee']
        )
        
        if result:
            print(f"  ✅ Created: {result['issue_key']}")
            print(f"  📋 Type: {result['issue_type']}")
            print(f"  👤 Assignee: {result['assignee']}")
            print(f"  🔗 URL: {result['url']}")
        else:
            print("  ❌ Failed to create ticket")
        
        print()


def test_error_handling():
    """Test error handling scenarios"""
    print("\n=== Testing Error Handling ===\n")
    
    # Test with invalid task type
    print("Testing with invalid task type...")
    result = create_jira_ticket(
        title='Test Invalid Type',
        task_type='invalid_type',
        description='This should default to Task type',
        assignee=None
    )
    
    if result:
        print(f"  ✅ Created with default type: {result['issue_type']}")
    else:
        print("  ❌ Failed to create ticket")
    
    # Test with empty title
    print("\nTesting with empty title...")
    result = create_jira_ticket(
        title='',
        task_type='task',
        description='This should fail due to empty title',
        assignee=None
    )
    
    if result:
        print("  ✅ Created (unexpected)")
    else:
        print("  ❌ Failed as expected")
    
    print()


def test_bulk_ticket_creation():
    """Test creating multiple tickets in bulk"""
    print("\n=== Testing Bulk Ticket Creation ===\n")
    
    # Sample bulk tasks
    bulk_tasks = [
        {
            'title': 'Fix CSS Styling Issues',
            'task_type': 'bug',
            'description': 'Various CSS styling issues on different browsers need to be fixed.',
            'assignee': 'frontend.dev'
        },
        {
            'title': 'Add Unit Tests',
            'task_type': 'task',
            'description': 'Add comprehensive unit tests for the user management module.',
            'assignee': 'qa.engineer'
        },
        {
            'title': 'Update Dependencies',
            'task_type': 'task',
            'description': 'Update all project dependencies to their latest stable versions.',
            'assignee': 'devops.engineer'
        }
    ]
    
    created_tickets = []
    
    for task in bulk_tasks:
        result = create_jira_ticket(
            title=task['title'],
            task_type=task['task_type'],
            description=task['description'],
            assignee=task['assignee']
        )
        
        if result:
            created_tickets.append(result)
            print(f"  ✅ Created: {result['issue_key']} - {task['title']}")
        else:
            print(f"  ❌ Failed: {task['title']}")
    
    print(f"\n📊 Summary: Created {len(created_tickets)} out of {len(bulk_tasks)} tickets")


def main():
    """Main function to run the example"""
    app = create_app()
    
    with app.app_context():
        print("🚀 Jira Ticket Creation Example")
        print("=" * 50)
        
        # Run tests
        test_basic_ticket_creation()
        test_ticket_with_assignee()
        test_jira_service_class()
        test_error_handling()
        test_bulk_ticket_creation()
        
        print("\n" + "=" * 50)
        print("✅ Example completed successfully!")
        print("\nKey features demonstrated:")
        print("1. Basic ticket creation for different task types")
        print("2. Ticket assignment to specific users")
        print("3. Using JiraService class directly")
        print("4. Error handling for invalid inputs")
        print("5. Bulk ticket creation")
        print("\nNote: Make sure your Jira credentials are properly configured!")


if __name__ == "__main__":
    main() 