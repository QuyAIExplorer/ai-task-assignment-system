# Employee Matching System

The Employee Matching System provides intelligent task-to-employee assignment based on multiple criteria including skills, availability, workload, and domain expertise.

## Overview

The system uses a sophisticated scoring algorithm to find the best employee for each task, considering:

- **Domain Expertise**: Matches employee skills to required domains (frontend, backend, devops, etc.)
- **Workload Balance**: Prefers employees with lower current workload
- **Priority Handling**: Considers employee's ability to handle high-priority tasks
- **Department Alignment**: Gives preference to employees in relevant departments
- **Task Type Experience**: Considers employee's experience with similar task types

## Core Components

### 1. EmployeeMatcher Class

The main class that handles intelligent employee matching.

```python
from utils.employee_matcher import EmployeeMatcher

matcher = EmployeeMatcher()
best_employee = matcher.find_best_employee(
    task_type='bug',
    priority='high',
    required_domain='frontend',
    estimated_hours=4.0,
    required_skills=['javascript', 'react']
)
```

### 2. Simple Function Interface

For quick usage, use the simple function:

```python
from utils.employee_matcher import find_best_employee_for_task

best_employee = find_best_employee_for_task(
    task_type='feature',
    priority='medium',
    required_domain='backend'
)
```

## Supported Domains

The system recognizes the following domains and their associated skills:

| Domain | Keywords |
|--------|----------|
| frontend | javascript, react, vue, angular, html, css, ui, ux |
| backend | python, java, node.js, php, ruby, api, database, sql |
| devops | docker, kubernetes, aws, azure, ci/cd, deployment, infrastructure |
| mobile | ios, android, react native, flutter, mobile, app |
| data | python, sql, machine learning, ai, analytics, data science |
| security | security, authentication, authorization, encryption, penetration testing |
| qa | testing, qa, quality assurance, automation, selenium, test |
| design | ui, ux, design, figma, adobe, photoshop, illustrator |

## Scoring Algorithm

The system calculates a score for each employee based on:

1. **Base Score** (10 points): Available employees get base points
2. **Domain Expertise** (20 points): How well skills match the required domain
3. **Skills Match** (15 points): Direct skills matching if specified
4. **Workload Balance** (10 points): Prefer employees with lower workload
5. **Priority Handling** (8 points): Ability to handle task priority
6. **Task Type Experience** (5 points): Experience with similar task types
7. **Department Alignment** (3 points): Department relevance bonus

## API Endpoints

### Find Best Employee

```http
POST /api/employee-matching/find-best
Content-Type: application/json

{
    "task_type": "bug",
    "priority": "high",
    "required_domain": "frontend",
    "estimated_hours": 4.0,
    "required_skills": ["javascript", "react"]
}
```

Response:
```json
{
    "success": true,
    "employee": {
        "id": 1,
        "name": "Alice Johnson",
        "email": "alice@company.com",
        "department": "Frontend Engineering",
        "skills": "javascript,react,vue,html,css,ui design"
    }
}
```

### Get Employee Recommendations

```http
POST /api/employee-matching/recommendations
Content-Type: application/json

{
    "task_type": "feature",
    "priority": "medium",
    "required_domain": "backend",
    "required_skills": ["python", "api"],
    "limit": 3
}
```

Response:
```json
{
    "success": true,
    "recommendations": [
        {
            "id": 2,
            "name": "Bob Smith",
            "email": "bob@company.com",
            "department": "Backend Engineering",
            "skills": "python,java,node.js,api,database,sql",
            "score": 85.5
        }
    ]
}
```

### Assign Task with Matching

```http
POST /api/employee-matching/assign-task
Content-Type: application/json

{
    "title": "Fix Login Bug",
    "description": "Users cannot log in on mobile devices",
    "task_type": "bug",
    "priority": "high",
    "required_domain": "frontend",
    "estimated_hours": 2.0,
    "required_skills": ["javascript", "react"]
}
```

Response:
```json
{
    "success": true,
    "assignment": {
        "id": 1,
        "task_id": 1,
        "employee_id": 1,
        "assigned_by": "AI Matcher",
        "status": "assigned",
        "notes": "Assigned by intelligent matching system. Task type: bug, Domain: frontend"
    },
    "employee": {
        "id": 1,
        "name": "Alice Johnson",
        "email": "alice@company.com",
        "department": "Frontend Engineering"
    },
    "task": {
        "id": 1,
        "title": "Fix Login Bug",
        "description": "Users cannot log in on mobile devices",
        "priority": "high",
        "status": "assigned"
    }
}
```

## Usage Examples

### Basic Usage

```python
from utils.employee_matcher import find_best_employee_for_task

# Find best employee for a bug fix
employee = find_best_employee_for_task(
    task_type='bug',
    priority='high',
    required_domain='frontend'
)

if employee:
    print(f"Best match: {employee.name} ({employee.department})")
else:
    print("No suitable employee found")
```

### Advanced Usage with EmployeeMatcher

```python
from utils.employee_matcher import EmployeeMatcher

matcher = EmployeeMatcher()

# Get multiple recommendations
recommendations = matcher.get_employee_recommendations(
    task_type='feature',
    priority='medium',
    required_domain='backend',
    required_skills=['python', 'api'],
    limit=5
)

for employee, score in recommendations:
    print(f"{employee.name}: {score:.2f}")
```

### Integration with Task Assignment Agent

```python
from agents.task_assignment_agent import TaskAssignmentAgent

agent = TaskAssignmentAgent()

task_data = {
    'title': 'Implement User Dashboard',
    'description': 'Create a new dashboard for user analytics',
    'task_type': 'feature',
    'priority': 'medium',
    'required_domain': 'frontend',
    'required_skills': ['react', 'javascript'],
    'estimated_hours': 8.0
}

assignment = agent.assign_task(task_data)
```

## Configuration

### Customizing Domain Keywords

You can customize the domain expertise mapping in the `EmployeeMatcher` class:

```python
matcher = EmployeeMatcher()
matcher.domain_expertise_map['custom_domain'] = ['skill1', 'skill2', 'skill3']
```

### Adjusting Scoring Weights

Modify the scoring weights in the `_calculate_employee_score` method:

```python
# Domain expertise is heavily weighted
score += domain_score * 20

# Skills match
score += skills_score * 15

# Workload balance
score += workload_score * 10
```

## Database Requirements

The system requires the following database models:

- **Employee**: Contains employee information, skills, department, availability
- **Task**: Contains task information, priority, type, domain
- **TaskAssignment**: Links tasks to employees with assignment details

### Employee Model Fields

- `id`: Primary key
- `name`: Employee name
- `email`: Employee email
- `department`: Department name
- `skills`: Comma-separated or JSON skills list
- `availability`: Boolean availability status

### Task Model Fields

- `id`: Primary key
- `title`: Task title
- `description`: Task description
- `priority`: Priority level (low, medium, high)
- `source`: Task source (manual, slack, jira, etc.)
- `estimated_hours`: Estimated completion time
- `due_date`: Task due date

## Error Handling

The system includes comprehensive error handling:

- **No Available Employees**: Returns None if no employees are available
- **No Qualified Employees**: Returns None if no employees match the requirements
- **Database Errors**: Logs errors and returns None
- **Invalid Input**: Validates required fields and returns appropriate errors

## Logging

The system logs important events:

- Employee selection with scores
- Assignment decisions
- Errors and warnings
- Workload optimization suggestions

## Testing

Run the example script to test the functionality:

```bash
python example_employee_matching.py
```

This will:
1. Create sample employees
2. Test various task types and domains
3. Demonstrate workload consideration
4. Show multiple recommendations

## Best Practices

1. **Keep Skills Updated**: Regularly update employee skills for accurate matching
2. **Monitor Workload**: Use workload optimization to prevent overloading
3. **Review Assignments**: Periodically review AI assignments for quality
4. **Customize Domains**: Adjust domain keywords based on your organization's needs
5. **Test Thoroughly**: Test with various task types and priorities

## Troubleshooting

### Common Issues

1. **No Employees Found**: Check employee availability status
2. **Poor Matches**: Review employee skills and domain keywords
3. **High Workload**: Use workload optimization features
4. **Database Errors**: Check database connectivity and model definitions

### Debug Mode

Enable debug logging to see detailed scoring:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

Potential improvements:

1. **Machine Learning**: Use ML models for better skill matching
2. **Performance Metrics**: Track assignment success rates
3. **Team Dynamics**: Consider team collaboration preferences
4. **Time Zones**: Account for employee time zones
5. **Skill Levels**: Add skill proficiency levels
6. **Learning Paths**: Suggest skill development opportunities 