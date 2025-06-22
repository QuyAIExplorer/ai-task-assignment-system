# Dashboard Documentation

## Overview

The AI Task Assignment Dashboard provides real-time monitoring and management of tasks and employees through a modern web interface.

## Features

### Task Management Dashboard
- Real-time task display with status, assignments, and priority
- Auto-refresh every 30 seconds
- Color-coded status badges (Open, In Progress, Closed)
- Priority indicators (High, Medium, Low)

### Employee Management Dashboard
- Employee directory with expertise and availability
- Status monitoring (Free/Busy)
- Current task tracking
- Add employee form with validation

## API Endpoints

### GET /api/tasks
Returns all tasks with assignment information.

### GET /api/employees
Returns all employees with current task information.

### POST /api/employees
Creates a new employee.

### GET /api/dashboard/stats
Returns dashboard statistics.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize database:**
   ```bash
   python example_dashboard.py
   ```

3. **Start server:**
   ```bash
   python run.py
   ```

4. **Access dashboard:**
   Open `http://localhost:5000/dashboard`

## Usage

### Viewing Tasks
- Navigate to "Task Management" tab
- Tasks auto-refresh every 30 seconds
- Use "Refresh" button for manual updates

### Managing Employees
- Navigate to "Employee Management" tab
- Click "Add Employee" to create new employee
- Fill required fields and submit

### Status Indicators
- **Tasks**: Open (Blue), In Progress (Orange), Closed (Green)
- **Employees**: Free (Green), Busy (Red)
- **Priority**: High (Red), Medium (Orange), Low (Blue)

## Customization

### Auto-refresh Interval
Modify the JavaScript interval (default: 30 seconds):
```javascript
autoRefreshInterval = setInterval(() => {
    // refresh logic
}, 60000); // 60 seconds
```

### Styling
Customize colors via CSS variables:
```css
:root {
  --primary-color: #667eea;
  --success-color: #28a745;
  --danger-color: #dc3545;
}
```

## Integration

The dashboard integrates with:
- **Slack**: Tasks created via Slack appear in dashboard
- **Jira**: Ticket creation and status synchronization
- **Email**: Assignment notifications

## Troubleshooting

### Common Issues
1. **Dashboard not loading**: Check Flask server and database
2. **API errors**: Verify database schema and environment variables
3. **Auto-refresh issues**: Check browser console for JavaScript errors

### Debug Mode
Enable Flask debug mode for detailed errors:
```python
app.config['DEBUG'] = True
```

## Future Enhancements

- Real-time WebSocket updates
- Advanced filtering and search
- Bulk operations
- Export functionality
- Mobile app
- Advanced analytics 