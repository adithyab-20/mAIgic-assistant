"""
Gmail implementation for mAIgic Email API.

This package provides Gmail-specific implementation of the EmailClient interface,
focused on AI assistant context gathering needs.
"""

from .clients import GmailClient
from .config import GmailConfig, get_default_gmail_config
from .providers import GmailProvider, create_gmail_client, create_gmail_client_from_env

__all__ = [
    "GmailClient",
    "GmailConfig",
    "get_default_gmail_config",
    "GmailProvider",
    "create_gmail_client",
    "create_gmail_client_from_env",
]
