"""
Email API Package.

This package provides abstract interfaces and data types for email operations.
It follows the same clean architecture pattern as the speech API.
"""

from .exceptions import (
    HTTP_ERROR_MAP,
    EmailAPIError,
    EmailAttachmentError,
    EmailAuthenticationError,
    EmailAuthorizationError,
    EmailConfigurationError,
    EmailConnectionError,
    EmailFolderError,
    EmailNotFoundError,
    EmailProviderError,
    EmailQuotaExceededError,
    EmailRateLimitError,
    EmailReceiveError,
    EmailSearchError,
    EmailSendError,
    EmailTimeoutError,
    EmailValidationError,
)
from .interfaces import (
    EmailClient,
    EmailProvider,
)
from .models import (
    Attachment,
    AttachmentList,
    AttachmentType,
    Email,
    EmailAddress,
    EmailFolder,
    EmailList,
    EmailPriority,
    EmailSearchQuery,
    EmailSearchResult,
    EmailStats,
    EmailStatus,
    EmailThread,
    EmailUpdateRequest,
    RecipientList,
)

__all__ = [
    # Core interfaces
    "EmailClient",
    "EmailProvider",

    # Data types
    "Email",
    "EmailAddress",
    "EmailFolder",
    "EmailThread",
    "EmailSearchQuery",
    "EmailSearchResult",
    "EmailStats",
    "EmailUpdateRequest",
    "Attachment",

    # Enums
    "EmailPriority",
    "EmailStatus",
    "AttachmentType",

    # Type aliases
    "EmailList",
    "RecipientList",
    "AttachmentList",

    # Exceptions
    "EmailAPIError",
    "EmailConnectionError",
    "EmailAuthenticationError",
    "EmailAuthorizationError",
    "EmailNotFoundError",
    "EmailValidationError",
    "EmailSendError",
    "EmailReceiveError",
    "EmailSearchError",
    "EmailAttachmentError",
    "EmailFolderError",
    "EmailQuotaExceededError",
    "EmailRateLimitError",
    "EmailProviderError",
    "EmailConfigurationError",
    "EmailTimeoutError",
    "HTTP_ERROR_MAP",
]
