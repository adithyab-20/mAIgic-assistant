"""LLM Package

This package contains the LLM API interfaces and types for provider-agnostic
LLM operations in the mAIgic assistant.
"""

from .llm_api import (
    # Interfaces
    LLMClient,
    LLMProvider,
    ConversationRepository,
    LLMClientFactory,
    
    # Core types
    UserContext,
    UserTask,
    UserGoal,
    TimeSlot,
    CalendarContext,
    EmailContext,
    UserProfile,
    
    # Intent types
    Intent,
    IntentType,
    ScheduleTaskIntent,
    QueryScheduleIntent,
    UpdateGoalIntent,
    LogActivityIntent,
    IntentUnion,
    
    # Scheduling types
    SchedulingRequest,
    SchedulingDecision,
    ScheduledTask,
    ConflictInfo,
    TaskPriority,
    
    # Goal tracking
    GoalProgressAssessment,
    GoalStatus,
    
    # Activity logging
    ActivityLog,
    AssistantInteraction,
    ActivityType,
    
    # Configuration
    LLMConfig,
    ConversationConfig,
    
    # Exceptions
    LLMError,
    LLMConnectionError,
    LLMTimeoutError,
    LLMRateLimitError,
    LLMAuthenticationError,
    LLMConfigurationError,
    LLMProviderError,
    LLMModelNotFoundError,
    LLMResponseError,
    LLMIntentParsingError,
    LLMSchedulingError,
    LLMGoalAssessmentError,
    ConversationStorageError,
    ConversationSaveError,
    ConversationRetrievalError,
    ConversationDeleteError,
    ConversationFileError,
    LLMFactoryError,
    
    # Utility functions
    get_error_details,
    is_retryable_error,
)

__all__ = [
    # Interfaces
    "LLMClient",
    "LLMProvider",
    "ConversationRepository",
    "LLMClientFactory",
    
    # Core types
    "UserContext",
    "UserTask",
    "UserGoal",
    "TimeSlot",
    "CalendarContext",
    "EmailContext",
    "UserProfile",
    
    # Intent types
    "Intent",
    "IntentType",
    "ScheduleTaskIntent",
    "QueryScheduleIntent",
    "UpdateGoalIntent",
    "LogActivityIntent",
    "IntentUnion",
    
    # Scheduling types
    "SchedulingRequest",
    "SchedulingDecision",
    "ScheduledTask",
    "ConflictInfo",
    "TaskPriority",
    
    # Goal tracking
    "GoalProgressAssessment",
    "GoalStatus",
    
    # Activity logging
    "ActivityLog",
    "AssistantInteraction",
    "ActivityType",
    
    # Configuration
    "LLMConfig",
    "ConversationConfig",
    
    # Exceptions
    "LLMError",
    "LLMConnectionError",
    "LLMTimeoutError",
    "LLMRateLimitError",
    "LLMAuthenticationError",
    "LLMConfigurationError",
    "LLMProviderError",
    "LLMModelNotFoundError",
    "LLMResponseError",
    "LLMIntentParsingError",
    "LLMSchedulingError",
    "LLMGoalAssessmentError",
    "ConversationStorageError",
    "ConversationSaveError",
    "ConversationRetrievalError",
    "ConversationDeleteError",
    "ConversationFileError",
    "LLMFactoryError",
    
    # Utility functions
    "get_error_details",
    "is_retryable_error",
] 