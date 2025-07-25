"""
Integration registry and factory for mAIgic integrations.

Discovers available providers and creates appropriate clients based on service type.
Handles the complexity of optional dependencies and provides clean factory interfaces.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .config import IntegrationConfig
from .credentials import CredentialManager, create_credential_manager

__all__ = [
    "IntegrationProvider",
    "CalendarIntegrationProvider",
    "EmailIntegrationProvider",
    "IntegrationRegistry",
    "CredentialManager",
    "get_registry",
    "create_calendar_client",
    "create_email_client",
    "get_available_integrations"
]

if TYPE_CHECKING:
    from .calendar.calendar_api.interfaces import CalendarClient
    from .email.email_api.interfaces import EmailClient


class IntegrationProvider(ABC):
    """Base class for all integration providers."""

    @abstractmethod
    def get_service_name(self) -> str:
        """Get the service name for this provider."""
        pass  # pragma: no cover

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider's dependencies are available."""
        pass  # pragma: no cover

    @abstractmethod
    def create_client(self, user_id: str, credential_manager: CredentialManager, **kwargs: Any) -> Any:
        """Create a client instance for this provider."""
        pass  # pragma: no cover

    @abstractmethod
    def get_required_credentials(self) -> List[str]:
        """Get list of required credential keys for this provider."""
        pass  # pragma: no cover


class CalendarIntegrationProvider(IntegrationProvider):
    """Provider interface for calendar integrations."""

    @abstractmethod
    def create_client(self, user_id: str, credential_manager: CredentialManager, **kwargs: Any) -> "CalendarClient":
        """Create a calendar client instance."""
        pass  # pragma: no cover


class EmailIntegrationProvider(IntegrationProvider):
    """Provider interface for email integrations."""

    @abstractmethod
    def create_client(self, user_id: str, credential_manager: CredentialManager, **kwargs: Any) -> "EmailClient":
        """Create an email client instance."""
        pass  # pragma: no cover


class IntegrationRegistry:
    """Central registry for all integration providers."""

    def __init__(self, config: Optional[IntegrationConfig] = None) -> None:
        self.config = config or IntegrationConfig.from_env()
        self.credential_manager = create_credential_manager(self.config)
        self._providers: Dict[str, IntegrationProvider] = {}
        self._discover_providers()

    def _discover_providers(self) -> None:
        """Discover and register all available providers."""
        # Calendar providers
        self._register_calendar_providers()

        # Email providers
        self._register_email_providers()

    def _register_calendar_providers(self) -> None:
        """Register available calendar providers."""
        # Google Calendar
        if self.config.google_calendar_enabled:
            try:
                from .calendar.calendar_google_impl.providers import (
                    GoogleCalendarProvider,
                )
                provider = GoogleCalendarProvider()
                if provider.is_available():
                    self._providers[provider.get_service_name()] = provider
            except ImportError:
                pass

        # Microsoft Outlook
        if self.config.microsoft_outlook_enabled:
            try:
                # from .calendar.calendar_outlook_impl.providers import OutlookCalendarProvider
                # provider = OutlookCalendarProvider()
                # if provider.is_available():
                #     self._providers[provider.get_service_name()] = provider
                pass
            except ImportError:
                pass

    def _register_email_providers(self) -> None:
        """Register available email providers."""
        # Google Gmail
        if self.config.google_gmail_enabled:
            try:
                from .email.email_gmail_impl.providers import GmailProvider
                provider = GmailProvider()
                if provider.is_available():
                    self._providers[provider.get_service_name()] = provider
            except ImportError:
                pass

    def get_available_providers(self) -> List[str]:
        """Get list of all available provider names."""
        return list(self._providers.keys())

    def get_calendar_providers(self) -> List[str]:
        """Get list of available calendar provider names."""
        return [
            service for service, provider in self._providers.items()
            if isinstance(provider, CalendarIntegrationProvider)
        ]

    def get_email_providers(self) -> List[str]:
        """Get list of available email provider names."""
        return [
            service for service, provider in self._providers.items()
            if isinstance(provider, EmailIntegrationProvider)
        ]

    def has_provider(self, service: str) -> bool:
        """Check if a provider is available for the given service."""
        return service in self._providers

    def get_provider(self, service: str) -> Optional[IntegrationProvider]:
        """Get a provider instance by service name."""
        return self._providers.get(service)

    def create_calendar_client(self, service: str, user_id: str = "default", **kwargs: Any) -> "CalendarClient":
        """Create a calendar client for the specified service."""
        if service not in self._providers:
            raise ValueError(f"Calendar provider '{service}' not available. Available: {self.get_calendar_providers()}")

        provider = self._providers[service]
        if not isinstance(provider, CalendarIntegrationProvider):
            raise ValueError(f"Provider '{service}' is not a calendar provider")

        return provider.create_client(user_id, self.credential_manager, **kwargs)

    def create_email_client(self, service: str, user_id: str = "default", **kwargs: Any) -> "EmailClient":
        """Create an email client for the specified service."""
        if service not in self._providers:
            raise ValueError(f"Email provider '{service}' not available. Available: {self.get_email_providers()}")

        provider = self._providers[service]
        if not isinstance(provider, EmailIntegrationProvider):
            raise ValueError(f"Provider '{service}' is not an email provider")

        return provider.create_client(user_id, self.credential_manager, **kwargs)

    def create_client(self, service: str, user_id: str = "default", **kwargs: Any) -> Any:
        """Create a client for any service type."""
        if service not in self._providers:
            available = ", ".join(self.get_available_providers())
            raise ValueError(f"Provider '{service}' not available. Available: {available}")

        provider = self._providers[service]
        return provider.create_client(user_id, self.credential_manager, **kwargs)

    def get_provider_info(self, service: str) -> Dict[str, Any]:
        """Get information about a provider."""
        if service not in self._providers:
            return {}

        provider = self._providers[service]
        return {
            "service": service,
            "available": provider.is_available(),
            "required_credentials": provider.get_required_credentials(),
            "type": "calendar" if isinstance(provider, CalendarIntegrationProvider) else "email"
        }

    def list_user_integrations(self, user_id: str) -> Dict[str, Dict[str, Any]]:
        """List all integrations available for a user."""
        integrations = {}

        for service, provider in self._providers.items():
            has_credentials = self.credential_manager.has_credentials(user_id, service)
            integrations[service] = {
                "available": provider.is_available(),
                "has_credentials": has_credentials,
                "required_credentials": provider.get_required_credentials(),
                "type": "calendar" if isinstance(provider, CalendarIntegrationProvider) else "email"
            }

        return integrations


# Global registry instance
_registry: Optional[IntegrationRegistry] = None


def get_registry(config: Optional[IntegrationConfig] = None) -> IntegrationRegistry:
    """Get the global integration registry instance."""
    global _registry
    if _registry is None or config is not None:
        _registry = IntegrationRegistry(config)
    return _registry


def create_calendar_client(service: str, user_id: str = "default", config: Optional[IntegrationConfig] = None, **kwargs: Any) -> "CalendarClient":
    """Convenience function to create a calendar client."""
    registry = get_registry(config)
    return registry.create_calendar_client(service, user_id, **kwargs)


def create_email_client(service: str, user_id: str = "default", config: Optional[IntegrationConfig] = None, **kwargs: Any) -> "EmailClient":
    """Convenience function to create an email client."""
    registry = get_registry(config)
    return registry.create_email_client(service, user_id, **kwargs)


def get_available_integrations(config: Optional[IntegrationConfig] = None) -> List[str]:
    """Convenience function to get available integrations."""
    registry = get_registry(config)
    return registry.get_available_providers()
