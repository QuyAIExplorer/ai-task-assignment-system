# Email Assignment System

The Email Assignment System provides functionality to send task assignment notifications via email using Gmail SMTP.

## Overview

The system supports:
- Sending assignment emails with task details and Jira links
- Using Gmail SMTP server with app password authentication
- Professional email formatting
- Error handling and logging
- Integration with the task assignment workflow

## Core Components

### 1. send_assignment_email Function

The main function that sends assignment emails using Gmail SMTP.

```python
from utils.email_service import send_assignment_email

success = send_assignment_email(
    employee_email='employee@company.com',
    task_title='Fix Login Bug',
    task_description='Users cannot log in on mobile devices',
    jira_url='https://your-domain.atlassian.net/browse/PROJ-123'
)
```

### 2. Enhanced EmailService Class

The EmailService class has been enhanced to support Jira assignments:

```python
from utils.email_service import EmailService

email_service = EmailService()

# Send Jira assignment email
success = email_service.send_jira_assignment_notification(
    employee_email='employee@company.com',
    task_title='Implement New Feature',
    task_description='Add user dashboard functionality',
    jira_url='https://your-domain.atlassian.net/browse/PROJ-124'
)
```

## Email Configuration

### Gmail Setup

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
3. **Set Environment Variable**:
   ```bash
   GMAIL_APP_PASSWORD=your-16-character-app-password
   ```

### Environment Variables

Required environment variables:

```bash
# Gmail Configuration
GMAIL_APP_PASSWORD=your-app-password

# Optional: Override default sender
SMTP_USERNAME=nguyencongquy23012002@gmail.com
```

## Email Format

### Subject Line
```
New Task Assigned: [task_title]
```

### Email Body
```
Hello,

You have been assigned a new task:

Task Title: [task_title]

Description:
[task_description]

Jira Ticket: [jira_url]

Please review the task details and update the status in Jira.

Best regards,
AI Task Assignment System
```

## API Endpoints

### Send Assignment Email

```http
POST /api/email/send-assignment
Content-Type: application/json

{
    "employee_email": "employee@company.com",
    "task_title": "Fix Login Bug",
    "task_description": "Users cannot log in on mobile devices",
    "jira_url": "https://your-domain.atlassian.net/browse/PROJ-123"
}
```

Response:
```json
{
    "success": true,
    "message": "Assignment email sent to employee@company.com"
}
```

### Send Jira Assignment Email

```http
POST /api/email/send-jira-assignment
Content-Type: application/json

{
    "employee_email": "employee@company.com",
    "task_title": "Implement User Dashboard",
    "task_description": "Create a new dashboard for user analytics",
    "jira_url": "https://your-domain.atlassian.net/browse/PROJ-124"
}
```

Response:
```json
{
    "success": true,
    "message": "Jira assignment email sent to employee@company.com"
}
```

## Usage Examples

### Basic Usage

```python
from utils.email_service import send_assignment_email

# Send assignment email
success = send_assignment_email(
    employee_email='john.doe@company.com',
    task_title='Fix Database Performance Issue',
    task_description='Database queries are taking too long to execute. Need to optimize the slow queries.',
    jira_url='https://your-domain.atlassian.net/browse/PROJ-125'
)

if success:
    print("Assignment email sent successfully!")
else:
    print("Failed to send assignment email")
```

### Integration with Employee Matching

```python
from utils.email_service import send_assignment_email
from utils.employee_matcher import find_best_employee_for_task
from utils.jira_service import create_jira_ticket

# Find best employee for a task
employee = find_best_employee_for_task(
    task_type='bug',
    priority='high',
    required_domain='frontend'
)

if employee:
    # Create Jira ticket
    jira_result = create_jira_ticket(
        title='Fix Frontend Bug',
        task_type='bug',
        description='Critical bug in the frontend application',
        assignee=employee.email
    )
    
    if jira_result:
        # Send assignment email
        send_assignment_email(
            employee_email=employee.email,
            task_title='Fix Frontend Bug',
            task_description='Critical bug in the frontend application',
            jira_url=jira_result['url']
        )
```

### Using EmailService Class

```python
from utils.email_service import EmailService

email_service = EmailService()

# Send different types of notifications
email_service.send_jira_assignment_notification(
    employee_email='alice.smith@company.com',
    task_title='Code Review - Authentication Module',
    task_description='Please review the new user authentication module implementation.',
    jira_url='https://your-domain.atlassian.net/browse/PROJ-126'
)

email_service.send_task_completion_notification(
    manager_email='manager@company.com',
    task_title='User Dashboard Implementation',
    employee_name='Alice Smith'
)
```

## Error Handling

The system includes comprehensive error handling:

- **Invalid Email Address**: Returns False for malformed email addresses
- **SMTP Authentication Failed**: Returns False if Gmail credentials are invalid
- **Network Errors**: Returns False for connection issues
- **Missing Configuration**: Returns False if GMAIL_APP_PASSWORD is not set

### Common Error Scenarios

1. **GMAIL_APP_PASSWORD not configured**:
   ```
   GMAIL_APP_PASSWORD not configured
   ```

2. **Invalid email address**:
   ```
   Failed to send assignment email: Invalid email address
   ```

3. **Authentication failed**:
   ```
   Failed to send assignment email: Authentication failed
   ```

## Logging

The system logs important events:

- Successful email sends with recipient and task details
- Failed email attempts with error messages
- Configuration issues
- SMTP connection problems

### Log Examples

```
INFO: Assignment email sent to john.doe@company.com for task: Fix Login Bug
ERROR: Failed to send assignment email: Authentication failed
ERROR: GMAIL_APP_PASSWORD not configured
```

## Testing

Run the example script to test the functionality:

```bash
python example_email_assignment.py
```

This will:
1. Test basic assignment email sending
2. Test different task types and descriptions
3. Test EmailService class integration
4. Test error handling scenarios
5. Test bulk email sending
6. Show email content formatting

## Best Practices

1. **Use App Passwords**: Never use your main Gmail password
2. **Test Email Addresses**: Always test with valid email addresses
3. **Handle Errors**: Always check return values for False
4. **Monitor Logs**: Check logs for email delivery issues
5. **Rate Limiting**: Be aware of Gmail's sending limits
6. **Professional Content**: Use clear, professional email content

## Troubleshooting

### Common Issues

1. **Authentication Failed**:
   - Check if 2FA is enabled on Gmail
   - Verify app password is correct
   - Ensure GMAIL_APP_PASSWORD is set

2. **Email Not Received**:
   - Check spam/junk folder
   - Verify recipient email address
   - Check Gmail sending limits

3. **SMTP Connection Error**:
   - Check internet connection
   - Verify Gmail SMTP settings
   - Check firewall settings

### Debug Mode

Enable debug logging to see detailed SMTP communication:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing Connection

Test your Gmail connection:

```python
from utils.email_service import send_assignment_email

# Test with a simple email
success = send_assignment_email(
    employee_email='test@example.com',
    task_title='Test Task',
    task_description='This is a test email',
    jira_url='https://example.com'
)

if success:
    print("Gmail connection working!")
else:
    print("Gmail connection failed")
```

## Integration with Other Systems

### Slack Integration

The email system works with Slack notifications:

```python
# Send both Slack and email notifications
slack_client.chat_postMessage(
    channel=channel_id,
    text=f"✅ Task assigned to {employee.name}: {jira_result['url']}"
)

send_assignment_email(
    employee_email=employee.email,
    task_title=task_title,
    task_description=task_description,
    jira_url=jira_result['url']
)
```

### Jira Integration

Seamless integration with Jira ticket creation:

```python
# Create Jira ticket and send email
jira_result = create_jira_ticket(
    title=task_title,
    task_type=task_type,
    description=task_description,
    assignee=employee.email
)

if jira_result:
    send_assignment_email(
        employee_email=employee.email,
        task_title=task_title,
        task_description=task_description,
        jira_url=jira_result['url']
    )
```

## Security Considerations

1. **App Passwords**: Use app passwords instead of main passwords
2. **Environment Variables**: Store credentials in environment variables
3. **Email Validation**: Validate email addresses before sending
4. **Rate Limiting**: Implement rate limiting for bulk emails
5. **Logging**: Avoid logging sensitive information

## Future Enhancements

Potential improvements:

1. **HTML Emails**: Support for rich HTML email content
2. **Email Templates**: Customizable email templates
3. **Attachments**: Support for file attachments
4. **Email Tracking**: Track email open rates and clicks
5. **Bulk Operations**: Efficient bulk email sending
6. **Email Scheduling**: Schedule emails for later delivery
7. **Multiple Providers**: Support for other email providers
8. **Email Analytics**: Track email delivery and engagement 