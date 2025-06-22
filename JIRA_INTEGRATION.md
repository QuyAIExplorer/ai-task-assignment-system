# Jira Integration - Ticket Creation

The Jira Integration module provides functionality to create and manage Jira tickets programmatically using the Jira REST API.

## Overview

The system supports:
- Creating tickets with different issue types (Bug, Story, Task, Feature, Incident, Epic)
- Automatic task type mapping
- Ticket assignment to specific users
- Retrieving ticket information
- Managing ticket status and transitions

## Core Components

### 1. JiraService Class

The main class that handles all Jira operations.

```python
from utils.jira_service import JiraService

jira_service = JiraService()
result = jira_service.create_jira_ticket(
    title='Fix Login Bug',
    task_type='bug',
    description='Users cannot log in on mobile devices',
    assignee='john.doe'
)
```

### 2. Simple Function Interface

For quick usage, use the simple function:

```python
from utils.jira_service import create_jira_ticket

result = create_jira_ticket(
    title='Implement New Feature',
    task_type='story',
    description='Add user dashboard functionality',
    assignee='alice.smith'
)
```

## Task Type Mapping

The system automatically maps task types to Jira issue types:

| Task Type | Jira Issue Type |
|-----------|-----------------|
| bug | Bug |
| story | Story |
| task | Task |
| feature | Story |
| incident | Bug |
| epic | Epic |
| subtask | Sub-task |

## API Endpoints

### Create Jira Ticket

```http
POST /api/jira/create-ticket
Content-Type: application/json

{
    "title": "Fix Login Button Not Working",
    "task_type": "bug",
    "description": "Users are unable to log in using the login button on the homepage.",
    "assignee": "john.doe"
}
```

Response:
```json
{
    "success": true,
    "issue_key": "PROJ-123",
    "url": "https://your-domain.atlassian.net/browse/PROJ-123",
    "issue_type": "Bug",
    "assignee": "john.doe"
}
```

### Get All Tickets

```http
GET /api/jira/tickets
```

Response:
```json
{
    "success": true,
    "tickets": [
        {
            "key": "PROJ-123",
            "summary": "Fix Login Button Not Working",
            "description": "Users are unable to log in...",
            "status": "To Do",
            "assignee": "John Doe",
            "issue_type": "Bug",
            "created": "2024-01-15T10:30:00.000Z",
            "updated": "2024-01-15T10:30:00.000Z",
            "url": "https://your-domain.atlassian.net/browse/PROJ-123"
        }
    ],
    "count": 1
}
```

### Get Specific Ticket

```http
GET /api/jira/tickets/PROJ-123
```

Response:
```json
{
    "success": true,
    "ticket": {
        "key": "PROJ-123",
        "summary": "Fix Login Button Not Working",
        "description": "Users are unable to log in...",
        "status": "To Do",
        "assignee": "John Doe",
        "issue_type": "Bug",
        "priority": "High",
        "created": "2024-01-15T10:30:00.000Z",
        "updated": "2024-01-15T10:30:00.000Z",
        "url": "https://your-domain.atlassian.net/browse/PROJ-123"
    }
}
```

### Assign Ticket

```http
POST /api/jira/tickets/PROJ-123/assign
Content-Type: application/json

{
    "assignee": "alice.smith"
}
```

Response:
```json
{
    "success": true,
    "message": "Ticket PROJ-123 assigned to alice.smith"
}
```

## Usage Examples

### Basic Ticket Creation

```python
from utils.jira_service import create_jira_ticket

# Create a bug ticket
result = create_jira_ticket(
    title='Fix Login Bug',
    task_type='bug',
    description='Users cannot log in on mobile devices',
    assignee='john.doe'
)

if result:
    print(f"Created ticket: {result['issue_key']}")
    print(f"URL: {result['url']}")
else:
    print("Failed to create ticket")
```

### Advanced Usage with JiraService

```python
from utils.jira_service import JiraService

jira_service = JiraService()

# Create different types of tickets
tickets = [
    {
        'title': 'Implement User Dashboard',
        'task_type': 'story',
        'description': 'Create a new dashboard for user analytics',
        'assignee': 'alice.smith'
    },
    {
        'title': 'Server Performance Issue',
        'task_type': 'incident',
        'description': 'Server response time is too slow',
        'assignee': 'devops.team'
    }
]

for ticket_data in tickets:
    result = jira_service.create_jira_ticket(**ticket_data)
    if result:
        print(f"Created {result['issue_type']}: {result['issue_key']}")
```

### Integration with Task Assignment

```python
from utils.jira_service import create_jira_ticket
from utils.employee_matcher import find_best_employee_for_task

# Find best employee for a task
employee = find_best_employee_for_task(
    task_type='bug',
    priority='high',
    required_domain='frontend'
)

if employee:
    # Create Jira ticket and assign to the employee
    result = create_jira_ticket(
        title='Fix Frontend Bug',
        task_type='bug',
        description='Critical bug in the frontend application',
        assignee=employee.email  # or employee.jira_username
    )
    
    if result:
        print(f"Ticket {result['issue_key']} assigned to {employee.name}")
```

## Configuration

### Environment Variables

Make sure these environment variables are set:

```bash
JIRA_SERVER=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your-api-token
JIRA_PROJECT_KEY=PROJ
```

### Customizing Task Type Mapping

You can customize the task type mapping in the JiraService class:

```python
jira_service = JiraService()
jira_service.task_type_mapping['custom_type'] = 'Custom Issue Type'
```

## Error Handling

The system includes comprehensive error handling:

- **Invalid Credentials**: Returns None if Jira authentication fails
- **Invalid Project Key**: Returns None if project doesn't exist
- **Invalid Assignee**: Returns None if assignee username is invalid
- **Network Errors**: Logs errors and returns None
- **API Rate Limits**: Handles rate limiting gracefully

## Logging

The system logs important events:

- Ticket creation with issue key
- Assignment changes
- API errors and warnings
- Authentication failures

## Testing

Run the example script to test the functionality:

```bash
python example_jira_ticket_creation.py
```

This will:
1. Test basic ticket creation for different task types
2. Test ticket assignment to users
3. Test error handling scenarios
4. Test bulk ticket creation
5. Demonstrate using the JiraService class directly

## Best Practices

1. **Use Descriptive Titles**: Make ticket titles clear and specific
2. **Provide Detailed Descriptions**: Include steps to reproduce, expected behavior, etc.
3. **Set Appropriate Task Types**: Use the correct task type for better organization
4. **Assign to Right People**: Use the employee matcher to find the best assignee
5. **Monitor Rate Limits**: Be aware of Jira API rate limits
6. **Handle Errors Gracefully**: Always check return values for None

## Troubleshooting

### Common Issues

1. **Authentication Failed**: Check Jira email and API token
2. **Project Not Found**: Verify JIRA_PROJECT_KEY is correct
3. **Assignee Not Found**: Ensure assignee username exists in Jira
4. **Invalid Issue Type**: Check if the issue type exists in your Jira project
5. **Rate Limit Exceeded**: Implement retry logic for bulk operations

### Debug Mode

Enable debug logging to see detailed API calls:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing Connection

Test your Jira connection:

```python
from utils.jira_service import JiraService

jira_service = JiraService()
try:
    # Try to get project info
    project = jira_service.jira.project(jira_service.project_key)
    print(f"Connected to project: {project.name}")
except Exception as e:
    print(f"Connection failed: {e}")
```

## Integration with Slack

The Jira integration works seamlessly with the Slack bot:

1. **Slack Commands**: `/bug`, `/story`, `/task` create Jira tickets
2. **AI Detection**: Automatically creates tickets for actionable messages
3. **Employee Assignment**: Uses employee matcher to assign tickets
4. **Notifications**: Sends ticket links back to Slack

Example Slack integration:
```python
# In slack_service.py
if task_type:
    jira_result = create_jira_ticket(
        title=task_title,
        task_type=task_type,
        description=message_text,
        assignee=best_employee.jira_username if best_employee else None
    )
    
    if jira_result:
        slack_client.chat_postMessage(
            channel=channel_id,
            text=f"✅ Created Jira ticket: {jira_result['url']}"
        )
```

## Future Enhancements

Potential improvements:

1. **Custom Fields**: Support for custom Jira fields
2. **Attachments**: Upload files to Jira tickets
3. **Comments**: Add comments to tickets
4. **Transitions**: Move tickets through workflows
5. **Bulk Operations**: Create multiple tickets efficiently
6. **Webhooks**: Receive Jira updates via webhooks
7. **Templates**: Use ticket templates for common issues
8. **Integration with Other Tools**: Connect with GitHub, GitLab, etc. 