"""
mAIgic Integrations Package.

This package provides integrations with various external services and APIs
for the mAIgic AI assistant platform.

Key Components:
- IntegrationRegistry: Central registry for discovering and creating clients
- IntegrationConfig: Environment-driven configuration management
- CredentialManager: Secure credential storage and management
"""

from typing import List

# Core integration system
from .config import IntegrationConfig
from .credentials import CredentialManager, create_credential_manager
from .registry import (
    IntegrationRegistry,
    create_calendar_client,
    create_email_client,
    get_available_integrations,
    get_registry,
)

__version__ = "0.1.0"

__all__: List[str] = [
    # Core integration system
    "IntegrationConfig",
    "CredentialManager",
    "create_credential_manager",
    "IntegrationRegistry",
    "get_registry",
    "create_calendar_client",
    "create_email_client",
    "get_available_integrations",

    # Integration modules
    "email",
    "calendar",
]
