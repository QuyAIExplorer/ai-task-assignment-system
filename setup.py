#!/usr/bin/env python3
"""
Setup script for AI Task Assignment System
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def create_virtual_environment():
    """Create virtual environment if it doesn't exist"""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    return run_command("python -m venv venv", "Creating virtual environment")


def install_dependencies():
    """Install Python dependencies"""
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        pip_cmd = "venv/bin/pip"
    
    return run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies")


def create_env_file():
    """Create .env file from template"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ env.example file not found")
        return False
    
    try:
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your actual credentials")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def setup_database():
    """Initialize database and create tables"""
    try:
        # Create database directory if it doesn't exist
        db_dir = Path("instance")
        db_dir.mkdir(exist_ok=True)
        
        # Create SQLite database
        db_path = db_dir / "task_assignment.db"
        conn = sqlite3.connect(db_path)
        
        # Create tables
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                slack_id VARCHAR(50) UNIQUE,
                jira_id VARCHAR(50) UNIQUE,
                department VARCHAR(100),
                skills TEXT,
                availability BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                priority VARCHAR(20) DEFAULT 'medium',
                status VARCHAR(20) DEFAULT 'pending',
                estimated_hours FLOAT,
                due_date DATETIME,
                source VARCHAR(50),
                source_id VARCHAR(100),
                created_by VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS task_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                employee_id INTEGER NOT NULL,
                assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                assigned_by VARCHAR(100),
                status VARCHAR(20) DEFAULT 'assigned',
                notes TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks (id),
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            );
            
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient_email VARCHAR(120) NOT NULL,
                subject VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'sent',
                error_message TEXT
            );
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False


def create_sample_data():
    """Create sample employees and tasks for testing"""
    try:
        db_path = Path("instance/task_assignment.db")
        conn = sqlite3.connect(db_path)
        
        # Check if data already exists
        cursor = conn.execute("SELECT COUNT(*) FROM employees")
        if cursor.fetchone()[0] > 0:
            print("✅ Sample data already exists")
            conn.close()
            return True
        
        # Insert sample employees
        employees = [
            ("John Doe", "john.doe@company.com", "Engineering", "Python, Flask, React"),
            ("Jane Smith", "jane.smith@company.com", "Design", "UI/UX Design, Figma, Adobe"),
            ("Mike Johnson", "mike.johnson@company.com", "Marketing", "Digital Marketing, SEO, Analytics"),
            ("Sarah Wilson", "sarah.wilson@company.com", "Engineering", "JavaScript, Node.js, MongoDB")
        ]
        
        for emp in employees:
            conn.execute("""
                INSERT INTO employees (name, email, department, skills)
                VALUES (?, ?, ?, ?)
            """, emp)
        
        # Insert sample tasks
        tasks = [
            ("Fix login bug", "There's a bug in the login system that needs to be fixed", "high", "Engineering"),
            ("Design new homepage", "Create a new design for the company homepage", "medium", "Design"),
            ("SEO optimization", "Optimize website for search engines", "low", "Marketing"),
            ("API documentation", "Write comprehensive API documentation", "medium", "Engineering")
        ]
        
        for task in tasks:
            conn.execute("""
                INSERT INTO tasks (title, description, priority, source)
                VALUES (?, ?, ?, 'manual')
            """, task[:3])
        
        conn.commit()
        conn.close()
        
        print("✅ Sample data created successfully")
        return True
    except Exception as e:
        print(f"❌ Sample data creation failed: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 Setting up AI Task Assignment System")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        sys.exit(1)
    
    # Create sample data
    if not create_sample_data():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your actual credentials")
    print("2. Activate virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("3. Run the application:")
    print("   python backend/app.py")
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    main() 