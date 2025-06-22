# Slack Workflow Simulation

## Overview

This simulation demonstrates the complete end-to-end workflow when a Slack message is received that requires task creation and assignment.

## Workflow Steps

### 1. Slack Message Reception
**Input**: "We've identified a critical bug impacting the checkout process. Our team is actively investigating and working on a fix."

### 2. AI Task Intent Detection
- **Service**: `TaskIntentDetector`
- **Process**: Analyzes message using GPT to determine:
  - Intent: `actionable` or `non-actionable`
  - Task Type: `bug`, `feature`, `story`, `incident`
  - Priority: `High`, `Medium`, `Low`
  - Confidence: 0.0-1.0 score

**Expected Result**:
```json
{
  "intent": "actionable",
  "confidence": 0.95,
  "task_type": "bug",
  "priority": "High"
}
```

### 3. Task Creation
- **Service**: Database models
- **Process**: Creates new Task record with:
  - Title: "Critical Bug: Checkout Process Issue"
  - Description: Original Slack message
  - Status: "Open"
  - Priority: Determined by AI
  - Source: "slack"

### 4. Employee Matching
- **Service**: `EmployeeMatcher`
- **Process**: Finds best employee based on:
  - Task type (bug)
  - Priority (High)
  - Required domain expertise
  - Availability status
  - Skill level

**Expected Match**: Employee with checkout/payment processing expertise

### 5. Task Assignment
- **Service**: Database functions
- **Process**: 
  - Assigns task to selected employee
  - Updates task status to "In Progress"
  - Updates employee availability

### 6. Jira Ticket Creation
- **Service**: `JiraService`
- **Process**: Creates Jira ticket with:
  - Title and description
  - Task type mapping
  - Priority level
  - Assignee

**Expected Result**:
```json
{
  "issue_key": "PROJ-123",
  "url": "https://company.atlassian.net/browse/PROJ-123",
  "assignee": "alice@company.com"
}
```

### 7. Email Notification
- **Service**: `EmailService`
- **Process**: Sends assignment email with:
  - Task details
  - Jira ticket link
  - Assignment information

### 8. Dashboard Updates
- **Process**: Updates real-time dashboards:
  - Task dashboard shows new task
  - Employee dashboard shows assignment
  - Statistics updated

### 9. Slack Response
- **Service**: `SlackService`
- **Process**: Sends confirmation message:
  - "Bug ticket created with title 'Critical Bug: Checkout Process Issue'. You can view the ticket on Jira: [URL]"

## Running the Simulation

### Prerequisites
1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables (see `.env.example`)
3. Initialize database: `python example_employee_task_management.py`

### Execute Simulation
```bash
python test_slack_workflow.py
```

### Expected Output
```
🚀 Slack Workflow Simulation
============================================================
Setting up sample employees...
   ✅ Added: Alice Johnson (senior)
   ✅ Added: Bob Smith (senior)
   ✅ Added: Carol Davis (senior)
   ✅ Added: David Wilson (mid)

============================================================
🚀 SIMULATING SLACK WORKFLOW
============================================================

📨 SLACK MESSAGE RECEIVED:
   'We've identified a critical bug impacting the checkout process...'

🤖 STEP 1: AI TASK INTENT DETECTION
----------------------------------------
   ✅ Intent detected: actionable
   ✅ Confidence: 0.95
   ✅ Task type: bug
   ✅ Priority: High
   ✅ Message is actionable - proceeding with task creation

📝 STEP 2: TASK CREATION
----------------------------------------
   ✅ Task created: #1 - Critical Bug: Checkout Process Issue
   ✅ Status: Open
   ✅ Priority: High

👥 STEP 3: EMPLOYEE MATCHING
----------------------------------------
   ✅ Best match found: Alice Johnson
   ✅ Expertise: Frontend Development, React, JavaScript, UI/UX, Checkout Process
   ✅ Level: senior
   ✅ Available: True

🔗 STEP 4: TASK ASSIGNMENT
----------------------------------------
   ✅ Task assigned to: Alice Johnson
   ✅ Task status updated to: In Progress

🎫 STEP 5: JIRA TICKET CREATION
----------------------------------------
   ✅ Jira ticket created: PROJ-123
   ✅ Jira URL: https://company.atlassian.net/browse/PROJ-123
   ✅ Assignee: alice@company.com

📧 STEP 6: EMAIL NOTIFICATION
----------------------------------------
   ✅ Email sent to: alice@company.com
   ✅ Subject: New Task Assignment: Critical Bug: Checkout Process Issue
   ✅ Status: sent

📊 STEP 7: DASHBOARD UPDATES
----------------------------------------
   ✅ Task dashboard updated with new task
   ✅ Employee dashboard updated - Alice Johnson now busy
   ✅ Real-time updates sent to connected clients
   📈 Current stats:
      - Total tasks: 1
      - Open tasks: 0
      - In progress: 1
      - Available employees: 3

💬 STEP 8: SLACK RESPONSE
----------------------------------------
   ✅ Slack response sent:
      'Bug ticket created with title 'Critical Bug: Checkout Process Issue'. You can view the ticket on Jira: https://company.atlassian.net/browse/PROJ-123'
   ✅ Channel: #general
   ✅ Status: sent

============================================================
📋 WORKFLOW SUMMARY
============================================================
✅ Task created: #1 - Critical Bug: Checkout Process Issue
✅ Assigned to: Alice Johnson (alice@company.com)
✅ Jira ticket: PROJ-123
✅ Email notification sent
✅ Dashboards updated
✅ Slack response sent

🎯 Workflow completed successfully!
   The critical checkout bug has been properly tracked and assigned.
```

## Configuration

### Environment Variables
```bash
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Jira Configuration
JIRA_URL=https://company.atlassian.net
JIRA_USERNAME=your_jira_username
JIRA_API_TOKEN=your_jira_api_token
JIRA_PROJECT_KEY=PROJ

# Email Configuration
GMAIL_APP_PASSWORD=your_gmail_app_password
SENDER_EMAIL=notifications@company.com

# Slack Configuration
SLACK_BOT_TOKEN=your_slack_bot_token
SLACK_SIGNING_SECRET=your_slack_signing_secret
```

### Sample Employees
The simulation creates employees with relevant expertise:
- **Alice Johnson**: Frontend, React, JavaScript, UI/UX, Checkout Process
- **Bob Smith**: Backend, Python, Django, Payment Processing, API
- **Carol Davis**: DevOps, Infrastructure, Database, Monitoring
- **David Wilson**: Mobile Development, iOS, Android, React Native

## Error Handling

The simulation includes comprehensive error handling:
- **Graceful degradation**: Continues workflow even if some services fail
- **Detailed logging**: Shows success/failure for each step
- **Transaction rollback**: Database operations are atomic
- **Service isolation**: One service failure doesn't break others

## Integration Points

### Services Used
1. **TaskIntentDetector**: OpenAI GPT integration
2. **EmployeeMatcher**: SQLAlchemy ORM queries
3. **JiraService**: Jira REST API
4. **EmailService**: Gmail SMTP
5. **SlackService**: Slack Web API
6. **Database**: SQLAlchemy models and functions

### Data Flow
```
Slack Message → AI Detection → Database → Employee Matching → 
Task Assignment → Jira Creation → Email Notification → 
Dashboard Updates → Slack Response
```

## Testing Different Scenarios

### Modify the Slack Message
Edit `slack_message` in `simulate_slack_workflow()` to test different scenarios:

```python
# Feature request
slack_message = "We need to add a new payment method to the checkout process."

# Incident
slack_message = "The website is down and customers can't access the platform."

# Non-actionable
slack_message = "Great job everyone on the latest release!"
```

### Test Employee Availability
Modify employee availability in `setup_sample_data()` to test different assignment scenarios.

### Test Priority Levels
The AI detection will automatically determine priority based on message content and keywords.

## Monitoring and Debugging

### Logs
Each step provides detailed logging with:
- ✅ Success indicators
- ❌ Error messages
- 📊 Statistics and metrics

### Database State
Check the database after simulation:
```python
# View all tasks
tasks = Task.query.all()
for task in tasks:
    print(f"#{task.id}: {task.title} -> {task.assigned_employee.name}")

# View employee status
employees = Employee.query.all()
for emp in employees:
    print(f"{emp.name}: Available={emp.is_available}, Tasks={len(emp.current_tasks)}")
```

### API Responses
Each service returns structured responses that can be inspected for debugging.

## Future Enhancements

1. **Real-time WebSocket updates** for dashboard
2. **Slack thread responses** instead of new messages
3. **Priority escalation** for critical issues
4. **Automated testing** with different message types
5. **Performance metrics** and timing analysis
6. **Integration with monitoring tools** (Sentry, DataDog) 