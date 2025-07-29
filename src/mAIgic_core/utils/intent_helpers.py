"""Intent helper functions for mAIgic_core.

This module provides utility functions for creating, validating,
and manipulating intent objects.
"""

from typing import Any, Dict, Union

from ..llm.llm_api.types import (
    Intent,
    IntentType,
    ScheduleTaskIntent,
    QueryScheduleIntent,
    UpdateGoalIntent,
    LogActivityIntent,
    IntentUnion,
)


def create_intent_from_type(intent_type: IntentType, **kwargs: Any) -> IntentUnion:
    """Factory function to create intent objects from type.
    
    Args:
        intent_type: The type of intent to create
        **kwargs: Additional parameters for the intent
        
    Returns:
        Appropriate intent object instance
        
    Raises:
        ValueError: If intent_type is not supported
    """
    intent_map = {
        IntentType.SCHEDULE_TASK: ScheduleTaskIntent,
        IntentType.QUERY_SCHEDULE: QueryScheduleIntent,
        IntentType.UPDATE_GOAL: UpdateGoalIntent,
        IntentType.LOG_ACTIVITY: LogActivityIntent,
    }
    
    intent_class = intent_map.get(intent_type, Intent)
    
    # Ensure type is set correctly
    kwargs["type"] = intent_type
    
    try:
        return intent_class(**kwargs)
    except TypeError as e:
        raise ValueError(f"Invalid parameters for intent type {intent_type}: {e}")


def validate_intent_data(intent_data: Dict[str, Any]) -> bool:
    """Validate intent data structure.
    
    Args:
        intent_data: Dictionary containing intent data
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["type", "confidence", "original_text"]
    
    # Check required fields
    for field in required_fields:
        if field not in intent_data:
            return False
    
    # Validate type
    try:
        IntentType(intent_data["type"])
    except ValueError:
        return False
    
    # Validate confidence
    confidence = intent_data.get("confidence", 0)
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        return False
    
    # Validate original_text
    if not isinstance(intent_data.get("original_text"), str):
        return False
    
    return True


def intent_to_dict(intent: Intent) -> Dict[str, Any]:
    """Convert intent object to dictionary.
    
    Args:
        intent: Intent object to convert
        
    Returns:
        Dictionary representation of the intent
    """
    result = {
        "type": intent.type.value if hasattr(intent.type, 'value') else intent.type,
        "confidence": intent.confidence,
        "original_text": intent.original_text,
        "parsed_at": intent.parsed_at.isoformat(),
    }
    
    # Add type-specific fields
    if isinstance(intent, ScheduleTaskIntent):
        result.update({
            "task_title": intent.task_title,
            "task_description": intent.task_description,
            "estimated_duration": intent.estimated_duration.total_seconds() if intent.estimated_duration else None,
            "deadline": intent.deadline.isoformat() if intent.deadline else None,
            "priority": intent.priority.value if hasattr(intent.priority, 'value') else intent.priority,
            "preferred_time": {
                "start": intent.preferred_time.start.isoformat(),
                "end": intent.preferred_time.end.isoformat(),
                "timezone": intent.preferred_time.timezone,
            } if intent.preferred_time else None,
            "goal_id": intent.goal_id,
        })
    elif isinstance(intent, QueryScheduleIntent):
        result.update({
            "time_range": {
                "start": intent.time_range.start.isoformat(),
                "end": intent.time_range.end.isoformat(),
                "timezone": intent.time_range.timezone,
            } if intent.time_range else None,
            "include_tasks": intent.include_tasks,
            "include_events": intent.include_events,
            "specific_goal": intent.specific_goal,
        })
    elif isinstance(intent, UpdateGoalIntent):
        result.update({
            "goal_title": intent.goal_title,
            "goal_description": intent.goal_description,
            "priority": intent.priority,
            "deadline": intent.deadline.isoformat() if intent.deadline else None,
            "is_new_goal": intent.is_new_goal,
            "goal_id": intent.goal_id,
        })
    elif isinstance(intent, LogActivityIntent):
        result.update({
            "activity_type": intent.activity_type.value if hasattr(intent.activity_type, 'value') else intent.activity_type,
            "description": intent.description,
            "task_id": intent.task_id,
            "goal_id": intent.goal_id,
            "completion_time": intent.completion_time.isoformat() if intent.completion_time else None,
        })
    
    return result


def intent_from_dict(intent_data: Dict[str, Any]) -> IntentUnion:
    """Create intent object from dictionary.
    
    Args:
        intent_data: Dictionary containing intent data
        
    Returns:
        Intent object instance
        
    Raises:
        ValueError: If intent_data is invalid
    """
    if not validate_intent_data(intent_data):
        raise ValueError("Invalid intent data structure")
    
    intent_type = IntentType(intent_data["type"])
    
    # Remove type from kwargs to avoid duplication
    kwargs = {k: v for k, v in intent_data.items() if k != "type"}
    
    # Convert string timestamps back to datetime objects if needed
    from datetime import datetime, timedelta
    
    if "parsed_at" in kwargs and isinstance(kwargs["parsed_at"], str):
        kwargs["parsed_at"] = datetime.fromisoformat(kwargs["parsed_at"])
    
    if "deadline" in kwargs and isinstance(kwargs["deadline"], str):
        kwargs["deadline"] = datetime.fromisoformat(kwargs["deadline"])
    
    if "completion_time" in kwargs and isinstance(kwargs["completion_time"], str):
        kwargs["completion_time"] = datetime.fromisoformat(kwargs["completion_time"])
    
    # Handle duration conversion
    if "estimated_duration" in kwargs and isinstance(kwargs["estimated_duration"], (int, float)):
        kwargs["estimated_duration"] = timedelta(seconds=kwargs["estimated_duration"])
    
    # Handle time_range conversion
    if "time_range" in kwargs and isinstance(kwargs["time_range"], dict):
        from ..llm.llm_api.types import TimeSlot
        time_range_data = kwargs["time_range"]
        kwargs["time_range"] = TimeSlot(
            start=datetime.fromisoformat(time_range_data["start"]),
            end=datetime.fromisoformat(time_range_data["end"]),
            timezone=time_range_data.get("timezone", "UTC")
        )
    
    # Handle preferred_time conversion
    if "preferred_time" in kwargs and isinstance(kwargs["preferred_time"], dict):
        from ..llm.llm_api.types import TimeSlot
        preferred_time_data = kwargs["preferred_time"]
        kwargs["preferred_time"] = TimeSlot(
            start=datetime.fromisoformat(preferred_time_data["start"]),
            end=datetime.fromisoformat(preferred_time_data["end"]),
            timezone=preferred_time_data.get("timezone", "UTC")
        )
    
    # Handle enum conversions
    if "priority" in kwargs and isinstance(kwargs["priority"], str):
        from ..llm.llm_api.types import TaskPriority
        kwargs["priority"] = TaskPriority(kwargs["priority"])
    
    if "activity_type" in kwargs and isinstance(kwargs["activity_type"], str):
        from ..llm.llm_api.types import ActivityType
        kwargs["activity_type"] = ActivityType(kwargs["activity_type"])
    
    return create_intent_from_type(intent_type, **kwargs) 