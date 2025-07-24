"""
Email API exception classes.

This module defines the exception hierarchy for email operations.
All email implementations should raise these exceptions for consistent error handling.
"""

from typing import Any, List, Optional


class EmailAPIError(Exception):
    """Base exception for all email API errors."""

    def __init__(self, message: str, error_code: Optional[str] = None, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.original_error = original_error


class EmailConnectionError(EmailAPIError):
    """Raised when connection to email provider fails."""
    pass


class EmailAuthenticationError(EmailAPIError):
    """Raised when authentication with email provider fails."""
    pass


class EmailAuthorizationError(EmailAPIError):
    """Raised when user lacks permission for requested operation."""
    pass


class EmailNotFoundError(EmailAPIError):
    """Raised when requested email or resource is not found."""
    pass


class EmailValidationError(EmailAPIError):
    """Raised when email data validation fails."""
    pass


class EmailSendError(EmailAPIError):
    """Raised when email sending fails."""

    def __init__(
        self,
        message: str = "Failed to send email",
        failed_recipients: Optional[List[str]] = None,
        provider: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(message, provider)
        self.failed_recipients = failed_recipients or []

        # Support additional fields like error_code, original_error
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.failed_recipients:
            return f"{base_msg} (failed recipients: {', '.join(self.failed_recipients)})"
        return base_msg


class EmailReceiveError(EmailAPIError):
    """Raised when email retrieval fails."""
    pass


class EmailSearchError(EmailAPIError):
    """Raised when email search operation fails."""
    pass


class EmailAttachmentError(EmailAPIError):
    """Raised when email attachment operations fail."""

    def __init__(
        self,
        message: str = "Attachment operation failed",
        attachment_id: Optional[str] = None,
        provider: Optional[str] = None
    ) -> None:
        super().__init__(message, provider)
        self.attachment_id = attachment_id

    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.attachment_id:
            return f"{base_msg} (attachment: {self.attachment_id})"
        return base_msg


class EmailFolderError(EmailAPIError):
    """Raised when folder operations fail."""
    pass


class EmailQuotaExceededError(EmailAPIError):
    """Raised when email quota limits are exceeded."""
    pass


class EmailRateLimitError(EmailAPIError):
    """Raised when API rate limits are exceeded."""

    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs: Any) -> None:
        super().__init__(message, **kwargs)
        self.retry_after = retry_after  # Seconds until retry is allowed


class EmailProviderError(EmailAPIError):
    """Raised when email provider returns an error."""

    def __init__(self, message: str, provider_response: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(message, **kwargs)
        self.provider_response = provider_response


class EmailConfigurationError(EmailAPIError):
    """Raised when email client configuration is invalid."""
    pass


class EmailTimeoutError(EmailAPIError):
    """Raised when email operations timeout."""
    pass


class EmailUpdateError(EmailAPIError):
    """Raised when email update operations fail."""

    def __init__(
        self,
        message: str = "Email update failed",
        message_ids: Optional[List[str]] = None,
        provider: Optional[str] = None
    ) -> None:
        super().__init__(message, provider)
        self.message_ids = message_ids or []

    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.message_ids:
            return f"{base_msg} (messages: {len(self.message_ids)} items)"
        return base_msg


# Convenience mapping for common HTTP status codes to exceptions
HTTP_ERROR_MAP = {
    400: EmailValidationError,
    401: EmailAuthenticationError,
    403: EmailAuthorizationError,
    404: EmailNotFoundError,
    413: EmailQuotaExceededError,
    429: EmailRateLimitError,
    500: EmailProviderError,
    502: EmailConnectionError,
    503: EmailConnectionError,
    504: EmailTimeoutError,
}
