#!/usr/bin/env python3
"""
Example script demonstrating email assignment functionality.
This script shows how to use the send_assignment_email function.
"""

from utils.email_service import send_assignment_email, EmailService
from flask import Flask
from config.config import Config


def create_app():
    """Create a Flask app for testing"""
    app = Flask(__name__)
    app.config.from_object(Config)
    return app


def test_basic_assignment_email():
    """Test basic assignment email sending"""
    print("\n=== Testing Basic Assignment Email ===\n")
    
    # Test data
    employee_email = "test@example.com"  # Replace with actual email
    task_title = "Fix Login Button Bug"
    task_description = """
    Users are unable to log in using the login button on the homepage. 
    The button appears to be unresponsive and doesn't trigger the login process.
    
    Steps to reproduce:
    1. Go to homepage
    2. Click login button
    3. Button doesn't respond
    
    Expected behavior: Login modal should appear
    """
    jira_url = "https://your-domain.atlassian.net/browse/PROJ-123"
    
    print(f"Sending assignment email to: {employee_email}")
    print(f"Task: {task_title}")
    print(f"Jira URL: {jira_url}")
    
    # Send email
    success = send_assignment_email(
        employee_email=employee_email,
        task_title=task_title,
        task_description=task_description,
        jira_url=jira_url
    )
    
    if success:
        print("✅ Assignment email sent successfully!")
    else:
        print("❌ Failed to send assignment email")
    
    print()


def test_different_task_types():
    """Test sending emails for different task types"""
    print("\n=== Testing Different Task Types ===\n")
    
    test_cases = [
        {
            'title': 'Implement User Dashboard',
            'type': 'Story',
            'description': 'Create a new dashboard page that displays user analytics, recent activities, and quick actions. The dashboard should be responsive and include charts and graphs.',
            'jira_url': 'https://your-domain.atlassian.net/browse/PROJ-124'
        },
        {
            'title': 'Fix Database Performance Issue',
            'type': 'Bug',
            'description': 'Database queries are taking too long to execute. Need to optimize the slow queries and add proper indexing.',
            'jira_url': 'https://your-domain.atlassian.net/browse/PROJ-125'
        },
        {
            'title': 'Add Push Notifications',
            'type': 'Feature',
            'description': 'Implement push notification functionality for mobile app users to receive real-time updates about their tasks and projects.',
            'jira_url': 'https://your-domain.atlassian.net/browse/PROJ-126'
        },
        {
            'title': 'Server Down - Production Issue',
            'type': 'Incident',
            'description': 'Production server is down. Users cannot access the application. Immediate attention required to restore service.',
            'jira_url': 'https://your-domain.atlassian.net/browse/PROJ-127'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['title']} ({test_case['type']})")
        
        success = send_assignment_email(
            employee_email="test@example.com",  # Replace with actual email
            task_title=test_case['title'],
            task_description=test_case['description'],
            jira_url=test_case['jira_url']
        )
        
        if success:
            print(f"  ✅ Email sent for {test_case['type']}")
        else:
            print(f"  ❌ Failed to send email for {test_case['type']}")
        
        print()


def test_email_service_integration():
    """Test using EmailService class with the new function"""
    print("\n=== Testing EmailService Integration ===\n")
    
    email_service = EmailService()
    
    # Test the enhanced send_task_assignment_notification method
    success = email_service.send_task_assignment_notification(
        employee_email="test@example.com",  # Replace with actual email
        task_title="Code Review - Authentication Module",
        task_description="Please review the new user authentication module implementation. Check for security vulnerabilities and code quality.",
        jira_url="https://your-domain.atlassian.net/browse/PROJ-128"
    )
    
    if success:
        print("✅ Email sent via EmailService integration!")
    else:
        print("❌ Failed to send email via EmailService")
    
    # Test the dedicated Jira assignment method
    success = email_service.send_jira_assignment_notification(
        employee_email="test@example.com",  # Replace with actual email
        task_title="Update API Documentation",
        task_description="Update the API documentation to include the new endpoints and fix outdated examples.",
        jira_url="https://your-domain.atlassian.net/browse/PROJ-129"
    )
    
    if success:
        print("✅ Jira assignment email sent via EmailService!")
    else:
        print("❌ Failed to send Jira assignment email")
    
    print()


def test_error_handling():
    """Test error handling scenarios"""
    print("\n=== Testing Error Handling ===\n")
    
    # Test with invalid email
    print("Testing with invalid email...")
    success = send_assignment_email(
        employee_email="invalid-email",
        task_title="Test Task",
        task_description="This should fail due to invalid email",
        jira_url="https://example.com"
    )
    
    if success:
        print("  ✅ Email sent (unexpected)")
    else:
        print("  ❌ Failed as expected")
    
    # Test with empty task title
    print("\nTesting with empty task title...")
    success = send_assignment_email(
        employee_email="test@example.com",
        task_title="",
        task_description="This should work with empty title",
        jira_url="https://example.com"
    )
    
    if success:
        print("  ✅ Email sent with empty title")
    else:
        print("  ❌ Failed with empty title")
    
    print()


def test_bulk_email_sending():
    """Test sending multiple assignment emails"""
    print("\n=== Testing Bulk Email Sending ===\n")
    
    # Sample assignments
    assignments = [
        {
            'email': 'frontend@example.com',
            'title': 'Fix CSS Styling Issues',
            'description': 'Various CSS styling issues on different browsers need to be fixed.',
            'jira_url': 'https://your-domain.atlassian.net/browse/PROJ-130'
        },
        {
            'email': 'backend@example.com',
            'title': 'Optimize Database Queries',
            'description': 'Optimize slow database queries and add proper indexing.',
            'jira_url': 'https://your-domain.atlassian.net/browse/PROJ-131'
        },
        {
            'email': 'qa@example.com',
            'title': 'Add Unit Tests',
            'description': 'Add comprehensive unit tests for the user management module.',
            'jira_url': 'https://your-domain.atlassian.net/browse/PROJ-132'
        }
    ]
    
    successful_sends = 0
    
    for assignment in assignments:
        success = send_assignment_email(
            employee_email=assignment['email'],
            task_title=assignment['title'],
            task_description=assignment['description'],
            jira_url=assignment['jira_url']
        )
        
        if success:
            successful_sends += 1
            print(f"  ✅ Sent to {assignment['email']}: {assignment['title']}")
        else:
            print(f"  ❌ Failed to send to {assignment['email']}")
    
    print(f"\n📊 Summary: Sent {successful_sends} out of {len(assignments)} emails")


def test_email_content():
    """Test and display email content format"""
    print("\n=== Email Content Format ===\n")
    
    # Sample email content
    employee_email = "test@example.com"
    task_title = "Sample Task Assignment"
    task_description = """
    This is a sample task description that demonstrates the email format.
    
    The email will include:
    - Task title
    - Detailed description
    - Jira ticket link
    - Professional formatting
    """
    jira_url = "https://your-domain.atlassian.net/browse/PROJ-999"
    
    print("Email Content Preview:")
    print("-" * 50)
    print(f"From: nguyencongquy23012002@gmail.com")
    print(f"To: {employee_email}")
    print(f"Subject: New Task Assigned: {task_title}")
    print("-" * 50)
    print(f"""
Hello,

You have been assigned a new task:

Task Title: {task_title}

Description:
{task_description}

Jira Ticket: {jira_url}

Please review the task details and update the status in Jira.

Best regards,
AI Task Assignment System
""")
    print("-" * 50)


def main():
    """Main function to run the example"""
    app = create_app()
    
    with app.app_context():
        print("📧 Email Assignment Example")
        print("=" * 50)
        
        # Run tests
        test_basic_assignment_email()
        test_different_task_types()
        test_email_service_integration()
        test_error_handling()
        test_bulk_email_sending()
        test_email_content()
        
        print("\n" + "=" * 50)
        print("✅ Example completed successfully!")
        print("\nKey features demonstrated:")
        print("1. Basic assignment email sending")
        print("2. Different task types and descriptions")
        print("3. EmailService class integration")
        print("4. Error handling for invalid inputs")
        print("5. Bulk email sending")
        print("6. Email content formatting")
        print("\nNote: Make sure GMAIL_APP_PASSWORD is configured!")
        print("Replace test@example.com with actual email addresses for testing.")


if __name__ == "__main__":
    main() 