#!/usr/bin/env python3
"""
Example script demonstrating Employee and Task management with SQLAlchemy.
"""

from flask import Flask
from config.config import Config
from models.database import (
    db, Employee, Task, 
    add_new_employee, assign_task_to_employee, update_task_status,
    get_available_employees, get_employee_tasks, get_unassigned_tasks
)


def create_app():
    """Create a Flask app for testing"""
    app = Flask(__name__)
    app.config.from_object(Config)
    return app


def main():
    """Main function to run the demonstration"""
    app = create_app()
    
    with app.app_context():
        # Initialize database
        db.create_all()
        
        print("🚀 Employee and Task Management Demo")
        print("=" * 50)
        
        # Clear existing data
        print("Clearing existing data...")
        Task.query.delete()
        Employee.query.delete()
        db.session.commit()
        
        # Add employees
        print("\n1. Adding employees...")
        try:
            alice = add_new_employee(
                name="Alice Johnson",
                email="alice@company.com",
                expertise="Frontend Development, React, JavaScript",
                level="senior"
            )
            print(f"   ✅ Added: {alice.name}")
            
            bob = add_new_employee(
                name="Bob Smith",
                email="bob@company.com",
                expertise="Backend Development, Python, Django",
                level="mid"
            )
            print(f"   ✅ Added: {bob.name}")
            
        except ValueError as e:
            print(f"   ❌ Error: {e}")
        
        # Create tasks
        print("\n2. Creating tasks...")
        task1 = Task(title="Fix Login Bug", description="Fix login button issue")
        task2 = Task(title="Implement Dashboard", description="Create user dashboard")
        task3 = Task(title="Update API Docs", description="Update documentation")
        
        db.session.add_all([task1, task2, task3])
        db.session.commit()
        print(f"   ✅ Created 3 tasks")
        
        # Assign tasks
        print("\n3. Assigning tasks...")
        try:
            assign_task_to_employee(task1.id, alice.id)
            print(f"   ✅ Assigned task '{task1.title}' to {alice.name}")
            
            assign_task_to_employee(task2.id, alice.id)
            print(f"   ✅ Assigned task '{task2.title}' to {alice.name}")
            
        except ValueError as e:
            print(f"   ❌ Error: {e}")
        
        # Update task status
        print("\n4. Updating task status...")
        try:
            update_task_status(task1.id, "Closed")
            print(f"   ✅ Updated task #{task1.id} to 'Closed'")
        except ValueError as e:
            print(f"   ❌ Error: {e}")
        
        # Show results
        print("\n5. Current state:")
        available_employees = get_available_employees()
        print(f"   Available employees: {len(available_employees)}")
        
        unassigned_tasks = get_unassigned_tasks()
        print(f"   Unassigned tasks: {len(unassigned_tasks)}")
        
        alice_tasks = get_employee_tasks(alice.id)
        print(f"   {alice.name}'s tasks: {len(alice_tasks)}")
        
        print("\n" + "=" * 50)
        print("✅ Demo completed successfully!")


if __name__ == "__main__":
    main() 