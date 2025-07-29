"""Exception hierarchy for mAIgic_core Assistant operations.

This module defines all exceptions that can be raised by assistant
workflow and session management operations.
"""

from typing import Any, Dict, List, Optional


class AssistantError(Exception):
    """Base exception for all assistant-related errors."""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "ASSISTANT_ERROR", 
        details: Dict[str, Any] = None
    ):
        """Initialize assistant error.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class SchedulingError(AssistantError):
    """Raised when scheduling operations fail."""
    
    def __init__(
        self, 
        message: str = "Scheduling operation failed", 
        intent_type: str = None,
        conflicts: List[str] = None,
        **kwargs
    ):
        super().__init__(message, error_code="SCHEDULING_ERROR", **kwargs)
        if intent_type:
            self.details["intent_type"] = intent_type
        if conflicts:
            self.details["conflicts"] = conflicts


class WorkflowError(AssistantError):
    """Raised when workflow execution fails."""
    
    def __init__(
        self, 
        message: str = "Workflow execution failed", 
        workflow_id: str = None,
        failed_step: str = None,
        **kwargs
    ):
        super().__init__(message, error_code="WORKFLOW_ERROR", **kwargs)
        if workflow_id:
            self.details["workflow_id"] = workflow_id
        if failed_step:
            self.details["failed_step"] = failed_step


class WorkflowTimeoutError(WorkflowError):
    """Raised when workflow execution times out."""
    
    def __init__(
        self, 
        message: str = "Workflow execution timed out", 
        timeout_seconds: float = None,
        **kwargs
    ):
        super().__init__(message, error_code="WORKFLOW_TIMEOUT", **kwargs)
        if timeout_seconds:
            self.details["timeout_seconds"] = timeout_seconds


class ServiceIntegrationError(WorkflowError):
    """Raised when service integration fails during workflow."""
    
    def __init__(
        self, 
        message: str = "Service integration failed", 
        service_type: str = None,
        service_error: str = None,
        **kwargs
    ):
        super().__init__(message, error_code="SERVICE_INTEGRATION_ERROR", **kwargs)
        if service_type:
            self.details["service_type"] = service_type
        if service_error:
            self.details["service_error"] = service_error


class SessionError(AssistantError):
    """Raised when session management operations fail."""
    
    def __init__(
        self, 
        message: str = "Session operation failed", 
        session_id: str = None,
        user_id: str = None,
        **kwargs
    ):
        super().__init__(message, error_code="SESSION_ERROR", **kwargs)
        if session_id:
            self.details["session_id"] = session_id
        if user_id:
            self.details["user_id"] = user_id


class SessionExpiredError(SessionError):
    """Raised when trying to use an expired session."""
    
    def __init__(
        self, 
        message: str = "Session has expired", 
        expired_at: str = None,
        **kwargs
    ):
        super().__init__(message, error_code="SESSION_EXPIRED", **kwargs)
        if expired_at:
            self.details["expired_at"] = expired_at


class ContextError(AssistantError):
    """Raised when context management operations fail."""
    
    def __init__(
        self, 
        message: str = "Context operation failed", 
        context_type: str = None,
        **kwargs
    ):
        super().__init__(message, error_code="CONTEXT_ERROR", **kwargs)
        if context_type:
            self.details["context_type"] = context_type


class ContextStaleError(ContextError):
    """Raised when context is stale and needs refresh."""
    
    def __init__(
        self, 
        message: str = "Context is stale and needs refresh", 
        last_updated: str = None,
        **kwargs
    ):
        super().__init__(message, error_code="CONTEXT_STALE", **kwargs)
        if last_updated:
            self.details["last_updated"] = last_updated


class ConfigurationError(AssistantError):
    """Raised when assistant configuration is invalid."""
    
    def __init__(
        self, 
        message: str = "Invalid assistant configuration", 
        config_field: str = None,
        config_value: Any = None,
        **kwargs
    ):
        super().__init__(message, error_code="CONFIGURATION_ERROR", **kwargs)
        if config_field:
            self.details["config_field"] = config_field
        if config_value is not None:
            self.details["config_value"] = str(config_value)


class ConflictResolutionError(SchedulingError):
    """Raised when conflict resolution fails."""
    
    def __init__(
        self, 
        message: str = "Failed to resolve scheduling conflicts", 
        conflict_count: int = None,
        **kwargs
    ):
        super().__init__(message, error_code="CONFLICT_RESOLUTION_ERROR", **kwargs)
        if conflict_count:
            self.details["conflict_count"] = conflict_count


class VoiceProcessingError(AssistantError):
    """Raised when voice input/output processing fails."""
    
    def __init__(
        self, 
        message: str = "Voice processing failed", 
        processing_stage: str = None,
        **kwargs
    ):
        super().__init__(message, error_code="VOICE_PROCESSING_ERROR", **kwargs)
        if processing_stage:
            self.details["processing_stage"] = processing_stage


# Utility Functions
def get_assistant_error_details(error: Exception) -> Dict[str, Any]:
    """Extract structured error details from any assistant exception.
    
    Args:
        error: Exception to extract details from
        
    Returns:
        Dictionary with error details
    """
    details = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    
    # Add specific details for assistant errors
    if isinstance(error, AssistantError):
        details["error_code"] = error.error_code
        details.update(error.details)
    
    return details


def is_retryable_assistant_error(error: Exception) -> bool:
    """Determine if an assistant error is retryable.
    
    Args:
        error: Exception to check
        
    Returns:
        True if the error is likely transient and retryable
    """
    retryable_errors = (
        WorkflowTimeoutError,
        ServiceIntegrationError,
        ContextStaleError,
        VoiceProcessingError,
    )
    
    # Don't retry configuration or session errors
    non_retryable_errors = (
        ConfigurationError,
        SessionExpiredError,
        ConflictResolutionError,
    )
    
    if isinstance(error, non_retryable_errors):
        return False
        
    if isinstance(error, retryable_errors):
        return True
        
    # For generic service or network errors, assume retryable
    error_str = str(error).lower()
    if any(keyword in error_str for keyword in ["timeout", "connection", "network", "service"]):
        return True
        
    return False


def should_fallback_to_text(error: Exception) -> bool:
    """Determine if voice error should fallback to text mode.
    
    Args:
        error: Exception to check
        
    Returns:
        True if should fallback to text mode
    """
    if isinstance(error, VoiceProcessingError):
        return True
        
    error_str = str(error).lower()
    voice_keywords = ["audio", "speech", "voice", "microphone", "speaker"]
    return any(keyword in error_str for keyword in voice_keywords) 