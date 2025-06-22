# Database Models Documentation

## Overview

This document describes the SQLAlchemy models for Employee and Task management, along with supporting functions for common operations.

## Models

### Employee Model

```python
class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    expertise = db.Column(db.String(500), nullable=False)
    level = db.Column(db.String(20), nullable=False)  # junior, mid, senior
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
```

**Fields:**
- `id`: Primary key
- `name`: Employee name (required)
- `email`: Employee email (required, unique)
- `expertise`: String describing skills/expertise (required)
- `level`: Employee level - junior, mid, or senior (required)
- `is_available`: Boolean indicating if employee can take new tasks
- `created_at`: Timestamp when employee was created
- `updated_at`: Timestamp when employee was last updated

**Relationships:**
- `assigned_tasks`: One-to-many relationship with Task model

**Properties:**
- `current_tasks`: Returns list of active task IDs for this employee
- `to_dict()`: Converts employee to dictionary format

### Task Model

```python
class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Open')  # Open, In Progress, Closed
    assigned_employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
```

**Fields:**
- `id`: Primary key
- `title`: Task title (required)
- `description`: Task description
- `status`: Task status - Open, In Progress, or Closed (default: Open)
- `assigned_employee_id`: Foreign key to Employee (optional)
- `created_at`: Timestamp when task was created
- `updated_at`: Timestamp when task was last updated

**Relationships:**
- `assigned_employee`: Many-to-one relationship with Employee model

**Properties:**
- `to_dict()`: Converts task to dictionary format

## Supporting Functions

### Employee Management

#### `add_new_employee(name, email, expertise, level, is_available=True)`

Adds a new employee to the database with validation.

**Parameters:**
- `name` (str): Employee name
- `email` (str): Employee email (must be unique)
- `expertise` (str): Employee skills/expertise
- `level` (str): Employee level (junior, mid, senior)
- `is_available` (bool): Whether employee is available for tasks

**Returns:**
- Employee object if successful

**Raises:**
- ValueError: If email already exists or level is invalid

**Example:**
```python
try:
    employee = add_new_employee(
        name="Alice Johnson",
        email="alice@company.com",
        expertise="Frontend Development, React, JavaScript",
        level="senior"
    )
    print(f"Added employee: {employee.name}")
except ValueError as e:
    print(f"Error: {e}")
```

### Task Management

#### `assign_task_to_employee(task_id, employee_id)`

Assigns a task to an available employee.

**Parameters:**
- `task_id` (int): ID of the task to assign
- `employee_id` (int): ID of the employee to assign the task to

**Returns:**
- Updated Task object

**Raises:**
- ValueError: If task/employee not found, employee unavailable, or task already assigned

**Example:**
```python
try:
    task = assign_task_to_employee(task_id=1, employee_id=2)
    print(f"Assigned task '{task.title}' to employee")
except ValueError as e:
    print(f"Error: {e}")
```

#### `update_task_status(task_id, new_status)`

Updates the status of a task and manages employee availability.

**Parameters:**
- `task_id` (int): ID of the task to update
- `new_status` (str): New status (Open, In Progress, Closed)

**Returns:**
- Updated Task object

**Raises:**
- ValueError: If task not found or status is invalid

**Example:**
```python
try:
    task = update_task_status(task_id=1, new_status="Closed")
    print(f"Updated task #{task.id} to '{task.status}'")
except ValueError as e:
    print(f"Error: {e}")
```

### Query Functions

#### `get_available_employees()`

Returns all employees who are available for new tasks.

**Returns:**
- List of Employee objects

#### `get_employee_tasks(employee_id)`

Returns all tasks assigned to a specific employee.

**Parameters:**
- `employee_id` (int): ID of the employee

**Returns:**
- List of Task objects

#### `get_unassigned_tasks()`

Returns all tasks that are not assigned to any employee.

**Returns:**
- List of Task objects

#### `get_tasks_by_status(status)`

Returns all tasks with a specific status.

**Parameters:**
- `status` (str): Task status to filter by

**Returns:**
- List of Task objects

## Usage Examples

### Basic Operations

```python
# Add a new employee
employee = add_new_employee(
    name="Bob Smith",
    email="bob@company.com",
    expertise="Backend Development, Python, Django",
    level="mid"
)

# Create a task
task = Task(
    title="Fix Login Bug",
    description="Fix the login button issue"
)
db.session.add(task)
db.session.commit()

# Assign task to employee
assign_task_to_employee(task.id, employee.id)

# Update task status
update_task_status(task.id, "In Progress")
```

### Query Examples

```python
# Get all available employees
available_employees = get_available_employees()
for emp in available_employees:
    print(f"{emp.name} ({emp.level})")

# Get employee's tasks
employee_tasks = get_employee_tasks(employee.id)
for task in employee_tasks:
    print(f"Task: {task.title} - Status: {task.status}")

# Get unassigned tasks
unassigned = get_unassigned_tasks()
for task in unassigned:
    print(f"Unassigned: {task.title}")

# Get tasks by status
in_progress_tasks = get_tasks_by_status("In Progress")
for task in in_progress_tasks:
    print(f"In Progress: {task.title}")
```

### Model Properties

```python
# Convert to dictionary
employee_dict = employee.to_dict()
task_dict = task.to_dict()

# Get current tasks for employee
current_task_ids = employee.current_tasks
print(f"Employee has {len(current_task_ids)} active tasks")

# Access assigned employee
if task.assigned_employee:
    print(f"Task assigned to: {task.assigned_employee.name}")
```

## Database Schema

### Employees Table
```sql
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    expertise VARCHAR(500) NOT NULL,
    level VARCHAR(20) NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Tasks Table
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'Open',
    assigned_employee_id INTEGER REFERENCES employees(id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Validation Rules

### Employee Validation
- Email must be unique
- Level must be one of: junior, mid, senior
- Name and email are required
- Expertise is required

### Task Validation
- Title is required
- Status must be one of: Open, In Progress, Closed
- assigned_employee_id must reference a valid employee

### Assignment Validation
- Employee must be available (is_available = True)
- Task must not already be assigned
- Task and employee must exist

## Error Handling

All functions include proper error handling:

- **Validation errors**: Raise ValueError with descriptive messages
- **Database errors**: Rollback transactions and re-raise exceptions
- **Not found errors**: Raise ValueError for missing records

## Best Practices

1. **Always use transactions**: Functions handle database transactions automatically
2. **Validate input**: Functions validate all input parameters
3. **Handle exceptions**: Always wrap function calls in try-except blocks
4. **Check availability**: Verify employee availability before assignment
5. **Update status appropriately**: Task status affects employee availability 