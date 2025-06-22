# Slack Integration Guide

This document describes the enhanced Slack integration for the AI Task Assignment System, including slash commands, real-time messaging, and AI-powered task detection.

## Overview

The Slack integration provides multiple ways to create tasks and tickets:

1. **Slash Commands**: Direct commands like `/task`, `/bug`, `/story`
2. **Command Prefixes**: Message prefixes like `!bug`, `!story`, `!task`
3. **AI Detection**: Automatic detection of actionable messages using OpenAI GPT
4. **Bot Mentions**: Mention the bot to process task requests

## Setup Instructions

### 1. Slack App Configuration

1. **Create a Slack App** at https://api.slack.com/apps
2. **Configure OAuth & Permissions**:
   - Bot Token Scopes:
     - `chat:write` - Send messages
     - `channels:read` - Read channel messages
     - `users:read` - Read user information
     - `commands` - Add slash commands
   - User Token Scopes:
     - `chat:write` - Send messages as user

3. **Enable Socket Mode**:
   - Enable Socket Mode
   - Add app-level token with `connections:write` scope

4. **Configure Slash Commands**:
   - Go to "Slash Commands" in your app settings
   - Add the following commands:
     - `/task` - Create a general task
     - `/bug` - Report a bug
     - `/story` - Create a user story

5. **Subscribe to Events**:
   - Go to "Event Subscriptions"
   - Enable events and subscribe to:
     - `message.channels` - Monitor channel messages
     - `app_mention` - Handle bot mentions

6. **Install App to Workspace**:
   - Go to "Install App" and install to your workspace
   - Copy the Bot User OAuth Token and App-Level Token

### 2. Environment Configuration

Update your `.env` file with Slack credentials:

```env
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
SLACK_SIGNING_SECRET=your-signing-secret-here
```

### 3. Webhook Configuration

Set up the following webhook URLs in your Slack app:

- **Event Subscriptions Request URL**: `https://your-domain.com/slack/events`
- **Slash Commands Request URL**: `https://your-domain.com/slack/events`

## Usage Guide

### Slash Commands

#### `/task <description>`
Creates a general task.

**Example:**
```
/task Update the user documentation with new API endpoints
```

**Response:**
```
✅ Created task: Update the user documentation with new API endpoints
🔗 Jira: PROJ-123
📝 Description: Update the user documentation with new API endpoints
```

#### `/bug <description>`
Reports a bug or issue.

**Example:**
```
/bug Login page shows error 500 when using Safari browser
```

**Response:**
```
✅ Created bug: Login page shows error 500 when using Safari browser
🔗 Jira: PROJ-124
📝 Description: Login page shows error 500 when using Safari browser
```

#### `/story <description>`
Creates a user story.

**Example:**
```
/story As a user, I want to export my data to CSV format
```

**Response:**
```
✅ Created story: As a user, I want to export my data to CSV format
🔗 Jira: PROJ-125
📝 Description: As a user, I want to export my data to CSV format
```

### Command Prefixes

You can also use command prefixes in regular messages:

- `!bug <description>` - Report a bug
- `!story <description>` - Create a user story
- `!task <description>` - Create a task
- `!incident <description>` - Report an incident
- `!feature <description>` - Request a feature

**Example:**
```
!bug The search function is not working properly
```

### AI-Powered Detection

The bot automatically monitors all messages in configured channels and uses OpenAI GPT to detect actionable items.

#### What Gets Detected

**Bugs:**
- "The login button doesn't work"
- "Users are getting error messages"
- "The app crashes when I click submit"

**Features:**
- "We should add a dark mode option"
- "Can we implement user notifications?"
- "It would be great to have a mobile app"

**Tasks:**
- "Need to update the documentation"
- "Should review the security settings"
- "Need to test the new deployment"

**Incidents:**
- "The website is down"
- "Users can't access the system"
- "Critical service outage"

#### What Gets Ignored

The bot intelligently ignores non-actionable messages:

- Greetings: "Hi", "Hello", "Good morning"
- Acknowledgments: "Thanks", "OK", "Sure"
- Social chat: "How are you?", "See you later"
- Very short messages (less than 10 characters)

### Bot Mentions

Mention the bot to process specific text as a task request:

```
@TaskBot The user registration form needs validation
```

## Response Format

All responses include:

1. **Confirmation**: ✅ for success, ❌ for errors
2. **Task Type**: bug, story, task, incident, or feature
3. **Title**: Generated from the description
4. **Jira Link**: If Jira integration is configured
5. **Description**: Truncated version of the full description

## Database Integration

When a task is created via Slack:

1. **Task Record**: Created in the local database
2. **Jira Ticket**: Created in Jira (if configured)
3. **Source Tracking**: Marked as `slack_command` or `slack_ai_detected`
4. **User Tracking**: Records the Slack user ID

## Error Handling

The system handles various error scenarios:

- **Invalid Commands**: Provides usage instructions
- **Empty Descriptions**: Prompts for more information
- **API Failures**: Logs errors and provides user feedback
- **Network Issues**: Graceful degradation

## Configuration Options

### Message Filtering

You can customize what messages get processed by modifying the `_should_process_message` method in `SlackService`:

```python
def _should_process_message(self, text):
    # Customize filtering logic here
    if len(text.strip()) < 10:
        return False
    
    # Add custom patterns to ignore
    non_task_patterns = [
        r'^(hi|hello|hey)',
        r'^(thanks|thank you)',
        # Add more patterns
    ]
    
    # ... rest of the logic
```

### Priority Detection

Customize priority detection in the `_extract_priority` method:

```python
def _extract_priority(self, text):
    text_lower = text.lower()
    
    # Add custom priority keywords
    high_priority = ['urgent', 'asap', 'emergency', 'critical', 'blocker']
    low_priority = ['low priority', 'when possible', 'no rush', 'nice to have']
    
    # ... rest of the logic
```

### Jira Mapping

Customize how task types map to Jira issue types:

```python
jira_issue_type = {
    'bug': 'Bug',
    'story': 'Story',
    'task': 'Task',
    'incident': 'Incident',
    'feature': 'New Feature'
}.get(issue_type, 'Task')
```

## Monitoring and Logging

The system provides comprehensive logging:

- **Command Processing**: Logs all slash commands and their results
- **AI Detection**: Logs which messages were processed and why
- **Error Tracking**: Detailed error logs for debugging
- **Performance**: Response time tracking

### Log Examples

```
INFO: Slack command received: /task Update documentation
INFO: Created task: Update documentation (ID: 123)
INFO: Created Jira ticket: PROJ-126
INFO: Ignoring non-actionable message: "Hi everyone!"
```

## Troubleshooting

### Common Issues

1. **Commands Not Working**:
   - Check bot token permissions
   - Verify webhook URLs are correct
   - Ensure app is installed to workspace

2. **AI Detection Not Working**:
   - Verify OpenAI API key is valid
   - Check API quota and limits
   - Review message filtering logic

3. **Jira Integration Issues**:
   - Verify Jira credentials
   - Check project key exists
   - Ensure user has create permissions

### Debug Mode

Enable debug logging by setting:

```env
FLASK_ENV=development
```

This will provide detailed logs for troubleshooting.

## Security Considerations

1. **Token Security**: Never commit tokens to version control
2. **Request Validation**: All requests are validated using Slack's signing secret
3. **Rate Limiting**: Consider implementing rate limiting for API calls
4. **User Permissions**: Verify user permissions before creating tickets

## Future Enhancements

Potential improvements:

1. **Interactive Messages**: Add buttons for task management
2. **Thread Support**: Process messages in threads
3. **File Attachments**: Handle file uploads
4. **Custom Fields**: Support for custom Jira fields
5. **Workflow Integration**: Connect to existing workflows
6. **Multi-language Support**: Support for different languages
7. **Advanced AI**: More sophisticated task classification

## Support

For issues and questions:

1. Check the logs for error messages
2. Verify configuration settings
3. Test with simple commands first
4. Contact the development team

## API Reference

### Endpoints

- `POST /slack/events` - Main Slack events endpoint
- `POST /slack/commands` - Alternative commands endpoint

### Request Format

Slack sends requests in the following format:

```json
{
  "token": "verification_token",
  "team_id": "T123456",
  "api_app_id": "A123456",
  "event": {
    "type": "message",
    "channel": "C123456",
    "user": "U123456",
    "text": "message text",
    "ts": "1234567890.123456"
  }
}
```

### Response Format

Responses should be in Slack's expected format:

```json
{
  "response_type": "in_channel",
  "text": "Response message"
}
``` 