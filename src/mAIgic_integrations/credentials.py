"""Credential management for mAIgic integrations."""

import hashlib
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

from .config import IntegrationConfig


class CredentialManager(ABC):
    """Abstract base class for credential management."""

    @abstractmethod
    def has_credentials(self, user_id: str, service: str) -> bool:
        """Check if credentials exist for user/service."""
        pass

    @abstractmethod
    def get_credentials(self, user_id: str, service: str) -> Optional[Dict[str, Any]]:
        """Get credentials for user/service."""
        pass

    @abstractmethod
    def store_credentials(self, user_id: str, service: str, credentials: Dict[str, Any]) -> None:
        """Store credentials for user/service."""
        pass

    @abstractmethod
    def delete_credentials(self, user_id: str, service: str) -> None:
        """Delete credentials for user/service."""
        pass


class FileCredentialManager(CredentialManager):
    """File-based credential management."""

    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.base_dir = Path(config.credentials_dir)
        self.base_dir.mkdir(exist_ok=True)

    def _get_user_hash(self, user_id: str) -> str:
        """Get consistent hash for user ID."""
        return hashlib.sha256(user_id.encode()).hexdigest()[:8]

    def _get_metadata_path(self, user_id: str, service: str) -> Path:
        """Get path to credential metadata file."""
        user_hash = self._get_user_hash(user_id)
        return self.base_dir / f"{user_hash}_{service}.json"

    def has_credentials(self, user_id: str, service: str) -> bool:
        """Check if credentials exist for user/service."""
        metadata_path = self._get_metadata_path(user_id, service)
        if not metadata_path.exists():
            return False

        try:
            metadata = self._load_metadata(metadata_path)
            # Check that all required paths exist
            if "credentials_path" in metadata:
                credentials_path = Path(metadata["credentials_path"])
                if not credentials_path.exists():
                    return False

            if "token_path" in metadata:
                # Token might not exist initially (OAuth flow creates it)
                # So we don't require it to exist
                pass

            return True
        except (json.JSONDecodeError, OSError):
            return False

    def get_credentials(self, user_id: str, service: str) -> Optional[Dict[str, Any]]:
        """Get credentials for user/service."""
        if not self.has_credentials(user_id, service):
            return None

        metadata_path = self._get_metadata_path(user_id, service)
        return self._load_metadata(metadata_path)

    def store_credentials(self, user_id: str, service: str, credentials: Dict[str, Any]) -> None:
        """Store credentials for user/service."""
        metadata_path = self._get_metadata_path(user_id, service)

        # Ensure directory exists
        metadata_path.parent.mkdir(parents=True, exist_ok=True)

        # Add metadata
        credentials_with_metadata = {
            **credentials,
            "user_id": user_id,
            "service": service,
            "created_by": "mAIgic_integrations_setup"
        }

        try:
            with open(metadata_path, 'w') as f:
                json.dump(credentials_with_metadata, f, indent=2)
        except (OSError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to store credentials: {e}") from e

    def delete_credentials(self, user_id: str, service: str) -> None:
        """Delete credentials for user/service."""
        metadata_path = self._get_metadata_path(user_id, service)
        if metadata_path.exists():
            metadata_path.unlink()

    def _load_metadata(self, path: Path) -> Dict[str, Any]:
        """Load metadata from file."""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                # Ensure we return a dict
                if not isinstance(data, dict):
                    raise RuntimeError(f"Metadata file {path} does not contain a JSON object")
                return data
        except (OSError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to load metadata from {path}: {e}") from e


def create_credential_manager(config: IntegrationConfig) -> CredentialManager:
    """Create credential manager based on configuration."""
    if config.credential_storage == "file":
        return FileCredentialManager(config)
    else:
        raise ValueError(f"Unsupported credential storage: {config.credential_storage}")
