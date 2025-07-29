"""Validation utilities for mAIgic_core.

This module provides validation functions for user context,
assistant configuration, and user input sanitization.
"""

import re
from typing import Any, Dict, List, Optional

from ..llm.llm_api.types import UserContext, UserGoal, UserTask
from ..assistant.types import AssistantConfig


def validate_user_context(context: UserContext) -> tuple[bool, Optional[str]]:
    """Validate user context structure and data.
    
    Args:
        context: UserContext to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check required fields
        if not context.user_id:
            return False, "User ID is required"
        
        if not context.current_time:
            return False, "Current time is required"
        
        # Validate goals
        for goal in context.active_goals:
            if not goal.id or not goal.title:
                return False, "Goal must have ID and title"
            
            if not (0 <= goal.progress <= 1):
                return False, "Goal progress must be between 0 and 1"
        
        # Validate tasks
        for task in context.pending_tasks:
            if not task.id or not task.title:
                return False, "Task must have ID and title"
        
        # Validate user profile
        profile = context.user_profile
        if not (0 <= profile.working_hours_start <= 23):
            return False, "Working hours start must be between 0 and 23"
        
        if not (0 <= profile.working_hours_end <= 23):
            return False, "Working hours end must be between 0 and 23"
        
        if profile.working_hours_start >= profile.working_hours_end:
            return False, "Working hours start must be before end"
        
        return True, None
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def validate_assistant_config(config: AssistantConfig) -> tuple[bool, Optional[str]]:
    """Validate assistant configuration.
    
    Args:
        config: AssistantConfig to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Validate temperature
        if not (0.0 <= config.default_temperature <= 1.0):
            return False, "Temperature must be between 0.0 and 1.0"
        
        # Validate timeouts
        if config.speech_timeout <= 0:
            return False, "Speech timeout must be positive"
        
        if config.workflow_timeout <= 0:
            return False, "Workflow timeout must be positive"
        
        # Validate limits
        if config.max_tokens <= 0:
            return False, "Max tokens must be positive"
        
        if config.context_window_size <= 0:
            return False, "Context window size must be positive"
        
        if config.max_concurrent_workflows <= 0:
            return False, "Max concurrent workflows must be positive"
        
        # Validate days
        if config.calendar_lookahead_days <= 0:
            return False, "Calendar lookahead days must be positive"
        
        if config.max_history_days <= 0:
            return False, "Max history days must be positive"
        
        # Validate batch sizes
        if config.email_batch_size <= 0:
            return False, "Email batch size must be positive"
        
        return True, None
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def sanitize_user_input(user_input: str, max_length: int = 1000) -> str:
    """Sanitize user input for safety and consistency.
    
    Args:
        user_input: Raw user input string
        max_length: Maximum allowed length
        
    Returns:
        Sanitized input string
    """
    if not isinstance(user_input, str):
        return ""
    
    # Remove excessive whitespace
    sanitized = re.sub(r'\s+', ' ', user_input.strip())
    
    # Remove control characters except newlines and tabs
    sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip()
    
    return sanitized


def validate_email_address(email: str) -> bool:
    """Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_time_zone(timezone: str) -> bool:
    """Validate timezone string.
    
    Args:
        timezone: Timezone string to validate
        
    Returns:
        True if valid timezone
    """
    try:
        import zoneinfo
        zoneinfo.ZoneInfo(timezone)
        return True
    except (ImportError, Exception):
        # Fallback for basic validation
        common_timezones = [
            "UTC", "US/Eastern", "US/Central", "US/Mountain", "US/Pacific",
            "Europe/London", "Europe/Paris", "Europe/Berlin", "Asia/Tokyo",
            "Asia/Shanghai", "Australia/Sydney"
        ]
        return timezone in common_timezones


def validate_goal_data(goal_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """Validate goal data structure.
    
    Args:
        goal_data: Dictionary containing goal data
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ["id", "title"]
    
    for field in required_fields:
        if field not in goal_data:
            return False, f"Missing required field: {field}"
    
    # Validate ID
    if not isinstance(goal_data["id"], str) or not goal_data["id"].strip():
        return False, "Goal ID must be a non-empty string"
    
    # Validate title
    if not isinstance(goal_data["title"], str) or not goal_data["title"].strip():
        return False, "Goal title must be a non-empty string"
    
    # Validate progress if present
    if "progress" in goal_data:
        progress = goal_data["progress"]
        if not isinstance(progress, (int, float)) or not (0 <= progress <= 1):
            return False, "Goal progress must be a number between 0 and 1"
    
    # Validate priority if present
    if "priority" in goal_data:
        priority = goal_data["priority"]
        if not isinstance(priority, int) or not (1 <= priority <= 10):
            return False, "Goal priority must be an integer between 1 and 10"
    
    return True, None


def validate_task_data(task_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """Validate task data structure.
    
    Args:
        task_data: Dictionary containing task data
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ["id", "title"]
    
    for field in required_fields:
        if field not in task_data:
            return False, f"Missing required field: {field}"
    
    # Validate ID
    if not isinstance(task_data["id"], str) or not task_data["id"].strip():
        return False, "Task ID must be a non-empty string"
    
    # Validate title
    if not isinstance(task_data["title"], str) or not task_data["title"].strip():
        return False, "Task title must be a non-empty string"
    
    # Validate estimated_duration if present
    if "estimated_duration" in task_data:
        duration = task_data["estimated_duration"]
        if not isinstance(duration, (int, float)) or duration <= 0:
            return False, "Task estimated duration must be a positive number"
    
    return True, None


def is_safe_filename(filename: str) -> bool:
    """Check if filename is safe for file system operations.
    
    Args:
        filename: Filename to validate
        
    Returns:
        True if filename is safe
    """
    if not filename or not isinstance(filename, str):
        return False
    
    # Check for dangerous characters
    dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\n', '\r', '\t']
    if any(char in filename for char in dangerous_chars):
        return False
    
    # Check for reserved names (Windows)
    reserved_names = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]
    if filename.upper() in reserved_names:
        return False
    
    # Check length (reasonable limit)
    if len(filename) > 255:
        return False
    
    # Check for leading/trailing dots or spaces
    if filename.startswith('.') or filename.endswith('.') or filename.startswith(' ') or filename.endswith(' '):
        return False
    
    return True 