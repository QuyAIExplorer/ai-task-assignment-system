from sqlalchemy import and_, or_, func, desc
from models.database import db, Employee, TaskAssignment, Task
from flask import current_app
import json
from datetime import datetime, timedelta


def find_best_employee_for_task(task_type, priority, required_domain,
                               estimated_hours=None, due_date=None, 
                               required_skills=None):
    """
    Simple function to find the best employee for a task.
    
    Args:
        task_type (str): Type of task (bug, incident, feature, task, story)
        priority (str): Priority level (low, medium, high)
        required_domain (str): Required domain expertise
        estimated_hours (float): Estimated hours for the task
        due_date (datetime): Task due date
        required_skills (list): List of required skills
        
    Returns:
        Employee or None: Best matching employee or None if no match found
    """
    matcher = EmployeeMatcher()
    return matcher.find_best_employee(
        task_type, priority, required_domain, 
        estimated_hours, due_date, required_skills
    )


class EmployeeMatcher:
    """Intelligent employee-task matching system"""
    
    def __init__(self):
        self.domain_expertise_map = {
            'frontend': ['javascript', 'react', 'vue', 'angular', 'html', 'css', 'ui', 'ux'],
            'backend': ['python', 'java', 'node.js', 'php', 'ruby', 'api', 'database', 'sql'],
            'devops': ['docker', 'kubernetes', 'aws', 'azure', 'ci/cd', 'deployment', 'infrastructure'],
            'mobile': ['ios', 'android', 'react native', 'flutter', 'mobile', 'app'],
            'data': ['python', 'sql', 'machine learning', 'ai', 'analytics', 'data science'],
            'security': ['security', 'authentication', 'authorization', 'encryption', 'penetration testing'],
            'qa': ['testing', 'qa', 'quality assurance', 'automation', 'selenium', 'test'],
            'design': ['ui', 'ux', 'design', 'figma', 'adobe', 'photoshop', 'illustrator']
        }
        
        self.priority_weights = {
            'high': 3,
            'medium': 2,
            'low': 1
        }
        
        self.task_type_weights = {
            'bug': 1.2,      # Bugs get higher priority
            'incident': 1.5, # Incidents get highest priority
            'feature': 1.0,  # Features get normal priority
            'task': 1.0,     # General tasks get normal priority
            'story': 1.0     # User stories get normal priority
        }
    
    def find_best_employee(self, task_type, priority, required_domain, 
                          estimated_hours=None, due_date=None, required_skills=None):
        """
        Find the best employee for a given task.
        
        Args:
            task_type (str): Type of task (bug, incident, feature, task, story)
            priority (str): Priority level (low, medium, high)
            required_domain (str): Required domain expertise
            estimated_hours (float): Estimated hours for the task
            due_date (datetime): Task due date
            required_skills (list): List of required skills
            
        Returns:
            Employee or None: Best matching employee or None if no match found
        """
        try:
            # Get available employees
            available_employees = self._get_available_employees()
            
            if not available_employees:
                current_app.logger.warning("No available employees found")
                return None
            
            # Score and rank employees
            scored_employees = []
            
            for employee in available_employees:
                score = self._calculate_employee_score(
                    employee, task_type, priority, required_domain, 
                    estimated_hours, due_date, required_skills
                )
                
                if score > 0:  # Only include employees with positive scores
                    scored_employees.append((employee, score))
            
            if not scored_employees:
                current_app.logger.warning(f"No qualified employees found for {task_type} in {required_domain}")
                return None
            
            # Sort by score (highest first) and return the best match
            scored_employees.sort(key=lambda x: x[1], reverse=True)
            best_employee, best_score = scored_employees[0]
            
            current_app.logger.info(
                f"Selected employee {best_employee.name} (score: {best_score:.2f}) "
                f"for {task_type} in {required_domain}"
            )
            
            return best_employee
            
        except Exception as e:
            current_app.logger.error(f"Error finding best employee: {str(e)}")
            return None
    
    def _get_available_employees(self):
        """Get all available employees with their current workload"""
        try:
            # Get employees who are available
            employees = Employee.query.filter_by(availability=True).all()
            
            # Calculate current workload for each employee
            for employee in employees:
                employee.current_workload = self._calculate_current_workload(employee)
            
            return employees
            
        except Exception as e:
            current_app.logger.error(f"Error getting available employees: {str(e)}")
            return []
    
    def _calculate_current_workload(self, employee):
        """Calculate current workload for an employee"""
        try:
            # Count active assignments
            active_assignments = TaskAssignment.query.filter(
                and_(
                    TaskAssignment.employee_id == employee.id,
                    TaskAssignment.status.in_(['assigned', 'accepted'])
                )
            ).count()
            
            # Get total estimated hours for active tasks
            active_tasks = db.session.query(func.sum(Task.estimated_hours)).join(
                TaskAssignment, Task.id == TaskAssignment.task_id
            ).filter(
                and_(
                    TaskAssignment.employee_id == employee.id,
                    TaskAssignment.status.in_(['assigned', 'accepted']),
                    Task.estimated_hours.isnot(None)
                )
            ).scalar() or 0
            
            return {
                'task_count': active_assignments,
                'estimated_hours': active_tasks
            }
            
        except Exception as e:
            current_app.logger.error(f"Error calculating workload for {employee.name}: {str(e)}")
            return {'task_count': 0, 'estimated_hours': 0}
    
    def _calculate_employee_score(self, employee, task_type, priority, required_domain,
                                estimated_hours=None, due_date=None, required_skills=None):
        """
        Calculate a score for how well an employee matches a task.
        Higher scores indicate better matches.
        """
        try:
            score = 0
            
            # Base score for being available
            score += 10
            
            # Domain expertise match
            domain_score = self._calculate_domain_expertise_score(employee, required_domain)
            score += domain_score * 20  # Domain expertise is heavily weighted
            
            # Skills match
            if required_skills:
                skills_score = self._calculate_skills_match_score(employee, required_skills)
                score += skills_score * 15
            
            # Workload balance (prefer employees with lower workload)
            workload_score = self._calculate_workload_score(employee)
            score += workload_score * 10
            
            # Priority handling capability
            priority_score = self._calculate_priority_handling_score(employee, priority, task_type)
            score += priority_score * 8
            
            # Experience with task type
            experience_score = self._calculate_task_type_experience_score(employee, task_type)
            score += experience_score * 5
            
            # Department alignment (bonus for matching department)
            department_score = self._calculate_department_alignment_score(employee, required_domain)
            score += department_score * 3
            
            return max(0, score)  # Ensure non-negative score
            
        except Exception as e:
            current_app.logger.error(f"Error calculating score for {employee.name}: {str(e)}")
            return 0
    
    def _calculate_domain_expertise_score(self, employee, required_domain):
        """Calculate how well an employee's skills match the required domain"""
        try:
            if not employee.skills:
                return 0
            
            # Parse employee skills
            employee_skills = self._parse_skills(employee.skills)
            
            # Get domain keywords
            domain_keywords = self.domain_expertise_map.get(required_domain.lower(), [])
            
            if not domain_keywords:
                return 0.5  # Default score for unknown domains
            
            # Count matching skills
            matches = 0
            for skill in employee_skills:
                for keyword in domain_keywords:
                    if keyword.lower() in skill.lower():
                        matches += 1
                        break
            
            # Calculate score based on match percentage
            if len(domain_keywords) > 0:
                return min(1.0, matches / len(domain_keywords))
            
            return 0
            
        except Exception as e:
            current_app.logger.error(f"Error calculating domain expertise: {str(e)}")
            return 0
    
    def _calculate_skills_match_score(self, employee, required_skills):
        """Calculate how well an employee's skills match the required skills"""
        try:
            if not employee.skills or not required_skills:
                return 0
            
            employee_skills = self._parse_skills(employee.skills)
            
            matches = 0
            for required_skill in required_skills:
                for employee_skill in employee_skills:
                    if required_skill.lower() in employee_skill.lower():
                        matches += 1
                        break
            
            return min(1.0, matches / len(required_skills))
            
        except Exception as e:
            current_app.logger.error(f"Error calculating skills match: {str(e)}")
            return 0
    
    def _calculate_workload_score(self, employee):
        """Calculate workload score (lower workload = higher score)"""
        try:
            workload = employee.current_workload
            
            # Score based on number of active tasks
            task_count_score = max(0, 1.0 - (workload['task_count'] / 5.0))
            
            # Score based on estimated hours
            hours_score = max(0, 1.0 - (workload['estimated_hours'] / 40.0))
            
            # Combine scores (weighted average)
            return (task_count_score * 0.6) + (hours_score * 0.4)
            
        except Exception as e:
            current_app.logger.error(f"Error calculating workload score: {str(e)}")
            return 0.5
    
    def _calculate_priority_handling_score(self, employee, priority, task_type):
        """Calculate how well an employee can handle the priority level"""
        try:
            # Get employee's current high-priority tasks
            high_priority_tasks = TaskAssignment.query.join(Task).filter(
                and_(
                    TaskAssignment.employee_id == employee.id,
                    TaskAssignment.status.in_(['assigned', 'accepted']),
                    Task.priority == 'high'
                )
            ).count()
            
            # If this is a high-priority task, prefer employees with fewer high-priority tasks
            if priority == 'high':
                return max(0, 1.0 - (high_priority_tasks / 3.0))
            
            # For medium/low priority, this is less important
            return 0.5
            
        except Exception as e:
            current_app.logger.error(f"Error calculating priority handling score: {str(e)}")
            return 0.5
    
    def _calculate_task_type_experience_score(self, employee, task_type):
        """Calculate employee's experience with the specific task type"""
        try:
            # Count previous tasks of the same type
            task_type_count = db.session.query(Task).join(TaskAssignment).filter(
                and_(
                    TaskAssignment.employee_id == employee.id,
                    Task.source.like(f'%{task_type}%')
                )
            ).count()
            
            # Score based on experience (more experience = higher score, but with diminishing returns)
            return min(1.0, task_type_count / 10.0)
            
        except Exception as e:
            current_app.logger.error(f"Error calculating task type experience: {str(e)}")
            return 0
    
    def _calculate_department_alignment_score(self, employee, required_domain):
        """Calculate department alignment score"""
        try:
            if not employee.department:
                return 0
            
            # Map domains to departments
            domain_department_map = {
                'frontend': ['engineering', 'development', 'frontend'],
                'backend': ['engineering', 'development', 'backend'],
                'devops': ['engineering', 'devops', 'infrastructure'],
                'mobile': ['engineering', 'development', 'mobile'],
                'data': ['data', 'analytics', 'engineering'],
                'security': ['security', 'engineering'],
                'qa': ['qa', 'testing', 'engineering'],
                'design': ['design', 'ux', 'ui']
            }
            
            expected_departments = domain_department_map.get(required_domain.lower(), [])
            
            if not expected_departments:
                return 0
            
            employee_dept = employee.department.lower()
            for expected_dept in expected_departments:
                if expected_dept in employee_dept:
                    return 1.0
            
            return 0
            
        except Exception as e:
            current_app.logger.error(f"Error calculating department alignment: {str(e)}")
            return 0
    
    def _parse_skills(self, skills_string):
        """Parse skills string into a list of skills"""
        try:
            if not skills_string:
                return []
            
            # Handle JSON format
            if skills_string.startswith('[') or skills_string.startswith('{'):
                try:
                    skills_data = json.loads(skills_string)
                    if isinstance(skills_data, list):
                        return skills_data
                    elif isinstance(skills_data, dict):
                        return list(skills_data.keys())
                except json.JSONDecodeError:
                    pass
            
            # Handle comma-separated format
            skills = [skill.strip() for skill in skills_string.split(',')]
            return [skill for skill in skills if skill]
            
        except Exception as e:
            current_app.logger.error(f"Error parsing skills: {str(e)}")
            return []
    
    def get_employee_recommendations(self, task_type, priority, required_domain, 
                                   required_skills=None, limit=5):
        """
        Get multiple employee recommendations for a task.
        
        Args:
            task_type (str): Type of task
            priority (str): Priority level
            required_domain (str): Required domain
            required_skills (list): Required skills
            limit (int): Maximum number of recommendations
            
        Returns:
            list: List of (employee, score) tuples, sorted by score
        """
        try:
            available_employees = self._get_available_employees()
            
            if not available_employees:
                return []
            
            scored_employees = []
            
            for employee in available_employees:
                score = self._calculate_employee_score(
                    employee, task_type, priority, required_domain,
                    required_skills=required_skills
                )
                
                if score > 0:
                    scored_employees.append((employee, score))
            
            # Sort by score and return top recommendations
            scored_employees.sort(key=lambda x: x[1], reverse=True)
            return scored_employees[:limit]
            
        except Exception as e:
            current_app.logger.error(f"Error getting employee recommendations: {str(e)}")
            return [] 