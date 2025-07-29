#!/usr/bin/env python3
"""
mAIgic Integration Setup - Single Entry Point

This is the unified setup system for all mAIgic integrations.

Key Features:
- Single entry point for all integrations
- Interactive discovery and setup
- Environment variable support for simple credentials
- Service-specific directories for complex OAuth
- Profile support for multiple users/environments
- Progressive complexity (simple by default, powerful when needed)

Usage:
    uv run maigic-integrations-setup                # Interactive setup wizard
    uv run maigic-integrations-setup --list         # Show current configuration
    uv run maigic-integrations-setup --service=calendar  # Setup specific service
    uv run maigic-integrations-setup --test         # Test all configured integrations

Alternative usage:
    uv run -m mAIgic_integrations.setup             # Using module flag
"""

import argparse  # pragma: no cover
import json  # pragma: no cover
import os  # pragma: no cover
import sys  # pragma: no cover
import webbrowser  # pragma: no cover
from pathlib import Path  # pragma: no cover
from typing import Any, Dict, List  # pragma: no cover

# Load environment variables from .env file
try:
    from dotenv import load_dotenv  # pragma: no cover
    load_dotenv()  # pragma: no cover
except ImportError:  # pragma: no cover
    pass  # pragma: no cover

# Core imports  # pragma: no cover
from .config import IntegrationConfig  # pragma: no cover
from .credentials import create_credential_manager  # pragma: no cover
from .registry import get_registry  # pragma: no cover


class IntegrationSetup:  # pragma: no cover
    """Unified setup system for mAIgic integrations."""

    def __init__(self, profile: str = "default"):
        """Initialize setup system.

        Args:
            profile: User profile name
        """
        self.profile = profile
        self.config = IntegrationConfig.from_env()
        self.registry = get_registry()
        self.credential_manager = create_credential_manager(self.config)

        # Create credentials directory if it doesn't exist
        self.credentials_dir = Path(self.config.credentials_dir)
        self.credentials_dir.mkdir(parents=True, exist_ok=True)

    def discover_integrations(self) -> Dict[str, Dict[str, Any]]:
        """Discover available integrations and their status.

        Returns:
            Dict mapping service names to their info and status
        """
        print("Discovering available integrations...")

        available = {}
        for service in self.registry.get_available_providers():
            info = self.registry.get_provider_info(service)
            has_creds = self.credential_manager.has_credentials(self.profile, service)

            available[service] = {
                **info,
                "has_credentials": has_creds,
                "configured": has_creds and info.get("available", False)
            }

        return available

    def print_status(self) -> None:
        """Print current integration status."""
        print(f"\nIntegration Status (Profile: {self.profile})")
        print("=" * 60)

        integrations = self.discover_integrations()

        if not integrations:
            print("No integrations available")
            print("\nThis might indicate a package installation issue.")
            return

        for service, info in integrations.items():
            # Status indicator
            if info["configured"]:
                status = "[READY]"
            elif info["has_credentials"]:
                status = "[CREDENTIALS FOUND]"
            elif info.get("available", False):
                status = "[NEEDS CREDENTIALS]"
            else:
                status = "[UNAVAILABLE]"

            print(f"{status:<20} {service}")

            # Show required credentials
            if info.get("required_credentials"):
                req_creds = ", ".join(info["required_credentials"])
                print(f"{'':20} Required: {req_creds}")

        print()

    def setup_simple_credentials(self) -> None:
        """Setup simple API key based credentials via environment variables."""
        print("\nSimple Credential Setup")
        print("=" * 40)
        print("For services using API keys, we recommend using environment variables.")
        print()

        # Check for .env file
        env_path = Path(".env")
        env_exists = env_path.exists()

        if env_exists:
            print(f"Found existing .env file: {env_path.absolute()}")
        else:
            print(f"No .env file found. We'll help you create one at: {env_path.absolute()}")

        # Check for existing OpenAI key
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            print("Found existing OPENAI_API_KEY in environment")

        # Example environment variables
        print("\nRecommended environment variables:")
        print("# Add these to your .env file")

        if not openai_key:
            print("OPENAI_API_KEY=sk-...                  # For speech processing")
        else:
            print("OPENAI_API_KEY=sk-...                  # ✓ Already configured")

        print("ANTHROPIC_API_KEY=...                   # For Claude integration")
        print("GOOGLE_CALENDAR_ENABLED=true            # Enable Google Calendar")
        print("GOOGLE_GMAIL_ENABLED=true               # Enable Gmail")
        print()

        # Check if speech component is available
        try:
            from mAIgic_speech.speech_openai_impl import OpenAIConfig  # noqa: F401
            speech_available = True
        except ImportError:
            speech_available = False

        if speech_available:
            if openai_key:
                print("Speech component is available and configured")
            else:
                print("Speech component is available but needs OPENAI_API_KEY")
                print("See examples in: src/mAIgic_speech/examples/")
        else:
            print("Speech component not installed")
            print("To add speech capabilities: uv sync --extra speech")

        print()

        if not env_exists:
            create_env = input("Create .env.template file with examples? (y/n): ").lower() == 'y'
            if create_env:
                self._create_env_template()

    def _create_env_template(self) -> None:
        """Create .env.template file with examples."""
        template_content = """# mAIgic Assistant Environment Configuration
# Copy this file to .env and fill in your actual values

# =============================================================================
# Simple API Keys (No setup wizard needed - just add to .env)
# =============================================================================

# OpenAI API key for speech processing (speech-to-text, text-to-speech, realtime)
# Get from: https://platform.openai.com/api-keys
# Examples: src/mAIgic_speech/examples/
OPENAI_API_KEY=sk-your-openai-api-key-here

# Anthropic API key for Claude integration (future)
# Get from: https://console.anthropic.com/
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# =============================================================================
# Integration Enablement (Complex OAuth - use setup wizard)
# =============================================================================

# Google Calendar integration
# Setup: uv run maigic-integrations-setup --service calendar
GOOGLE_CALENDAR_ENABLED=true

# Google Gmail integration
# Setup: uv run maigic-integrations-setup --service gmail
GOOGLE_GMAIL_ENABLED=true

# Microsoft Outlook integration (future)
MICROSOFT_OUTLOOK_ENABLED=false

# =============================================================================
# Advanced Configuration
# =============================================================================

# Credentials storage directory for OAuth files
MAIGIC_CREDENTIALS_DIR=credentials

# Environment (development, staging, production)
MAIGIC_ENVIRONMENT=development

# Credential storage backend (file, vault)
MAIGIC_CREDENTIAL_STORAGE=file

# =============================================================================
# Component Setup Guide
# =============================================================================
#
# SPEECH PROCESSING (Simple - just API keys):
#   1. Get OpenAI API key from https://platform.openai.com/api-keys
#   2. Set OPENAI_API_KEY above
#   3. Run examples: uv run python src/mAIgic_speech/examples/batch_transcription.py
#
# EMAIL & CALENDAR (Complex - use setup wizard):
#   1. Run: uv run maigic-integrations-setup
#   2. Follow interactive prompts for OAuth setup
#   3. Use simple imports: create_calendar_client("google_calendar")
#
"""

        template_path = Path(".env.template")
        template_path.write_text(template_content)
        print(f"Created {template_path.absolute()}")
        print("Copy this to .env and add your actual API keys")
        print()
        print("Setup Guide:")
        print("  - Speech: Just add OPENAI_API_KEY to .env")
        print("  - Integrations: Run 'uv run maigic-integrations-setup' for OAuth setup")

    def setup_google_calendar(self) -> bool:
        """Setup Google Calendar OAuth credentials.

        Returns:
            True if setup was successful
        """
        print("\nGoogle Calendar Setup")
        print("=" * 40)

        service_dir = self.credentials_dir / "google_calendar"
        creds_file = service_dir / "credentials.json"
        token_file = service_dir / "token.json"

        # Check existing credentials
        if creds_file.exists():
            print(f"Found existing credentials: {creds_file}")
            if token_file.exists():
                print(f"Found existing token: {token_file}")
                if self._test_google_calendar():
                    print("Google Calendar is already working!")
                    return True

        print("\nTo use Google Calendar, you need OAuth2 credentials from Google Cloud Console.")
        print()
        print("Setup Steps:")
        print("1. Go to Google Cloud Console (https://console.cloud.google.com/)")
        print("2. Create a new project or select existing one")
        print("3. Enable the Google Calendar API")
        print("4. Create OAuth2 credentials (Desktop Application)")
        print("5. Download the credentials.json file")
        print()

        # Offer to open browser
        open_browser = input("Open Google Cloud Console in browser? (y/n): ").lower() == 'y'
        if open_browser:
            webbrowser.open("https://console.cloud.google.com/apis/credentials")

        print("\nPlease save your credentials.json file to:")
        print(f"   {creds_file.absolute()}")
        print()

        input("Press Enter when you've saved the credentials.json file...")

        # Validate and setup
        if self._setup_google_oauth(service_dir, "google_calendar"):
            print("Google Calendar setup completed!")
            return True
        else:
            print("Google Calendar setup failed")
            return False

    def setup_gmail(self) -> bool:
        """Setup Gmail OAuth credentials.

        Returns:
            True if setup was successful
        """
        print("\nGmail Setup")
        print("=" * 40)

        # Check if Google Calendar is already set up
        calendar_dir = self.credentials_dir / "google_calendar"
        calendar_creds = calendar_dir / "credentials.json"

        gmail_dir = self.credentials_dir / "google_gmail"
        gmail_creds = gmail_dir / "credentials.json"

        if gmail_creds.exists():
            if self._test_gmail():
                print("Gmail is already working!")
                return True

        # Offer to reuse Google Calendar credentials
        if calendar_creds.exists():
            print("Google Calendar credentials found!")
            print("Gmail can use the same OAuth2 application.")
            print()
            reuse = input("Use existing Google Calendar credentials for Gmail? (y/n): ").lower() == 'y'

            if reuse:
                # Copy credentials
                gmail_dir.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(calendar_creds, gmail_creds)
                print(f"Copied credentials to {gmail_creds}")

                if self._setup_google_oauth(gmail_dir, "google_gmail"):
                    print("Gmail setup completed!")
                    return True

        # New setup
        print("\nFor Gmail, you need the same OAuth2 setup as Google Calendar.")
        print("You can use the same credentials.json file.")
        print()

        if self._setup_google_oauth(gmail_dir, "google_gmail"):
            print("Gmail setup completed!")
            return True
        else:
            print("Gmail setup failed")
            return False

    def _setup_google_oauth(self, service_dir: Path, service_name: str) -> bool:
        """Setup Google OAuth for a service.

        Args:
            service_dir: Directory for service credentials
            service_name: Name of the service (google_calendar, google_gmail)

        Returns:
            True if setup was successful
        """
        service_dir.mkdir(parents=True, exist_ok=True)
        creds_file = service_dir / "credentials.json"

        # Validate credentials file
        if not creds_file.exists():
            print(f"Credentials file not found: {creds_file}")
            return False

        try:
            with open(creds_file, 'r') as f:
                creds_data = json.load(f)

            # Validate OAuth2 structure
            if 'installed' not in creds_data:
                print("Invalid credentials: Expected OAuth2 desktop application credentials")
                return False

            oauth_info = creds_data['installed']
            required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
            missing = [field for field in required_fields if field not in oauth_info]

            if missing:
                print(f"Invalid credentials: Missing fields: {missing}")
                return False

            print("Credentials file validated")

        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading credentials: {e}")
            return False

        # Store in credential manager
        credential_data = {
            "credentials_path": str(creds_file),
            "token_path": str(service_dir / "token.json"),
            "application_name": "mAIgic Assistant",
            "user_timezone": "UTC",
            "read_only": False
        }

        self.credential_manager.store_credentials(
            self.profile, service_name, credential_data
        )
        success = True

        if success:
            print(f"Credentials saved for {service_name}")
            return True
        else:
            print(f"Failed to save credentials for {service_name}")
            return False

    def _test_google_calendar(self) -> bool:
        """Test Google Calendar connection."""
        try:
            self.registry.create_calendar_client("google_calendar", self.profile)
            print("Google Calendar connection successful")
            return True
        except Exception as e:
            print(f"Google Calendar test failed: {e}")
            return False

    def _test_gmail(self) -> bool:
        """Test Gmail connection."""
        try:
            self.registry.create_email_client("google_gmail", self.profile)
            print("Gmail connection successful")
            return True
        except Exception as e:
            print(f"Gmail test failed: {e}")
            return False

    def test_integrations(self) -> None:
        """Test all configured integrations."""
        print("\nTesting Integrations")
        print("=" * 40)

        integrations = self.discover_integrations()
        configured = {k: v for k, v in integrations.items() if v["has_credentials"]}

        if not configured:
            print("No integrations configured to test")
            return

        for service in configured:
            print(f"\nTesting {service}...")

            if service == "google_calendar":
                self._test_google_calendar()
            elif service == "google_gmail":
                self._test_gmail()
            else:
                print(f"No test available for {service}")

    def interactive_setup(self) -> None:
        """Run interactive setup wizard."""
        print("\nmAIgic Integration Setup Wizard")
        print("=" * 50)

        # Show current status
        self.print_status()

        # Discover what's available
        integrations = self.discover_integrations()
        available_unconfigured = [
            k for k, v in integrations.items()
            if v.get("available", False) and not v["configured"]
        ]

        if not available_unconfigured:
            print("All available integrations are already configured!")
            print("\nRun with --test to test your integrations")
            return

        print("Available integrations to set up:")
        for i, service in enumerate(available_unconfigured, 1):
            info = integrations[service]
            req_creds = ", ".join(info.get("required_credentials", []))
            print(f"{i}. {service} (requires: {req_creds})")

        print("0. Set up simple credentials (API keys via .env)")
        print()

        try:
            choice = input("Select integration to set up (number), 'all', or 'quit': ").strip().lower()

            if choice == 'quit':
                return
            elif choice == 'all':
                self._setup_all_integrations(available_unconfigured)
            elif choice == '0':
                self.setup_simple_credentials()
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(available_unconfigured):
                    service = available_unconfigured[idx]
                    self._setup_service(service)
                else:
                    print("Invalid selection")
            else:
                print("Invalid input")

        except KeyboardInterrupt:
            print("\n\nSetup cancelled by user")
        except Exception as e:
            print(f"\nSetup error: {e}")

    def _setup_all_integrations(self, services: List[str]) -> None:
        """Set up all available integrations."""
        print(f"\nSetting up all integrations: {', '.join(services)}")

        # Pre-create directories for selected services
        self._create_service_directories(services)

        # Always start with simple credentials
        self.setup_simple_credentials()

        # Set up each service
        for service in services:
            print(f"\n{'='*20} {service.upper()} {'='*20}")
            self._setup_service(service)

    def _setup_service(self, service: str) -> None:
        """Set up a specific service."""
        # Pre-create directory for this service
        self._create_service_directories([service])

        if service == "google_calendar":
            self.setup_google_calendar()
        elif service == "google_gmail":
            self.setup_gmail()
        else:
            print(f"Setup not yet implemented for {service}")

    def _create_service_directories(self, services: List[str]) -> None:
        """Create directories for the specified services."""
        for service in services:
            if service in ["google_calendar", "google_gmail"]:
                service_dir = self.credentials_dir / service
                service_dir.mkdir(parents=True, exist_ok=True)
                print(f"Created directory: {service_dir}")

                # Show where to place credentials
                creds_file = service_dir / "credentials.json"
                print(f"  → Place your credentials.json at: {creds_file}")
                print()


def main() -> None:
    """Main entry point for integration setup."""
    parser = argparse.ArgumentParser(
        description="mAIgic Integration Setup - Single entry point for all integrations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run maigic-integrations-setup                   # Interactive setup wizard
  uv run maigic-integrations-setup --list            # Show current status
  uv run maigic-integrations-setup --service calendar  # Setup calendar only
  uv run maigic-integrations-setup --test            # Test all integrations
  uv run maigic-integrations-setup --profile work    # Use 'work' profile

Alternative usage:
  uv run -m mAIgic_integrations.setup                # Using module flag
        """
    )

    parser.add_argument(
        "--profile",
        default="default",
        help="User profile name (default: 'default')"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Show current integration status"
    )
    parser.add_argument(
        "--service",
        choices=["calendar", "gmail", "google_calendar", "google_gmail"],
        help="Set up specific service only"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test all configured integrations"
    )
    parser.add_argument(
        "--simple",
        action="store_true",
        help="Set up simple credentials only (API keys)"
    )

    args = parser.parse_args()

    # Create setup instance
    setup = IntegrationSetup(profile=args.profile)

    try:
        if args.list:
            setup.print_status()
        elif args.test:
            setup.test_integrations()
        elif args.simple:
            setup.setup_simple_credentials()
        elif args.service:
            # Map service names
            service_map = {
                "calendar": "google_calendar",
                "gmail": "google_gmail",
                "google_calendar": "google_calendar",
                "google_gmail": "google_gmail"
            }
            service_name = service_map.get(args.service, args.service)
            setup._setup_service(service_name)
        else:
            # Interactive wizard
            setup.interactive_setup()

    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nSetup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()  # pragma: no cover
