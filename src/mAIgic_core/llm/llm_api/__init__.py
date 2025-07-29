"""mAIgic_core LLM API.

This package provides abstract interfaces and types for AI assistant LLM operations.
Designed specifically for assistant use cases rather than generic chat.

Example usage:
    from mAIgic_core.llm.llm_api import (
        LLMClient,
        UserContext,
        SchedulingRequest,
        Intent
    )
    
    # Use with implementation
    from mAIgic_core.llm.llm_gemini_impl import GeminiLLMClient
    
    client = GeminiLLMClient(config)
    intent = await client.parse_intent("Schedule thesis work", context)
"""

from .exceptions import (
    # Base exceptions
    LLMError,
    LLMConnectionError,
    LLMTimeoutError,
    LLMRateLimitError,
    LLMAuthenticationError,
    LLMConfigurationError,
    
    # Provider exceptions
    LLMProviderError,
    LLMModelNotFoundError,
    
    # Response exceptions
    LLMResponseError,
    LLMIntentParsingError,
    LLMSchedulingError,
    LLMGoalAssessmentError,
    
    # Conversation exceptions
    ConversationStorageError,
    ConversationSaveError,
    ConversationRetrievalError,
    ConversationDeleteError,
    ConversationFileError,
    
    # Factory exceptions
    LLMFactoryError,
    
    # Utility functions
    get_error_details,
    is_retryable_error,
)

from .interfaces import (
    # Core interfaces
    LLMClient,
    LLMProvider,
    ConversationRepository,
    LLMClientFactory,
)

from .types import (
    # Enums
    IntentType,
    TaskPriority,
    GoalStatus,
    ActivityType,
    
    # Core types
    TimeSlot,
    UserTask,
    UserGoal,
    CalendarContext,
    EmailContext,
    UserProfile,
    UserContext,
    
    # Intent types
    Intent,
    ScheduleTaskIntent,
    QueryScheduleIntent,
    UpdateGoalIntent,
    LogActivityIntent,
    
    # Request/Response types
    SchedulingRequest,
    ConflictInfo,
    ScheduledTask,
    SchedulingDecision,
    GoalProgressAssessment,
    
    # Logging types
    ActivityLog,
    AssistantInteraction,
    
    # Configuration types
    LLMConfig,
    ConversationConfig,
    
    # Union types
    IntentUnion,
    

)

__version__ = "0.1.0"

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