import subprocess
import logging
from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task
from .models import RegulatedTask, TaskExecution, NotificationLog

logger = logging.getLogger(__name__)


def execute_command(command):
    """Execute system command and return result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'exit_code': result.returncode,
            'success': result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            'stdout': '',
            'stderr': 'Command timeout after 300 seconds',
            'exit_code': 124,
            'success': False
        }
    except Exception as e:
        return {
            'stdout': '',
            'stderr': str(e),
            'exit_code': 1,
            'success': False
        }


def send_notification(task_execution, status):
    """Send email notification"""
    task = task_execution.task
    emails = task.get_notify_emails()
    
    if not emails:
        return
    
    # Prepare email content
    status_text = {
        'completed': '✅ Успешно завершена',
        'failed': '❌ Завершена с ошибкой',
    }
    
    subject = f"[{status_text.get(status, status)}] Задача: {task.name}"
    
    message = f"""
Регламентная работа: {task.name}
Тип: {task.get_task_type_display()}
Статус: {status_text.get(status, status)}

Время начала: {task_execution.started_at}
Время завершения: {task_execution.completed_at}
Длительность: {task_execution.duration_seconds} сек

Код выхода: {task_execution.exit_code}

--- ВЫВОД STDOUT ---
{task_execution.stdout[:1000]}

--- ВЫВОД STDERR ---
{task_execution.stderr[:1000]}

--- ПРИМЕЧАНИЯ ---
{task_execution.notes}

Система управления регламентными работами
    """
    
    for email in emails:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            NotificationLog.objects.create(
                task_execution=task_execution,
                recipient_email=email,
                subject=subject,
                status='sent'
            )
            logger.info(f"Notification sent to {email} for task {task.name}")
        except Exception as e:
            logger.error(f"Failed to send notification to {email}: {str(e)}")
            NotificationLog.objects.create(
                task_execution=task_execution,
                recipient_email=email,
                subject=subject,
                status='failed',
                error_message=str(e)
            )


@shared_task
def execute_task(task_id):
    """Execute regulated task"""
    try:
        task = RegulatedTask.objects.get(id=task_id)
        
        if not task.is_active:
            logger.info(f"Task {task.name} is inactive")
            return
        
        # Create execution record
        execution = TaskExecution.objects.create(
            task=task,
            status='pending',
            executed_by='celery'
        )
        
        execution.mark_as_running()
        logger.info(f"Starting execution of task: {task.name}")
        
        # Execute command
        result = execute_command(task.command)
        
        # Update execution record
        if result['success']:
            execution.mark_as_completed(
                exit_code=result['exit_code'],
                notes='Task completed successfully'
            )
            send_notification(execution, 'completed')
            logger.info(f"Task {task.name} completed successfully")
        else:
            execution.mark_as_failed(
                exit_code=result['exit_code'],
                notes='Task failed'
            )
            send_notification(execution, 'failed')
            logger.error(f"Task {task.name} failed with exit code {result['exit_code']}")
        
        # Store output
        execution.stdout = result['stdout']
        execution.stderr = result['stderr']
        execution.save()
        
        return f"Task {task.name} executed with exit code {result['exit_code']}"
        
    except RegulatedTask.DoesNotExist:
        logger.error(f"Task with id {task_id} not found")
        return f"Task with id {task_id} not found"
    except Exception as e:
        logger.error(f"Error executing task: {str(e)}")
        return f"Error: {str(e)}"


@shared_task
def backup_task():
    """Backup task"""
    logger.info("Starting backup task")
    # Find and execute backup tasks
    backup_tasks = RegulatedTask.objects.filter(task_type='backup', is_active=True)
    for task in backup_tasks:
        execute_task.delay(task.id)


@shared_task
def check_disk_task():
    """Check disk task"""
    logger.info("Starting disk check task")
    disk_tasks = RegulatedTask.objects.filter(task_type='disk_check', is_active=True)
    for task in disk_tasks:
        execute_task.delay(task.id)


@shared_task
def check_services_task():
    """Check services task"""
    logger.info("Starting services check task")
    service_tasks = RegulatedTask.objects.filter(task_type='service_check', is_active=True)
    for task in service_tasks:
        execute_task.delay(task.id)


@shared_task
def clean_logs_task():
    """Clean logs task"""
    logger.info("Starting logs cleanup task")
    cleanup_tasks = RegulatedTask.objects.filter(task_type='log_cleanup', is_active=True)
    for task in cleanup_tasks:
        execute_task.delay(task.id)


@shared_task
def system_update_task():
    """System update task"""
    logger.info("Starting system update task")
    update_tasks = RegulatedTask.objects.filter(task_type='system_update', is_active=True)
    for task in update_tasks:
        execute_task.delay(task.id)
