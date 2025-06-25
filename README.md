# AI-Powered Task Assignment System

An intelligent task management system that uses AI to automatically assign tasks to employees based on skills, availability, and workload. Built with Flask, SQLAlchemy, OpenAI GPT, and modern web technologies.

## 🚀 Features

- 🤖 **AI-Powered Task Detection**: Uses OpenAI GPT to detect actionable tasks from Slack messages
- 👥 **Intelligent Employee Matching**: Sophisticated algorithm to find the best employee for each task
- 📱 **Slack Integration**: Real-time message monitoring with slash commands and AI detection
- 🎯 **Jira Integration**: Automatic ticket creation and synchronization
- 📧 **Email Notifications**: Professional Gmail SMTP notifications for task assignments
- 📊 **Modern Dashboard**: Beautiful, responsive web interface with real-time updates
- 🔄 **Auto-refresh**: Live dashboard updates every 30 seconds
- 🎨 **Command Parsing**: Support for `!bug`, `!story`, `!task`, `!incident`, `!feature` commands
- 📈 **Real-time Statistics**: Live task and employee metrics

## 🏗️ Architecture

```
├── backend/                    # Flask application and API routes
│   ├── app.py                 # Main Flask application
│   └── routes.py              # API and web routes
├── frontend/                   # HTML templates and static assets
│   └── templates/
│       ├── dashboard.html     # Main dashboard interface
│       ├── index.html         # Landing page
│       ├── tasks.html         # Task management
│       └── employees.html     # Employee management
├── models/                     # SQLAlchemy database models
│   └── database.py            # Employee, Task, and supporting models
├── utils/                      # Utility services
│   ├── slack_service.py       # Slack integration and bot
│   ├── jira_service.py        # Jira ticket creation and management
│   ├── email_service.py       # Gmail SMTP email notifications
│   ├── task_intent_detector.py # OpenAI GPT task detection
│   └── employee_matcher.py    # Intelligent employee matching
├── config/                     # Configuration management
│   └── config.py              # Environment-based configuration
├── agents/                     # AutoGen multi-agent orchestration
│   └── task_assignment_agent.py # AI agents for task assignment
├── example_*.py               # Example scripts and simulations
├── *.md                       # Comprehensive documentation
└── requirements.txt           # Python dependencies
```

### System Architecture Flow

Below is a high-level architecture diagram of the application's flow:

```mermaid
flowchart TD
   A["User"] -->|"Interacts via UI/API"| B["Frontend"]
    A["User"] -->|"Interacts via SLackMessage"| C["Backend (Flask app.py/routes.py)"]
    B -->|"Sends requests"| C["Backend (Flask app.py/routes.py)"]
    C -->|"Reads/Writes"| D["Database (models/database.py)"]
    C -->|"Uses"| E["Agents (agents/task_assignment_agent.py)"]
    C -->|"Uses"| F["Utils (utils/*)"]
    F -->|"Email/Jira/Slack"| G["External Services (email, Jira, Slack)"]
    E -->|"Assigns tasks"| D
    C -->|"Handles AI logic"| H["TaskIntentDetector"]
    H -->|"Interacts with"| E
    H -->|"Interacts with"| F

    subgraph "Backend"
        C
        E
        F
        H
    end
    subgraph "Database"
        D
    end
    subgraph "External"
        G
    end
```

## 🛠️ Prerequisites

- Python 3.8+
- Slack Bot Token and App Token
- Jira API credentials
- OpenAI API key
- Gmail account for SMTP

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-task-assignment-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your actual credentials
   ```

5. **Initialize database**
   ```bash
   python example_employee_task_management.py
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=sqlite:///task_assignment.db

# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_SIGNING_SECRET=your-signing-secret

# Jira Configuration
JIRA_URL=https://your-domain.atlassian.net
JIRA_API_TOKEN=your-jira-api-token
JIRA_EMAIL=your-email@domain.com
JIRA_PROJECT_KEY=PROJ

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key

# Email Configuration (Gmail)
GMAIL_APP_PASSWORD=your-gmail-app-password
SENDER_EMAIL=notifications@company.com
```

### Setting up Slack Bot

1. Create a Slack app at https://api.slack.com/apps
2. Add bot token scopes: `chat:write`, `channels:read`, `users:read`, `commands`
3. Enable Socket Mode and add app token
4. Subscribe to events: `message.channels`, `app_mention`
5. Add slash commands: `/task`, `/bug`, `/story`
6. Install app to workspace

### Setting up Jira Integration

1. Generate API token in Jira account settings
2. Note your Jira domain and project key
3. Ensure the project exists and you have access

### Setting up Gmail SMTP

1. Enable 2-factor authentication on Gmail account
2. Generate app password for SMTP access
3. Use app password in `GMAIL_APP_PASSWORD` variable

## 🎮 Usage

### Web Dashboard

Access the dashboard at `http://localhost:5000/dashboard`

**Task Management Tab:**
- View all tasks with status, assignments, and priority
- Auto-refresh every 30 seconds
- Color-coded status indicators
- Real-time task statistics

**Employee Management Tab:**
- View employee directory with expertise and availability
- Add new employees via modal form
- Track current task assignments
- Monitor employee availability status

### Slack Integration

**AI-Powered Detection:**
- Monitors all messages for actionable content
- Uses GPT to detect task requests, bugs, features
- Automatically determines priority and task type

**Slash Commands:**
- `/task <description>` - Create a task
- `/bug <description>` - Create a bug report
- `/story <description>` - Create a user story

**Command Prefixes:**
- `!bug <description>` - Create a bug
- `!story <description>` - Create a story
- `!task <description>` - Create a task
- `!incident <description>` - Create an incident
- `!feature <description>` - Create a feature request

**Bot Mentions:**
- `@bot help` - Get help information
- `@bot status` - Check system status

### API Endpoints

**Task Management:**
- `GET /api/tasks` - Get all tasks with assignment info
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/{id}/status` - Update task status
- `POST /api/tasks/{id}/assign` - Assign task to employee

**Employee Management:**
- `GET /api/employees` - Get all employees with current tasks
- `POST /api/employees` - Add new employee
- `GET /api/employees/available` - Get available employees

**Jira Integration:**
- `POST /api/jira/tickets` - Create Jira ticket
- `GET /api/jira/tickets/{key}` - Get ticket details
- `PUT /api/jira/tickets/{key}/assign` - Assign ticket

**Email Notifications:**
- `POST /api/email/assignment` - Send assignment email
- `POST /api/email/jira-assignment` - Send Jira assignment email

**Dashboard:**
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /dashboard` - Main dashboard page

## 🤖 AI Features

### Task Intent Detection

Uses OpenAI GPT to analyze messages and determine:

- **Intent**: `actionable` or `non-actionable`
- **Task Type**: `bug`, `feature`, `story`, `incident`
- **Priority**: `High`, `Medium`, `Low`
- **Confidence**: 0.0-1.0 score

### Intelligent Employee Matching

Sophisticated algorithm considers:

- **Domain Expertise**: Skills match with task requirements
- **Experience Level**: Junior, Mid-level, Senior, Lead
- **Current Workload**: Number of active tasks
- **Department Alignment**: Relevant department expertise
- **Availability Status**: Free vs. busy employees
- **Priority Handling**: Senior employees for high-priority tasks

### AutoGen Multi-Agent Orchestration

Two AI agents collaborate for optimal task assignment:

1. **TaskAnalyst**: Analyzes task requirements and employee capabilities
2. **TaskManager**: Makes final assignment decisions based on recommendations

## 📊 Database Schema

### Employee Model
```python
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    expertise = db.Column(db.String(500), nullable=False)
    level = db.Column(db.String(20), nullable=False)  # junior, mid, senior
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
```

### Task Model
```python
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Open')  # Open, In Progress, Closed
    assigned_employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
```

## 🔧 Supporting Functions

### Employee Management
- `add_new_employee()` - Add employee with validation
- `get_available_employees()` - Get available employees
- `get_employee_tasks()` - Get tasks for specific employee

### Task Management
- `assign_task_to_employee()` - Assign task to available employee
- `update_task_status()` - Update status and manage availability
- `get_unassigned_tasks()` - Get unassigned tasks
- `get_tasks_by_status()` - Get tasks by status

## 🧪 Testing & Simulation

### Run Examples

```bash
# Test employee and task management
python example_employee_task_management.py

# Test email functionality
python example_email_assignment.py

# Test Jira integration
python example_jira_ticket_creation.py

# Test employee matching
python example_employee_matching.py

# Run complete Slack workflow simulation
python test_slack_workflow.py
```

### Slack Workflow Simulation

The system includes a comprehensive simulation that demonstrates the complete workflow:

1. **Slack Message Reception**: "We've identified a critical bug impacting the checkout process..."
2. **AI Detection**: Determines it's a bug with High priority
3. **Employee Matching**: Finds best employee (Alice Johnson - Frontend/Checkout expertise)
4. **Task Assignment**: Assigns task and updates status
5. **Jira Creation**: Creates ticket PROJ-123
6. **Email Notification**: Sends assignment email
7. **Dashboard Updates**: Updates real-time statistics
8. **Slack Response**: Confirms ticket creation with Jira link

## 📚 Documentation

- **[Dashboard Documentation](DASHBOARD.md)** - Dashboard features and usage
- **[Database Models](DATABASE_MODELS.md)** - Database schema and functions
- **[Slack Integration](SLACK_INTEGRATION.md)** - Slack bot setup and commands
- **[Jira Integration](JIRA_INTEGRATION.md)** - Jira ticket management
- **[Email Assignment](EMAIL_ASSIGNMENT.md)** - Email notification system
- **[Employee Matching](EMPLOYEE_MATCHING.md)** - Employee selection algorithm
- **[Slack Workflow Simulation](SLACK_WORKFLOW_SIMULATION.md)** - Complete workflow demo

## 🚀 Quick Start

1. **Setup**: Follow installation steps above
2. **Configure**: Set up environment variables
3. **Initialize**: Run `python example_employee_task_management.py`
4. **Start**: Run `python run.py`
5. **Access**: Open `http://localhost:5000/dashboard`
6. **Test**: Run `python test_slack_workflow.py`

