#!/usr/bin/env python3
"""
Run script for AI Task Assignment System
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Run the Flask application"""
    try:
        # Check if .env file exists
        if not Path('.env').exists():
            print("❌ .env file not found!")
            print("Please run 'python setup.py' first to create the .env file")
            sys.exit(1)
        
        # Check if virtual environment is activated
        if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("⚠️  Virtual environment not detected")
            print("Please activate your virtual environment first:")
            if os.name == 'nt':
                print("   venv\\Scripts\\activate")
            else:
                print("   source venv/bin/activate")
            print("Then run this script again")
            sys.exit(1)
        
        # Import and run the Flask app
        from backend.app import create_app
        
        app = create_app()
        
        print("🚀 Starting AI Task Assignment System...")
        print("📍 Web interface: http://localhost:5000")
        print("🔌 API endpoints: http://localhost:5000/api")
        print("📡 Slack events: http://localhost:5000/slack/events")
        print("💚 Health check: http://localhost:5000/health")
        print("\nPress Ctrl+C to stop the server")
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 