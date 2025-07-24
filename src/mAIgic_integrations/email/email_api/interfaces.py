"""
Email API interface definitions.

This module defines the abstract interfaces that all email implementations must follow.
The interfaces are designed for AI personal assistants that need to gather email context.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional

from .models import Email, EmailStats


class EmailClient(ABC):
    """
    Email interface focused on AI personal assistant context gathering.

    This interface is designed for AI assistants that need to:
    - Understand user's email context for better assistance
    - Read and analyze emails to provide insights
    - Help users organize and manage their email

    Uses async context manager pattern for automatic connection management.

    Example usage:
        async with SomeEmailClient(config) as client:
            emails = await client.get_emails()
            results = await client.search_emails("important")
            stats = await client.get_account_info()
    """

    @abstractmethod
    async def __aenter__(self) -> "EmailClient":
        """
        Async context manager entry.

        Automatically handles authentication and connection setup.

        Returns:
            Self for use in async with statement

        Raises:
            EmailConnectionError: If connection fails
            EmailAuthenticationError: If authentication fails
        """
        pass

    @abstractmethod
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Async context manager exit.

        Automatically handles cleanup and disconnection.
        Safe to call even if connection failed.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        pass

    @abstractmethod
    async def get_emails(
        self,
        folder: str = "INBOX",
        limit: int = 50,
        include_body: bool = True,
        since_days: Optional[int] = None
    ) -> List[Email]:
        """
        Get emails for AI context analysis.

        This is the primary method AI assistants use to understand
        what's happening in the user's email world.

        Args:
            folder: Email folder/label to read from
            limit: Maximum number of emails to return
            include_body: Whether to include full email body content
            since_days: Only get emails from last N days (None = all emails)

        Returns:
            List of Email objects sorted by date (newest first)

        Raises:
            EmailConnectionError: If not connected or connection fails
            EmailReceiveError: If unable to retrieve emails
        """
        pass

    @abstractmethod
    async def search_emails(self, query: str, limit: int = 10) -> List[Email]:
        """
        Search emails for AI analysis.

        AI assistants need to find specific emails based on user queries
        like "show me emails about the project" or "urgent emails from boss".

        Args:
            query: Natural search query
            limit: Maximum results to return

        Returns:
            List of matching Email objects

        Raises:
            EmailConnectionError: If not connected or connection fails
            EmailSearchError: If search operation fails
        """
        pass

    @abstractmethod
    async def get_recent_emails(self, days: int = 7) -> List[Email]:
        """
        Get recent emails for AI context.

        This is what AI assistants typically need - recent email context
        to understand what's happening in the user's email.

        Args:
            days: Number of days back to search

        Returns:
            List of recent emails sorted by date (newest first)

        Raises:
            EmailConnectionError: If not connected or connection fails
            EmailReceiveError: If unable to retrieve emails
        """
        pass

    @abstractmethod
    async def get_email(self, message_id: str) -> Email:
        """
        Get a specific email by ID with full content.

        Args:
            message_id: Unique email identifier

        Returns:
            Complete Email object with full content

        Raises:
            EmailConnectionError: If not connected or connection fails
            EmailNotFoundError: If email with given ID doesn't exist
            EmailReceiveError: If unable to retrieve email
        """
        pass

    @abstractmethod
    async def get_account_info(self) -> EmailStats:
        """
        Get email account statistics for AI context.

        Returns:
            EmailStats object with account information

        Raises:
            EmailConnectionError: If not connected or connection fails
            EmailReceiveError: If unable to retrieve account info
        """
        pass

    @abstractmethod
    async def download_attachment(self, message_id: str, attachment_id: str) -> bytes:
        """
        Download email attachment content.

        Args:
            message_id: Email message ID containing the attachment
            attachment_id: Specific attachment identifier

        Returns:
            Raw attachment data as bytes

        Raises:
            EmailConnectionError: If not connected or connection fails
            EmailNotFoundError: If message or attachment doesn't exist
            EmailAttachmentError: If unable to download attachment
        """
        pass


class EmailProvider(ABC):
    """
    Abstract base class for email provider implementations.

    This interface defines provider-specific configuration and setup.
    """

    @abstractmethod
    def create_client(self, **config: Any) -> EmailClient:
        """
        Create an email client instance for this provider.

        Args:
            **config: Provider-specific configuration parameters

        Returns:
            Configured email client instance

        Raises:
            EmailConfigurationError: If configuration is invalid
        """
        pass

    @abstractmethod
    def validate_config(self, **config: Any) -> bool:
        """
        Validate provider-specific configuration.

        Args:
            **config: Configuration parameters to validate

        Returns:
            True if configuration is valid

        Raises:
            EmailConfigurationError: If configuration is invalid
        """
        pass

    @abstractmethod
    def get_required_config_keys(self) -> List[str]:
        """
        Get list of required configuration keys for this provider.

        Returns:
            List of required configuration key names
        """
        pass

    @abstractmethod
    def get_optional_config_keys(self) -> List[str]:
        """Get list of optional configuration keys."""
        pass

    @abstractmethod
    def get_config_description(self) -> str:
        """Get human-readable description of configuration requirements."""
        pass
