"""
Entry point for running mAIgic_integrations as a module.

This provides helpful guidance when users run `uv run -m mAIgic_integrations`.
"""

import sys


def main() -> None:  # pragma: no cover
    """Main entry point for module execution."""
    print("mAIgic Integrations Setup")
    print("=" * 30)
    print()
    print("Available commands:")
    print("  uv run maigic-integrations-setup           # Interactive setup wizard")
    print("  uv run maigic-integrations-setup --list    # Show integration status")
    print("  uv run maigic-integrations-setup --test    # Test integrations")
    print()
    print("Alternative (module) commands:")
    print("  uv run -m mAIgic_integrations.setup        # Same as maigic-integrations-setup")
    print("  uv run -m mAIgic_integrations.setup --list # Show status")
    print()
    print("For Google Calendar/Gmail setup:")
    print("  1. Get credentials from: https://console.cloud.google.com/")
    print("  2. Download credentials.json to credentials/google_calendar/ or credentials/google_gmail/")
    print("  3. Run: uv run maigic-integrations-setup")
    print()
    print("For help with specific services:")
    print("  uv run maigic-integrations-setup --service calendar")
    print("  uv run maigic-integrations-setup --service gmail")
    print()

    # Exit with code 0 to indicate successful help display
    sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
