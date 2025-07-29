"""Assistant types for workflow orchestration and session management.

This module defines data structures specific to assistant operations,
separate from the generic LLM API types.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, StrEnum
from typing import Any, Dict, List, Optional, Union

# Import core types from LLM API
from ..llm.llm_api.types import (
    Intent,
    UserContext,
    SchedulingDecision,
    ConflictInfo,
    TimeSlot,
)


class WorkflowStatus(StrEnum):
    """Status of workflow execution."""
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ServiceType(StrEnum):
    """Types of services the assistant can interact with."""
    
    CALENDAR = "calendar"
    EMAIL = "email"
    SPEECH = "speech"
    LLM = "llm"
    STORAGE = "storage"


class ResponseType(StrEnum):
    """Types of assistant responses."""
    
    TEXT = "text"
    VOICE = "voice"
    ACTION_CONFIRMATION = "action_confirmation"
    ERROR = "error"
    QUESTION = "question"


@dataclass
class WorkflowStep:
    """Individual step in a workflow execution."""
    
    id: str
    service_type: ServiceType
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: Optional[Any] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class WorkflowResult:
    """Result of a complete workflow execution."""
    
    workflow_id: str
    intent: Intent
    steps: List[WorkflowStep] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    final_result: Optional[Any] = None
    error_message: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    total_duration: float = 0.0  # seconds
    
    @property
    def is_complete(self) -> bool:
        """Check if workflow is complete (success or failure)."""
        return self.status in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED)
    
    @property
    def success(self) -> bool:
        """Check if workflow completed successfully."""
        return self.status == WorkflowStatus.COMPLETED


@dataclass
class AssistantResponse:
    """Response from the assistant to user interaction."""
    
    response_id: str
    response_type: ResponseType
    content: str
    audio_path: Optional[str] = None
    actions_taken: List[str] = field(default_factory=list)
    follow_up_suggestions: List[str] = field(default_factory=list)
    requires_confirmation: bool = False
    confidence: float = 1.0
    workflow_result: Optional[WorkflowResult] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary for serialization."""
        return {
            "response_id": self.response_id,
            "response_type": self.response_type,
            "content": self.content,
            "audio_path": self.audio_path,
            "actions_taken": self.actions_taken,
            "follow_up_suggestions": self.follow_up_suggestions,
            "requires_confirmation": self.requires_confirmation,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class SessionState:
    """Current state of an assistant session."""
    
    session_id: str
    user_id: str = "default"
    started_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    context: Optional[UserContext] = None
    pending_confirmations: List[str] = field(default_factory=list)
    conversation_history: List[str] = field(default_factory=list)
    active_workflows: List[str] = field(default_factory=list)
    session_metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now()
    
    @property
    def duration(self) -> float:
        """Get session duration in seconds."""
        return (self.last_activity - self.started_at).total_seconds()


@dataclass
class AssistantConfig:
    """Configuration for assistant behavior and capabilities."""
    
    # Voice settings
    enable_voice_input: bool = True
    enable_voice_output: bool = True
    voice_language: str = "en-US"
    speech_timeout: float = 30.0
    
    # LLM settings
    default_temperature: float = 0.7
    max_tokens: int = 500
    context_window_size: int = 10  # Number of recent interactions to include
    
    # Workflow settings
    max_concurrent_workflows: int = 3
    workflow_timeout: float = 300.0  # 5 minutes
    auto_confirm_low_risk_actions: bool = False
    
    # Service settings
    calendar_lookahead_days: int = 30
    email_batch_size: int = 50
    
    # Storage settings
    max_history_days: int = 30
    backup_conversations: bool = True
    
    # Behavior settings
    proactive_suggestions: bool = True
    learning_mode: bool = True
    privacy_mode: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "enable_voice_input": self.enable_voice_input,
            "enable_voice_output": self.enable_voice_output,
            "voice_language": self.voice_language,
            "speech_timeout": self.speech_timeout,
            "default_temperature": self.default_temperature,
            "max_tokens": self.max_tokens,
            "context_window_size": self.context_window_size,
            "max_concurrent_workflows": self.max_concurrent_workflows,
            "workflow_timeout": self.workflow_timeout,
            "auto_confirm_low_risk_actions": self.auto_confirm_low_risk_actions,
            "calendar_lookahead_days": self.calendar_lookahead_days,
            "email_batch_size": self.email_batch_size,
            "max_history_days": self.max_history_days,
            "backup_conversations": self.backup_conversations,
            "proactive_suggestions": self.proactive_suggestions,
            "learning_mode": self.learning_mode,
            "privacy_mode": self.privacy_mode,
        }


@dataclass
class ContextSnapshot:
    """Snapshot of user context at a specific point in time."""
    
    timestamp: datetime
    context: UserContext
    context_hash: str  # For detecting changes
    source: str = "assistant"  # Where this snapshot came from
    
    def __post_init__(self):
        """Generate context hash after initialization."""
        if not self.context_hash:
            self.context_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        """Generate a hash of the context for change detection."""
        import hashlib
        import json
        
        # Create a simplified representation for hashing
        context_dict = {
            "user_id": self.context.user_id,
            "active_goals_count": len(self.context.active_goals),
            "pending_tasks_count": len(self.context.pending_tasks),
            "calendar_events_count": len(self.context.calendar.upcoming_events),
            "unread_emails": self.context.email.unread_count,
        }
        
        context_str = json.dumps(context_dict, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()


# Union types for convenience
WorkflowResultUnion = Union[WorkflowResult, Dict[str, Any]]
AssistantResponseUnion = Union[AssistantResponse, str] 