"""Exception hierarchy for mAIgic_core LLM API.

This module defines all exceptions that can be raised by the LLM API,
providing clear error types for different failure scenarios.
"""


class LLMError(Exception):
    """Base exception for all LLM-related errors."""
    
    def __init__(self, message: str, error_code: str = "LLM_ERROR", details: dict = None):
        """Initialize LLM error.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class LLMConnectionError(LLMError):
    """Raised when LLM service is unavailable or connection fails."""
    
    def __init__(self, message: str = "Failed to connect to LLM service", **kwargs):
        super().__init__(message, error_code="LLM_CONNECTION_ERROR", **kwargs)


class LLMTimeoutError(LLMConnectionError):
    """Raised when LLM request times out."""
    
    def __init__(self, message: str = "LLM request timed out", timeout_seconds: float = None, **kwargs):
        super().__init__(message, error_code="LLM_TIMEOUT_ERROR", **kwargs)
        if timeout_seconds:
            self.details["timeout_seconds"] = timeout_seconds


class LLMRateLimitError(LLMConnectionError):
    """Raised when LLM provider rate limits are exceeded."""
    
    def __init__(self, message: str = "LLM rate limit exceeded", retry_after: int = None, **kwargs):
        super().__init__(message, error_code="LLM_RATE_LIMIT_ERROR", **kwargs)
        if retry_after:
            self.details["retry_after_seconds"] = retry_after


class LLMAuthenticationError(LLMError):
    """Raised when LLM provider authentication fails."""
    
    def __init__(self, message: str = "LLM authentication failed", **kwargs):
        super().__init__(message, error_code="LLM_AUTH_ERROR", **kwargs)


class LLMConfigurationError(LLMError):
    """Raised when LLM configuration is invalid."""
    
    def __init__(self, message: str = "Invalid LLM configuration", config_field: str = None, **kwargs):
        super().__init__(message, error_code="LLM_CONFIG_ERROR", **kwargs)
        if config_field:
            self.details["config_field"] = config_field


class LLMProviderError(LLMError):
    """Base exception for provider-specific errors."""
    
    def __init__(self, message: str, provider_name: str = None, **kwargs):
        super().__init__(message, error_code="LLM_PROVIDER_ERROR", **kwargs)
        if provider_name:
            self.details["provider"] = provider_name


class LLMModelNotFoundError(LLMProviderError):
    """Raised when specified model is not available."""
    
    def __init__(
        self, 
        message: str = "Model not found", 
        model_name: str = None, 
        available_models: list = None,
        **kwargs
    ):
        super().__init__(message, error_code="LLM_MODEL_NOT_FOUND", **kwargs)
        if model_name:
            self.details["requested_model"] = model_name
        if available_models:
            self.details["available_models"] = available_models


class LLMResponseError(LLMError):
    """Raised when LLM response is invalid or cannot be parsed."""
    
    def __init__(
        self, 
        message: str = "Invalid LLM response", 
        response_text: str = None,
        expected_format: str = None,
        **kwargs
    ):
        super().__init__(message, error_code="LLM_RESPONSE_ERROR", **kwargs)
        if response_text:
            self.details["response_text"] = response_text
        if expected_format:
            self.details["expected_format"] = expected_format


class LLMIntentParsingError(LLMResponseError):
    """Raised when intent parsing fails or returns invalid structure."""
    
    def __init__(self, message: str = "Failed to parse user intent", **kwargs):
        super().__init__(message, error_code="LLM_INTENT_PARSING_ERROR", **kwargs)


class LLMSchedulingError(LLMResponseError):
    """Raised when scheduling decision generation fails."""
    
    def __init__(self, message: str = "Failed to generate scheduling decision", **kwargs):
        super().__init__(message, error_code="LLM_SCHEDULING_ERROR", **kwargs)


class LLMGoalAssessmentError(LLMResponseError):
    """Raised when goal progress assessment fails."""
    
    def __init__(self, message: str = "Failed to assess goal progress", **kwargs):
        super().__init__(message, error_code="LLM_GOAL_ASSESSMENT_ERROR", **kwargs)


# Conversation Repository Exceptions
class ConversationStorageError(Exception):
    """Base exception for conversation storage operations."""
    
    def __init__(self, message: str, operation: str = None, **kwargs):
        super().__init__(message)
        self.message = message
        self.operation = operation
        self.details = kwargs


class ConversationSaveError(ConversationStorageError):
    """Raised when saving conversation interaction fails."""
    
    def __init__(self, message: str = "Failed to save conversation interaction", **kwargs):
        super().__init__(message, operation="save", **kwargs)


class ConversationRetrievalError(ConversationStorageError):
    """Raised when retrieving conversation history fails."""
    
    def __init__(self, message: str = "Failed to retrieve conversation history", **kwargs):
        super().__init__(message, operation="retrieve", **kwargs)


class ConversationDeleteError(ConversationStorageError):
    """Raised when deleting conversation data fails."""
    
    def __init__(self, message: str = "Failed to delete conversation data", **kwargs):
        super().__init__(message, operation="delete", **kwargs)


class ConversationFileError(ConversationStorageError):
    """Raised when file operations fail in file-based storage."""
    
    def __init__(
        self, 
        message: str = "Conversation file operation failed", 
        file_path: str = None,
        **kwargs
    ):
        super().__init__(message, operation="file", **kwargs)
        if file_path:
            self.details["file_path"] = file_path


# Factory Exception
class LLMFactoryError(LLMError):
    """Raised when LLM client factory operations fail."""
    
    def __init__(
        self, 
        message: str = "LLM factory operation failed", 
        provider_name: str = None,
        **kwargs
    ):
        super().__init__(message, error_code="LLM_FACTORY_ERROR", **kwargs)
        if provider_name:
            self.details["provider_name"] = provider_name


# Utility Functions
def get_error_details(error: Exception) -> dict:
    """Extract structured error details from any exception.
    
    Args:
        error: Exception to extract details from
        
    Returns:
        Dictionary with error details
    """
    details = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    
    # Add specific details for LLM errors
    if isinstance(error, LLMError):
        details["error_code"] = error.error_code
        details.update(error.details)
    
    # Add specific details for conversation errors
    if isinstance(error, ConversationStorageError):
        details["operation"] = error.operation
        details.update(error.details)
    
    return details


def is_retryable_error(error: Exception) -> bool:
    """Determine if an error is retryable.
    
    Args:
        error: Exception to check
        
    Returns:
        True if the error is likely transient and retryable
    """
    retryable_errors = (
        LLMTimeoutError,
        LLMRateLimitError,
        LLMConnectionError,
        ConversationFileError,
    )
    
    # Don't retry authentication or configuration errors
    non_retryable_errors = (
        LLMAuthenticationError,
        LLMConfigurationError,
        LLMModelNotFoundError,
    )
    
    if isinstance(error, non_retryable_errors):
        return False
        
    if isinstance(error, retryable_errors):
        return True
        
    # For generic connection errors, assume retryable
    if "connection" in str(error).lower() or "timeout" in str(error).lower():
        return True
        
    return False