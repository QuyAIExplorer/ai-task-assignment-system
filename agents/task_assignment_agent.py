import autogen
from flask import current_app
from models.database import db, Employee, Task, TaskAssignment
from utils.email_service import EmailService
from utils.employee_matcher import EmployeeMatcher
import json


class TaskAssignmentAgent:
    """Intelligent task assignment agent using employee matching"""
    
    def __init__(self):
        self.employee_matcher = EmployeeMatcher()
        self.email_service = EmailService()
        
        # Keep AutoGen for complex decision making if needed
        self.config_list = [
            {
                'model': 'gpt-3.5-turbo',
                'api_key': current_app.config['OPENAI_API_TOKEN']
            }
        ]
        
        self.manager_agent = autogen.AssistantAgent(
            name="TaskManager",
            system_message="""You are a task manager responsible for analyzing tasks 
            and determining the best employee assignment based on skills, availability, 
            and workload. You make final assignment decisions.""",
            llm_config={"config_list": self.config_list}
        )
        
        self.user_proxy = autogen.UserProxyAgent(
            name="UserProxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={"work_dir": "coding"},
            llm_config={"config_list": self.config_list}
        )
    
    def assign_task(self, task_data):
        """Assign a task to the best available employee using intelligent matching"""
        try:
            # Create task in database
            task = Task(
                title=task_data.get('title', 'Untitled Task'),
                description=task_data.get('description', ''),
                priority=task_data.get('priority', 'medium'),
                source=task_data.get('source', 'manual'),
                source_id=task_data.get('source_id'),
                created_by=task_data.get('created_by', 'system'),
                estimated_hours=task_data.get('estimated_hours'),
                due_date=task_data.get('due_date')
            )
            db.session.add(task)
            db.session.commit()
            
            # Determine task type and domain from the task data
            task_type = self._determine_task_type(task_data)
            required_domain = self._determine_required_domain(task_data)
            required_skills = self._extract_required_skills(task_data)
            
            # Find best employee using intelligent matching
            best_employee = self.employee_matcher.find_best_employee(
                task_type=task_type,
                priority=task.priority,
                required_domain=required_domain,
                estimated_hours=task.estimated_hours,
                due_date=task.due_date,
                required_skills=required_skills
            )
            
            if best_employee:
                # Create assignment
                assignment = TaskAssignment(
                    task_id=task.id,
                    employee_id=best_employee.id,
                    assigned_by='AI Matcher',
                    notes=f"Assigned by intelligent matching system. "
                          f"Task type: {task_type}, Domain: {required_domain}"
                )
                db.session.add(assignment)
                
                # Update task status
                task.status = 'assigned'
                db.session.commit()
                
                # Send notification
                self.email_service.send_task_assignment_notification(
                    best_employee.email,
                    task.title,
                    task.description
                )
                
                current_app.logger.info(
                    f"Task '{task.title}' assigned to {best_employee.name} "
                    f"using intelligent matching"
                )
                
                return assignment
            else:
                # Fallback to AutoGen if no match found
                current_app.logger.warning(
                    f"No suitable employee found for task '{task.title}'. "
                    f"Falling back to AutoGen assignment."
                )
                return self._fallback_autogen_assignment(task, task_data)
            
        except Exception as e:
            current_app.logger.error(f"Task assignment failed: {str(e)}")
            return None
    
    def _determine_task_type(self, task_data):
        """Determine task type from task data"""
        # Check if task type is explicitly provided
        if task_data.get('task_type'):
            return task_data['task_type']
        
        # Infer from source or title
        source = task_data.get('source', '').lower()
        title = task_data.get('title', '').lower()
        
        if 'bug' in source or 'bug' in title:
            return 'bug'
        elif 'incident' in source or 'incident' in title:
            return 'incident'
        elif 'feature' in source or 'feature' in title:
            return 'feature'
        elif 'story' in source or 'story' in title:
            return 'story'
        else:
            return 'task'
    
    def _determine_required_domain(self, task_data):
        """Determine required domain from task data"""
        # Check if domain is explicitly provided
        if task_data.get('domain'):
            return task_data['domain']
        
        # Infer from description or skills
        description = task_data.get('description', '').lower()
        title = task_data.get('title', '').lower()
        
        # Simple keyword-based domain detection
        if any(keyword in description or keyword in title 
               for keyword in ['frontend', 'ui', 'ux', 'react', 'vue', 'angular']):
            return 'frontend'
        elif any(keyword in description or keyword in title 
                for keyword in ['backend', 'api', 'database', 'server']):
            return 'backend'
        elif any(keyword in description or keyword in title 
                for keyword in ['devops', 'deployment', 'infrastructure', 'docker']):
            return 'devops'
        elif any(keyword in description or keyword in title 
                for keyword in ['mobile', 'ios', 'android', 'app']):
            return 'mobile'
        elif any(keyword in description or keyword in title 
                for keyword in ['data', 'analytics', 'machine learning', 'ai']):
            return 'data'
        elif any(keyword in description or keyword in title 
                for keyword in ['security', 'auth', 'encryption']):
            return 'security'
        elif any(keyword in description or keyword in title 
                for keyword in ['test', 'qa', 'testing']):
            return 'qa'
        elif any(keyword in description or keyword in title 
                for keyword in ['design', 'figma', 'photoshop']):
            return 'design'
        else:
            return 'general'
    
    def _extract_required_skills(self, task_data):
        """Extract required skills from task data"""
        if task_data.get('required_skills'):
            return task_data['required_skills']
        
        # Could implement skill extraction from description using NLP
        # For now, return None to let the matcher use domain-based matching
        return None
    
    def _fallback_autogen_assignment(self, task, task_data):
        """Fallback to AutoGen-based assignment if intelligent matching fails"""
        try:
            # Get available employees
            employees = Employee.query.filter_by(availability=True).all()
            
            if not employees:
                return None
            
            # Prepare employee data for AutoGen
            employee_data = []
            for emp in employees:
                emp_info = {
                    'id': emp.id,
                    'name': emp.name,
                    'email': emp.email,
                    'department': emp.department,
                    'skills': emp.skills,
                    'current_tasks': len(emp.task_assignments)
                }
                employee_data.append(emp_info)
            
            # Create analysis prompt
            analysis_prompt = f"""
            Analyze the following task and available employees to determine the best assignment:
            
            Task: {task.title}
            Description: {task.description}
            Priority: {task.priority}
            
            Available Employees: {json.dumps(employee_data, indent=2)}
            
            Consider:
            1. Skills match between task requirements and employee skills
            2. Current workload of each employee
            3. Department alignment
            4. Task priority and urgency
            
            Provide a recommendation for the best employee assignment with reasoning.
            Return the employee_id in your response.
            """
            
            # Run agent conversation
            chat_result = self.user_proxy.initiate_chat(
                self.manager_agent,
                message=analysis_prompt
            )
            
            # Extract recommendation from chat
            recommendation = self._extract_recommendation(chat_result)
            
            if recommendation and recommendation.get('employee_id'):
                # Create assignment
                assignment = TaskAssignment(
                    task_id=task.id,
                    employee_id=recommendation['employee_id'],
                    assigned_by='AutoGen Fallback',
                    notes=recommendation.get('reasoning', '')
                )
                db.session.add(assignment)
                
                # Update task status
                task.status = 'assigned'
                db.session.commit()
                
                # Send notification
                employee = Employee.query.get(recommendation['employee_id'])
                if employee:
                    self.email_service.send_task_assignment_notification(
                        employee.email,
                        task.title,
                        task.description
                    )
                
                return assignment
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"AutoGen fallback assignment failed: {str(e)}")
            return None
    
    def _extract_recommendation(self, chat_result):
        """Extract assignment recommendation from agent conversation"""
        try:
            # Look for the last message from the manager agent
            messages = chat_result.chat_history
            for message in reversed(messages):
                if message.get('name') == 'TaskManager':
                    content = message.get('content', '')
                    
                    # Try to extract employee ID from the message
                    if 'employee_id' in content.lower():
                        import re
                        emp_id_match = re.search(r'employee_id[:\s]*(\d+)', content)
                        if emp_id_match:
                            return {
                                'employee_id': int(emp_id_match.group(1)),
                                'reasoning': content
                            }
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Failed to extract recommendation: {str(e)}")
            return None
    
    def get_employee_recommendations(self, task_data, limit=5):
        """Get employee recommendations for a task without assigning"""
        try:
            task_type = self._determine_task_type(task_data)
            required_domain = self._determine_required_domain(task_data)
            required_skills = self._extract_required_skills(task_data)
            priority = task_data.get('priority', 'medium')
            
            recommendations = self.employee_matcher.get_employee_recommendations(
                task_type=task_type,
                priority=priority,
                required_domain=required_domain,
                required_skills=required_skills,
                limit=limit
            )
            
            return recommendations
            
        except Exception as e:
            current_app.logger.error(f"Failed to get recommendations: {str(e)}")
            return []
    
    def optimize_workload(self):
        """Optimize workload distribution across employees"""
        try:
            # Get current assignments
            assignments = TaskAssignment.query.filter_by(status='assigned').all()
            
            # Analyze workload distribution
            workload_data = {}
            for assignment in assignments:
                emp_id = assignment.employee_id
                if emp_id not in workload_data:
                    workload_data[emp_id] = 0
                workload_data[emp_id] += 1
            
            # Find overloaded employees
            avg_workload = sum(workload_data.values()) / len(workload_data) if workload_data else 0
            overloaded = [emp_id for emp_id, count in workload_data.items() 
                         if count > avg_workload * 1.5]
            
            if overloaded:
                current_app.logger.info(f"Found overloaded employees: {overloaded}")
                # Here you could implement workload rebalancing logic
                
            return workload_data
            
        except Exception as e:
            current_app.logger.error(f"Workload optimization failed: {str(e)}")
            return {} 