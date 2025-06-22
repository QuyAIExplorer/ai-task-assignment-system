import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from models.database import db, Notification


def send_assignment_email(employee_email, task_title, task_description, jira_url):
    """
    Send assignment email using Gmail SMTP.
    
    Args:
        employee_email (str): Recipient email address
        task_title (str): Title of the assigned task
        task_description (str): Description of the task
        jira_url (str): URL to the Jira ticket
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Email configuration
        sender_email = "nguyencongquy23012002@gmail.com"
        subject = f"New Task Assigned: {task_title}"
        
        # Create email body
        body = f"""
        Hello,

        You have been assigned a new task:

        Task Title: {task_title}
        
        Description:
        {task_description}
        
        Jira Ticket: {jira_url}
        
        Please review the task details and update the status in Jira.
        
        Best regards,
        AI Task Assignment System
        """
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = employee_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Gmail SMTP configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # Get Gmail app password from environment
        gmail_password = current_app.config.get('GMAIL_APP_PASSWORD')
        if not gmail_password:
            current_app.logger.error("GMAIL_APP_PASSWORD not configured")
            return False
        
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, gmail_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, employee_email, text)
        server.quit()
        
        current_app.logger.info(
            f"Assignment email sent to {employee_email} for task: {task_title}"
        )
        
        # Log successful notification
        notification = Notification(
            recipient_email=employee_email,
            subject=subject,
            message=body,
            status='sent'
        )
        db.session.add(notification)
        db.session.commit()
        
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send assignment email: {str(e)}")
        
        # Log failed notification
        try:
            notification = Notification(
                recipient_email=employee_email,
                subject=subject if 'subject' in locals() else "Task Assignment",
                message=body if 'body' in locals() else "",
                status='failed',
                error_message=str(e)
            )
            db.session.add(notification)
            db.session.commit()
        except:
            pass  # Don't let notification logging break the main function
        
        return False


class EmailService:
    """Email service for sending notifications"""
    
    def __init__(self):
        self.smtp_server = current_app.config['SMTP_SERVER']
        self.smtp_port = current_app.config['SMTP_PORT']
        self.username = current_app.config['SMTP_USERNAME']
        self.password = current_app.config['SMTP_PASSWORD']
    
    def send_email(self, recipient_email, subject, message):
        """Send an email notification"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Add body to email
            msg.attach(MIMEText(message, 'plain'))
            
            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.username, recipient_email, text)
            server.quit()
            
            # Log successful notification
            notification = Notification(
                recipient_email=recipient_email,
                subject=subject,
                message=message,
                status='sent'
            )
            db.session.add(notification)
            db.session.commit()
            
            return True
            
        except Exception as e:
            # Log failed notification
            notification = Notification(
                recipient_email=recipient_email,
                subject=subject,
                message=message,
                status='failed',
                error_message=str(e)
            )
            db.session.add(notification)
            db.session.commit()
            
            current_app.logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def send_task_assignment_notification(self, employee_email, task_title, 
                                        task_description, jira_url=None):
        """Send task assignment notification with optional Jira URL"""
        if jira_url:
            # Use the new Gmail function for Jira assignments
            return send_assignment_email(
                employee_email, task_title, task_description, jira_url
            )
        else:
            # Use the original method for non-Jira assignments
            subject = f"New Task Assignment: {task_title}"
            message = f"""
            You have been assigned a new task:
            
            Title: {task_title}
            Description: {task_description}
            
            Please log into the task management system to view details and update 
            the status.
            
            Best regards,
            AI Task Assignment System
            """
            
            return self.send_email(employee_email, subject, message)
    
    def send_task_completion_notification(self, manager_email, task_title, 
                                        employee_name):
        """Send task completion notification to manager"""
        subject = f"Task Completed: {task_title}"
        message = f"""
        A task has been completed:
        
        Task: {task_title}
        Completed by: {employee_name}
        
        Please review the completed task in the task management system.
        
        Best regards,
        AI Task Assignment System
        """
        
        return self.send_email(manager_email, subject, message)
    
    def send_jira_assignment_notification(self, employee_email, task_title, 
                                        task_description, jira_url):
        """Send Jira-specific assignment notification using Gmail"""
        return send_assignment_email(
            employee_email, task_title, task_description, jira_url
        ) 