"""
Email Integration Package.

This package provides a unified interface for email operations with a clean architecture
that supports multiple email providers. Currently includes a comprehensive Gmail implementation
with full OAuth2 support, async/await patterns, and robust error handling.

The package includes:
- Abstract email API interfaces and types
- Gmail implementation with OAuth2 authentication
- Comprehensive exception hierarchy
- Full async/await support
- Type safety throughout

Example usage:
    # Gmail client usage
    from mAIgic_integrations.email import GmailClient, GmailConfig

    config = GmailConfig(
        credentials_path="credentials.json",
        token_path="token.json"
    )

    async with GmailClient(config) as client:
        # Get recent emails
        emails = await client.get_recent_emails(days=7)

        # Search emails
        results = await client.search_emails("important project")

        # Get account statistics
        stats = await client.get_account_info()
        print(f"Total emails: {stats.total_messages}")
"""

# Core email types and enums
# Exception hierarchy
from .email_api.exceptions import (
    EmailAPIError,
    EmailAttachmentError,
    EmailAuthenticationError,
    EmailConfigurationError,
    EmailConnectionError,
    EmailFolderError,
    EmailNotFoundError,
    EmailQuotaExceededError,
    EmailRateLimitError,
    EmailReceiveError,
    EmailSearchError,
    EmailSendError,
    EmailValidationError,
)

# Abstract interfaces
from .email_api.interfaces import (
    EmailClient,
    EmailProvider,
)
from .email_api.models import (
    Attachment,
    AttachmentType,
    Email,
    EmailAddress,
    EmailFolder,
    EmailPriority,
    EmailSearchQuery,
    EmailSearchResult,
    EmailStats,
    EmailStatus,
    EmailThread,
)

# Gmail implementation
from .email_gmail_impl import (
    GmailClient,
    GmailConfig,
    GmailProvider,
)

__all__ = [
    # Core data types
    "Email",
    "EmailAddress",
    "EmailFolder",
    "EmailSearchQuery",
    "EmailSearchResult",
    "EmailStats",
    "EmailThread",
    "Attachment",
    "EmailPriority",
    "EmailStatus",
    "AttachmentType",

    # Abstract interfaces
    "EmailClient",
    "EmailProvider",

    # Exception hierarchy
    "EmailAPIError",
    "EmailConnectionError",
    "EmailAuthenticationError",
    "EmailValidationError",
    "EmailSendError",
    "EmailReceiveError",
    "EmailSearchError",
    "EmailNotFoundError",
    "EmailFolderError",
    "EmailAttachmentError",
    "EmailRateLimitError",
    "EmailQuotaExceededError",
    "EmailConfigurationError",

    # Gmail implementation
    "GmailClient",
    "GmailProvider",
    "GmailConfig",
]

# Version information
__version__ = "0.1.0"
__author__ = "mAIgic Assistant"
__description__ = "Gmail integration package with comprehensive EmailClient interface"
