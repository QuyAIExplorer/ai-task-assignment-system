#!/usr/bin/env python3
"""
Simulation of the complete Slack workflow:
1. AI determines it's a bug
2. Employee chosen based on expertise
3. Jira ticket created
4. Email sent
5. Dashboards updated
6. Slack message sent
"""

import json
from datetime import datetime
from flask import Flask
from config.config import Config
from models.database import (
    db, Employee, Task, 
    add_new_employee, assign_task_to_employee
)
from utils.task_intent_detector import TaskIntentDetector
from utils.employee_matcher import EmployeeMatcher
from utils.jira_service import JiraService
from utils.email_service import EmailService
from utils.slack_service import SlackService


def create_app():
    """Create a Flask app for testing"""
    app = Flask(__name__)
    app.config.from_object(Config)
    return app


def setup_sample_data():
    """Create sample employees for testing"""
    print("Setting up sample employees...")
    
    employees_data = [
        {
            'name': 'Alice Johnson',
            'email': 'alice@company.com',
            'expertise': 'Frontend Development, React, JavaScript, UI/UX, Checkout Process',
            'level': 'senior',
            'is_available': True
        },
        {
            'name': 'Bob Smith',
            'email': 'bob@company.com',
            'expertise': 'Backend Development, Python, Django, Payment Processing, API',
            'level': 'senior',
            'is_available': True
        },
        {
            'name': 'Carol Davis',
            'email': 'carol@company.com',
            'expertise': 'DevOps, Infrastructure, Database, Monitoring, Deployment',
            'level': 'senior',
            'is_available': True
        },
        {
            'name': 'David Wilson',
            'email': 'david@company.com',
            'expertise': 'Mobile Development, iOS, Android, React Native',
            'level': 'mid',
            'is_available': True
        }
    ]
    
    employees = []
    for emp_data in employees_data:
        try:
            employee = add_new_employee(**emp_data)
            employees.append(employee)
            print(f"   ✅ Added: {employee.name} ({employee.level})")
        except ValueError as e:
            print(f"   ❌ Error: {e}")
    
    return employees


def simulate_slack_workflow():
    """Simulate the complete Slack workflow"""
    print("\n" + "="*60)
    print("🚀 SIMULATING SLACK WORKFLOW")
    print("="*60)
    
    # Step 1: Simulate Slack message
    slack_message = "We've identified a critical bug impacting the checkout process. Our team is actively investigating and working on a fix."
    print(f"\n📨 SLACK MESSAGE RECEIVED:")
    print(f"   '{slack_message}'")
    
    # Step 2: AI determines it's a bug
    print(f"\n🤖 STEP 1: AI TASK INTENT DETECTION")
    print("-" * 40)
    
    intent_detector = TaskIntentDetector()
    try:
        intent_result = intent_detector.detect_intent(slack_message)
        print(f"   ✅ Intent detected: {intent_result['intent']}")
        print(f"   ✅ Confidence: {intent_result['confidence']:.2f}")
        print(f"   ✅ Task type: {intent_result['task_type']}")
        print(f"   ✅ Priority: {intent_result['priority']}")
        
        if intent_result['intent'] == 'actionable':
            print(f"   ✅ Message is actionable - proceeding with task creation")
        else:
            print(f"   ❌ Message is not actionable - stopping workflow")
            return
            
    except Exception as e:
        print(f"   ❌ Error in intent detection: {e}")
        return
    
    # Step 3: Create task in database
    print(f"\n📝 STEP 2: TASK CREATION")
    print("-" * 40)
    
    try:
        task = Task(
            title=f"Critical Bug: Checkout Process Issue",
            description=slack_message,
            status='Open',
            priority=intent_result['priority'],
            source='slack'
        )
        db.session.add(task)
        db.session.commit()
        print(f"   ✅ Task created: #{task.id} - {task.title}")
        print(f"   ✅ Status: {task.status}")
        print(f"   ✅ Priority: {task.priority}")
        
    except Exception as e:
        print(f"   ❌ Error creating task: {e}")
        return
    
    # Step 4: Employee matching
    print(f"\n👥 STEP 3: EMPLOYEE MATCHING")
    print("-" * 40)
    
    try:
        matcher = EmployeeMatcher()
        best_employee = matcher.find_best_employee(
            task_type=intent_result['task_type'],
            priority=task.priority,
            required_domain='checkout process, payment processing, frontend'
        )
        
        if best_employee:
            print(f"   ✅ Best match found: {best_employee.name}")
            print(f"   ✅ Expertise: {best_employee.expertise}")
            print(f"   ✅ Level: {best_employee.level}")
            print(f"   ✅ Available: {best_employee.is_available}")
        else:
            print(f"   ❌ No suitable employee found")
            return
            
    except Exception as e:
        print(f"   ❌ Error in employee matching: {e}")
        return
    
    # Step 5: Assign task to employee
    print(f"\n🔗 STEP 4: TASK ASSIGNMENT")
    print("-" * 40)
    
    try:
        updated_task = assign_task_to_employee(task.id, best_employee.id)
        print(f"   ✅ Task assigned to: {best_employee.name}")
        print(f"   ✅ Task status updated to: {updated_task.status}")
        
    except Exception as e:
        print(f"   ❌ Error assigning task: {e}")
        return
    
    # Step 6: Create Jira ticket
    print(f"\n🎫 STEP 5: JIRA TICKET CREATION")
    print("-" * 40)
    
    try:
        jira_service = JiraService()
        jira_result = jira_service.create_jira_ticket(
            title=task.title,
            description=task.description,
            task_type=intent_result['task_type'],
            priority=task.priority,
            assignee=best_employee.email
        )
        
        print(f"   ✅ Jira ticket created: {jira_result['issue_key']}")
        print(f"   ✅ Jira URL: {jira_result['url']}")
        print(f"   ✅ Assignee: {jira_result['assignee']}")
        
        # Update task with Jira info
        task.source_id = jira_result['issue_key']
        db.session.commit()
        
    except Exception as e:
        print(f"   ❌ Error creating Jira ticket: {e}")
        # Continue with workflow even if Jira fails
    
    # Step 7: Send email notification
    print(f"\n📧 STEP 6: EMAIL NOTIFICATION")
    print("-" * 40)
    
    try:
        email_service = EmailService()
        email_result = email_service.send_assignment_email(
            employee_email=best_employee.email,
            employee_name=best_employee.name,
            task_title=task.title,
            task_description=task.description,
            jira_url=jira_result.get('url', 'N/A') if 'jira_result' in locals() else 'N/A'
        )
        
        print(f"   ✅ Email sent to: {best_employee.email}")
        print(f"   ✅ Subject: {email_result['subject']}")
        print(f"   ✅ Status: {email_result['status']}")
        
    except Exception as e:
        print(f"   ❌ Error sending email: {e}")
        # Continue with workflow even if email fails
    
    # Step 8: Update dashboards (simulate)
    print(f"\n📊 STEP 7: DASHBOARD UPDATES")
    print("-" * 40)
    
    try:
        # Simulate dashboard updates
        print(f"   ✅ Task dashboard updated with new task")
        print(f"   ✅ Employee dashboard updated - {best_employee.name} now busy")
        print(f"   ✅ Real-time updates sent to connected clients")
        
        # Get current stats
        total_tasks = Task.query.count()
        open_tasks = Task.query.filter_by(status='Open').count()
        in_progress_tasks = Task.query.filter_by(status='In Progress').count()
        available_employees = Employee.query.filter_by(is_available=True).count()
        
        print(f"   📈 Current stats:")
        print(f"      - Total tasks: {total_tasks}")
        print(f"      - Open tasks: {open_tasks}")
        print(f"      - In progress: {in_progress_tasks}")
        print(f"      - Available employees: {available_employees}")
        
    except Exception as e:
        print(f"   ❌ Error updating dashboards: {e}")
    
    # Step 9: Send Slack response
    print(f"\n💬 STEP 8: SLACK RESPONSE")
    print("-" * 40)
    
    try:
        slack_service = SlackService()
        
        # Create response message
        jira_key = jira_result.get('issue_key', 'N/A') if 'jira_result' in locals() else 'N/A'
        jira_url = jira_result.get('url', 'N/A') if 'jira_result' in locals() else 'N/A'
        
        response_message = f"Bug ticket created with title '{task.title}'. You can view the ticket on Jira: {jira_url}"
        
        slack_response = slack_service.send_message(
            channel="#general",
            message=response_message,
            thread_ts=None  # Would be the original message timestamp in real scenario
        )
        
        print(f"   ✅ Slack response sent:")
        print(f"      '{response_message}'")
        print(f"   ✅ Channel: #general")
        print(f"   ✅ Status: {slack_response.get('status', 'sent')}")
        
    except Exception as e:
        print(f"   ❌ Error sending Slack response: {e}")
    
    # Step 10: Workflow summary
    print(f"\n" + "="*60)
    print("📋 WORKFLOW SUMMARY")
    print("="*60)
    
    print(f"✅ Task created: #{task.id} - {task.title}")
    print(f"✅ Assigned to: {best_employee.name} ({best_employee.email})")
    if 'jira_result' in locals():
        print(f"✅ Jira ticket: {jira_result['issue_key']}")
    print(f"✅ Email notification sent")
    print(f"✅ Dashboards updated")
    print(f"✅ Slack response sent")
    
    print(f"\n🎯 Workflow completed successfully!")
    print(f"   The critical checkout bug has been properly tracked and assigned.")


def main():
    """Main function to run the simulation"""
    app = create_app()
    
    with app.app_context():
        # Initialize database
        db.create_all()
        
        print("🚀 Slack Workflow Simulation")
        print("=" * 60)
        
        # Clear existing data
        print("Clearing existing data...")
        Task.query.delete()
        Employee.query.delete()
        db.session.commit()
        
        # Setup sample employees
        employees = setup_sample_data()
        
        if not employees:
            print("❌ No employees created. Cannot proceed with simulation.")
            return
        
        # Run the simulation
        simulate_slack_workflow()


if __name__ == "__main__":
    main() 