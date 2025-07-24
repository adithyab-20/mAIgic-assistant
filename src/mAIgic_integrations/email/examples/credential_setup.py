#!/usr/bin/env python3
"""
Gmail API Credential Setup and Validation Tool

Interactive utility for setting up and validating Gmail API credentials
for the mAIgic Assistant email integration package.

Features:
- Validates existing credentials.json format
- Provides step-by-step setup instructions
- Checks OAuth token status
- Troubleshoots common configuration issues

This tool ensures proper Gmail API access before running other examples.
"""

import json
import os


def validate_credentials_file():
    """Validate credentials.json file format and content."""

    credentials_path = "credentials.json"

    if not os.path.exists(credentials_path):
        return False, f"Credentials file not found: {credentials_path}"

    try:
        with open(credentials_path, 'r') as file:
            credentials = json.load(file)

        # Check for valid OAuth2 credentials structure
        if 'installed' in credentials:
            client_info = credentials['installed']
            required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']

            missing_fields = [field for field in required_fields if field not in client_info]
            if missing_fields:
                return False, f"Missing required OAuth2 fields: {missing_fields}"

            return True, "Valid OAuth2 desktop application credentials found"

        elif 'web' in credentials:
            return False, "Web application credentials detected. Desktop application credentials required."

        else:
            return False, "Invalid credentials file format. Expected OAuth2 structure not found."

    except json.JSONDecodeError as e:
        return False, f"Invalid JSON format: {str(e)}"
    except Exception as e:
        return False, f"Error reading credentials file: {str(e)}"


def display_setup_instructions():
    """Display comprehensive Gmail API setup instructions."""

    print("Gmail API Setup Instructions")
    print("=" * 50)
    print()

    print("Step 1: Google Cloud Console Setup")
    print("  Navigate to: https://console.cloud.google.com/")
    print("  - Create a new project or select an existing one")
    print("  - Note your project name for reference")
    print()

    print("Step 2: Enable Gmail API")
    print("  - Go to 'APIs & Services' > 'Library'")
    print("  - Search for 'Gmail API'")
    print("  - Click 'Enable' button")
    print("  - Wait for API to be enabled")
    print()

    print("Step 3: Create OAuth2 Credentials")
    print("  - Go to 'APIs & Services' > 'Credentials'")
    print("  - Click '+ CREATE CREDENTIALS' > 'OAuth client ID'")
    print("  - Select 'Desktop application' as application type")
    print("  - Enter name: 'mAIgic Assistant Gmail Client'")
    print("  - Click 'Create' button")
    print()

    print("Step 4: Download Credentials")
    print("  - Click download button next to your new credential")
    print("  - Save file as 'credentials.json' in project root directory")
    print("  - Ensure file is named exactly 'credentials.json'")
    print()

    print("Step 5: OAuth Consent Screen (if required)")
    print("  - Go to 'APIs & Services' > 'OAuth consent screen'")
    print("  - Select 'External' user type for testing")
    print("  - Fill required fields:")
    print("    * App name: 'mAIgic Assistant'")
    print("    * User support email: your email address")
    print("    * Developer contact: your email address")
    print("  - Add your email to 'Test users' section")
    print()

    print("Step 6: Verify Setup")
    print("  - Run: python examples/basic_operations.py")
    print("  - Browser will open for OAuth authentication")
    print("  - Grant Gmail access permissions")
    print("  - Verify successful connection")
    print()


def validate_complete_setup():
    """Validate the complete Gmail API setup configuration."""

    print("Gmail API Setup Validation")
    print("=" * 40)
    print()

    # Check credentials file
    is_valid, message = validate_credentials_file()

    if is_valid:
        print("Credentials File: VALID")
        print(f"  Details: {message}")

        # Check for existing authentication token
        token_path = "token.json"
        if os.path.exists(token_path):
            print("Authentication Token: FOUND")
            print(f"  Location: {token_path}")
            print("  Status: OAuth flow previously completed")
        else:
            print("Authentication Token: NOT FOUND")
            print("  Status: OAuth flow required on first use")

        print()
        print("Setup Status: READY")
        print("You can now run the Gmail examples:")
        print("  - python examples/basic_operations.py")
        print("  - python examples/advanced_operations.py")

    else:
        print("Credentials File: INVALID")
        print(f"  Error: {message}")
        print()
        print("Setup Status: INCOMPLETE")
        print("Please complete the setup instructions below.")
        print()
        display_setup_instructions()


def check_file_permissions():
    """Check file system permissions for credential files."""

    print("File System Permissions Check")
    print("=" * 40)

    current_dir = os.getcwd()
    print(f"Working directory: {current_dir}")

    # Check directory write permissions
    if os.access(current_dir, os.W_OK):
        print("Directory permissions: WRITABLE")
    else:
        print("Directory permissions: READ-ONLY")
        print("Warning: Cannot create token.json in current directory")

    # Check credentials file permissions
    credentials_path = "credentials.json"
    if os.path.exists(credentials_path):
        if os.access(credentials_path, os.R_OK):
            print("Credentials file: READABLE")
        else:
            print("Credentials file: ACCESS DENIED")
    else:
        print("Credentials file: NOT FOUND")

    print()


def interactive_troubleshooting():
    """Interactive troubleshooting for common setup issues."""

    print("Interactive Troubleshooting")
    print("=" * 40)
    print()

    issues = [
        {
            "problem": "Credentials file not found",
            "solution": "Download credentials.json from Google Cloud Console and place in project root"
        },
        {
            "problem": "Invalid credentials format",
            "solution": "Ensure you downloaded Desktop application credentials, not Web application"
        },
        {
            "problem": "Authentication failed during OAuth",
            "solution": "Check OAuth consent screen configuration and add your email to test users"
        },
        {
            "problem": "Gmail API not enabled error",
            "solution": "Enable Gmail API in Google Cloud Console APIs & Services > Library"
        },
        {
            "problem": "Permission denied errors",
            "solution": "Verify OAuth consent screen is properly configured with required scopes"
        }
    ]

    print("Common Issues and Solutions:")
    for i, issue in enumerate(issues, 1):
        print(f"{i}. Problem: {issue['problem']}")
        print(f"   Solution: {issue['solution']}")
        print()


def main():
    """Main credential setup utility with interactive menu."""

    print("Gmail API Credential Setup Utility")
    print("=" * 45)
    print()
    print("This utility helps configure Gmail API access for mAIgic Assistant")
    print()

    menu_options = [
        "Validate current setup",
        "Show setup instructions",
        "Check file permissions",
        "Interactive troubleshooting",
        "Exit"
    ]

    while True:
        print("Available Options:")
        for i, option in enumerate(menu_options, 1):
            print(f"{i}. {option}")

        try:
            choice = input(f"\nSelect option (1-{len(menu_options)}): ").strip()
            print()

            if choice == "1":
                validate_complete_setup()
            elif choice == "2":
                display_setup_instructions()
            elif choice == "3":
                check_file_permissions()
            elif choice == "4":
                interactive_troubleshooting()
            elif choice == "5":
                print("Setup utility exiting...")
                break
            else:
                print(f"Invalid selection. Please choose 1-{len(menu_options)}.")

            print()
            input("Press Enter to continue...")
            print()

        except KeyboardInterrupt:
            print("\nSetup utility interrupted. Exiting...")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            print("Please try again or check your input.")


if __name__ == "__main__":
    main()
