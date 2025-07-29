"""Data types for mAIgic_core LLM API.

This module defines all data structures used in the LLM API,
including context types, intent types, and interaction records.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, StrEnum
from typing import Any, Dict, List, Optional, Union


# Enums and String Enums
class IntentType(StrEnum):
    """Types of user intents the assistant can handle."""
    
    SCHEDULE_TASK = "schedule_task"
    QUERY_SCHEDULE = "query_schedule"
    UPDATE_GOAL = "update_goal"
    LOG_ACTIVITY = "log_activity"
    RESCHEDULE_TASK = "reschedule_task"
    QUERY_AVAILABILITY = "query_availability"
    EMAIL_ACTION = "email_action"
    GENERAL_CONVERSATION = "general_conversation"


class TaskPriority(Enum):
    """Task priority levels matching Motion's approach."""
    
    ASAP = 4      # Urgent, can override normal hours
    HIGH = 3      # Important, respects working hours
    MEDIUM = 2    # Normal priority
    LOW = 1       # Can be postponed


class GoalStatus(StrEnum):
    """Status of user goals."""
    
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class ActivityType(StrEnum):
    """Types of activities the user can log."""
    
    TASK_COMPLETION = "task_completion"
    TASK_START = "task_start"
    GOAL_UPDATE = "goal_update"
    SCHEDULE_CHANGE = "schedule_change"
    PRODUCTIVITY_NOTE = "productivity_note"


# Core Data Models
@dataclass
class TimeSlot:
    """Represents a time period with timezone awareness."""
    
    start: datetime
    end: datetime
    timezone: str = "UTC"
    
    @property
    def duration(self) -> timedelta:
        """Calculate duration of the time slot."""
        return self.end - self.start
    
    def overlaps_with(self, other: "TimeSlot") -> bool:
        """Check if this time slot overlaps with another."""
        return self.start < other.end and self.end > other.start


@dataclass
class UserTask:
    """Represents a task that needs to be scheduled."""
    
    id: str
    title: str
    description: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_duration: timedelta = timedelta(hours=1)
    deadline: Optional[datetime] = None
    goal_id: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None


@dataclass
class UserGoal:
    """Represents a user's long-term goal."""
    
    id: str
    title: str
    description: str = ""
    priority: int = 5  # 1-10 scale
    deadline: Optional[datetime] = None
    status: GoalStatus = GoalStatus.ACTIVE
    progress: float = 0.0  # 0.0-1.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    milestones: List[str] = field(default_factory=list)


@dataclass
class CalendarContext:
    """Context from calendar integrations."""
    
    upcoming_events: List[Dict[str, Any]] = field(default_factory=list)
    free_time_slots: List[TimeSlot] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class EmailContext:
    """Context from email integrations."""
    
    unread_count: int = 0
    priority_emails: List[Dict[str, Any]] = field(default_factory=list)
    recent_contacts: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class UserProfile:
    """User preferences and patterns."""
    
    timezone: str = "UTC"
    working_hours_start: int = 9  # 24-hour format
    working_hours_end: int = 17
    preferred_task_duration: timedelta = timedelta(hours=2)
    energy_pattern: Dict[int, float] = field(default_factory=dict)  # hour -> energy score
    productivity_preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserContext:
    """Complete user context for LLM decision making."""
    
    user_id: str = "default"
    current_time: datetime = field(default_factory=datetime.now)
    calendar: CalendarContext = field(default_factory=CalendarContext)
    email: EmailContext = field(default_factory=EmailContext)
    active_goals: List[UserGoal] = field(default_factory=list)
    pending_tasks: List[UserTask] = field(default_factory=list)
    user_profile: UserProfile = field(default_factory=UserProfile)
    recent_activities: List["ActivityLog"] = field(default_factory=list)
    context_metadata: Dict[str, Any] = field(default_factory=dict)


# Intent Types
@dataclass
class Intent:
    """Base intent class for all user intents."""
    
    type: IntentType
    confidence: float = 1.0
    original_text: str = ""
    parsed_at: datetime = field(default_factory=datetime.now)


@dataclass
class ScheduleTaskIntent(Intent):
    """Intent to schedule a new task."""
    
    type: IntentType = IntentType.SCHEDULE_TASK
    task_title: str = ""
    task_description: str = ""
    estimated_duration: Optional[timedelta] = None
    deadline: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    preferred_time: Optional[TimeSlot] = None
    goal_id: Optional[str] = None


@dataclass
class QueryScheduleIntent(Intent):
    """Intent to query current schedule."""
    
    type: IntentType = IntentType.QUERY_SCHEDULE
    time_range: Optional[TimeSlot] = None
    include_tasks: bool = True
    include_events: bool = True
    specific_goal: Optional[str] = None


@dataclass
class UpdateGoalIntent(Intent):
    """Intent to update or create goals."""
    
    type: IntentType = IntentType.UPDATE_GOAL
    goal_title: str = ""
    goal_description: str = ""
    priority: int = 5
    deadline: Optional[datetime] = None
    is_new_goal: bool = True
    goal_id: Optional[str] = None


@dataclass
class LogActivityIntent(Intent):
    """Intent to log completed activities."""
    
    type: IntentType = IntentType.LOG_ACTIVITY
    activity_type: ActivityType = ActivityType.TASK_COMPLETION
    description: str = ""
    task_id: Optional[str] = None
    goal_id: Optional[str] = None
    completion_time: Optional[datetime] = None


# Request and Response Types
@dataclass
class SchedulingRequest:
    """Request for scheduling decision from LLM."""
    
    intent: Intent
    context: UserContext
    request_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConflictInfo:
    """Information about scheduling conflicts."""
    
    conflict_type: str = ""
    description: str = ""
    conflicting_items: List[str] = field(default_factory=list)
    suggested_resolution: str = ""
    severity: int = 1  # 1-5 scale


@dataclass
class ScheduledTask:
    """A task with assigned time slot."""
    
    task: UserTask
    time_slot: TimeSlot
    confidence: float = 1.0
    reasoning: str = ""
    calendar_event_id: Optional[str] = None


@dataclass
class SchedulingDecision:
    """LLM decision for scheduling operations."""
    
    scheduled_tasks: List[ScheduledTask] = field(default_factory=list)
    reasoning: str = ""
    confidence: float = 1.0
    conflicts: List[ConflictInfo] = field(default_factory=list)
    alternative_options: List[Dict[str, Any]] = field(default_factory=list)
    follow_up_actions: List[str] = field(default_factory=list)
    estimated_completion_time: Optional[datetime] = None


@dataclass
class GoalProgressAssessment:
    """Assessment of progress toward a goal."""
    
    goal_id: str
    current_progress: float = 0.0  # 0.0-1.0
    progress_delta: float = 0.0  # Change since last assessment
    completion_confidence: float = 0.5  # Confidence in meeting deadline
    blockers: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)
    estimated_completion: Optional[datetime] = None
    assessment_reasoning: str = ""


# Activity and Interaction Logging
@dataclass
class ActivityLog:
    """Log entry for user activities."""
    
    id: str
    user_id: str = "default"
    activity_type: ActivityType = ActivityType.TASK_COMPLETION
    description: str = ""
    task_id: Optional[str] = None
    goal_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AssistantInteraction:
    """Complete record of user interaction with assistant."""
    
    id: str
    user_id: str = "default"
    input_text: str = ""
    input_audio_path: Optional[str] = None
    parsed_intent: Optional[Intent] = None
    context_snapshot: Optional[UserContext] = None
    llm_response: str = ""
    actions_taken: List[str] = field(default_factory=list)
    success: bool = True
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    processing_time: float = 0.0  # seconds
    tokens_used: int = 0


# Configuration Types
@dataclass
class LLMConfig:
    """Base configuration for LLM providers."""
    
    provider: str = "gemini"
    model_name: str = ""
    api_key: str = ""
    base_url: Optional[str] = None
    timeout: float = 30.0
    max_retries: int = 3
    default_temperature: float = 0.7
    default_max_tokens: int = 500


@dataclass
class ConversationConfig:
    """Configuration for conversation storage."""
    
    storage_type: str = "file"  # "file", "database", "memory"
    data_directory: str = "mAIgic_data"
    max_history_days: int = 30
    max_interactions_per_user: int = 1000
    backup_enabled: bool = True


# Union Types for Convenience
IntentUnion = Union[
    ScheduleTaskIntent,
    QueryScheduleIntent,
    UpdateGoalIntent,
    LogActivityIntent,
    Intent
]


# Note: Helper functions have been moved to mAIgic_core.utils
# Import from mAIgic_core.utils.intent_helpers and mAIgic_core.utils.time_helpers