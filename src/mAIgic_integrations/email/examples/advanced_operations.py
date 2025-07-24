#!/usr/bin/env python3
"""
Advanced Gmail Operations Example

Comprehensive demonstration of Gmail client capabilities for AI assistant integration,
including account analysis, content processing, and error handling patterns.

Features Demonstrated:
- Account information gathering
- Recent email analysis with content inspection
- Advanced search operations
- Email content analysis for AI processing
- Attachment handling
- Folder-based email retrieval
- Comprehensive error handling

Setup Requirements:
1. Create Google Cloud Project with Gmail API enabled
2. Generate OAuth2 credentials (Desktop application type)
3. Download credentials.json to project root
4. Run script - browser will open for OAuth flow on first use
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.mAIgic_integrations.email.email_api.exceptions import (  # noqa: E402
    EmailAuthenticationError,
    EmailConfigurationError,
    EmailConnectionError,
)
from src.mAIgic_integrations.email.email_gmail_impl import (  # noqa: E402
    GmailClient,
    GmailConfig,
)


async def demonstrate_advanced_features():
    """Demonstrate comprehensive Gmail client features for AI assistant integration."""

    print("Advanced Gmail Operations Demo")
    print("=" * 50)

    # Configuration paths
    credentials_path = "credentials.json"
    token_path = "token.json"

    # Validate credentials file exists
    if not os.path.exists(credentials_path):
        print(f"Error: Credentials file not found at {credentials_path}")
        print_setup_instructions()
        return

    try:
        # Initialize Gmail configuration
        config = GmailConfig(
            credentials_path=credentials_path,
            token_path=token_path
        )

        print(f"Using credentials: {credentials_path}")
        print(f"Token storage: {token_path}")

        # Create and connect Gmail client
        client = GmailClient(config)

        async with client:
            print("Connected to Gmail API successfully")

            # Account information analysis
            await analyze_account_information(client)

            # Recent email analysis
            await analyze_recent_emails(client)

            # Search operations
            await demonstrate_search_operations(client)

            # Content analysis
            await analyze_email_content(client)

            # Folder-based retrieval
            await demonstrate_folder_operations(client)

            print("\nAdvanced Gmail Operations Demo Complete")
            print_capabilities_summary()

    except EmailAuthenticationError as e:
        print(f"Authentication Error: {e}")
        print("Solution: Delete token.json and re-run to re-authenticate")

    except EmailConnectionError as e:
        print(f"Connection Error: {e}")
        print("Solution: Check internet connection and Gmail API quotas")

    except EmailConfigurationError as e:
        print(f"Configuration Error: {e}")
        print("Solution: Verify credentials.json file format")

    except Exception as e:
        print(f"Unexpected Error: {e}")
        print("Review error details and check configuration")


async def analyze_account_information(client):
    """Analyze Gmail account information for AI context."""

    print("\n1. Account Information Analysis")
    print("-" * 40)

    stats = await client.get_account_info()
    print(f"Total messages: {stats.total_messages:,}")
    print(f"Unread messages: {stats.unread_messages:,}")
    print(f"Total folders: {stats.total_folders}")
    if stats.last_sync:
        print(f"Last sync: {stats.last_sync.strftime('%Y-%m-%d %H:%M:%S')}")


async def analyze_recent_emails(client):
    """Analyze recent emails for AI context gathering."""

    print("\n2. Recent Email Analysis")
    print("-" * 40)

    recent_emails = await client.get_recent_emails(days=7)
    print(f"Retrieved {len(recent_emails)} emails from last 7 days")

    # Display sample emails with metadata
    for i, email in enumerate(recent_emails[:3], 1):
        print(f"\nEmail {i}:")
        print(f"  From: {email.sender.name or email.sender.address}")
        subject = email.subject[:60] + "..." if len(email.subject) > 60 else email.subject
        print(f"  Subject: {subject}")
        if email.date_received:
            print(f"  Date: {email.date_received.strftime('%Y-%m-%d %H:%M')}")
        if email.has_attachments:
            print(f"  Attachments: {len(email.attachments)} file(s)")
        print(f"  Labels: {', '.join(email.labels[:3])}{'...' if len(email.labels) > 3 else ''}")


async def demonstrate_search_operations(client):
    """Demonstrate advanced email search capabilities."""

    print("\n3. Advanced Search Operations")
    print("-" * 40)

    # AI-relevant search queries
    search_queries = [
        "important",
        "meeting",
        "project",
        "urgent",
        "deadline"
    ]

    for query in search_queries:
        try:
            results = await client.search_emails(query, limit=5)
            print(f"Query '{query}': {len(results)} results")

            if results:
                # Show most relevant result
                email = results[0]
                subject = email.subject[:50] + "..." if len(email.subject) > 50 else email.subject
                print(f"  Most relevant: {subject}")

        except Exception as e:
            print(f"Query '{query}': Error - {str(e)}")


async def analyze_email_content(client):
    """Analyze email content for AI processing insights."""

    print("\n4. Content Analysis for AI Processing")
    print("-" * 40)

    # Get recent email for analysis
    recent_emails = await client.get_recent_emails(days=1)
    if not recent_emails:
        print("No recent emails available for analysis")
        return

    email = recent_emails[0]
    print(f"Analyzing email: {email.subject}")
    print(f"From: {email.sender.name or email.sender.address}")
    print(f"Recipients: {len(email.recipients)} person(s)")
    print(f"CC recipients: {len(email.cc_recipients)} person(s)")

    # Content analysis
    if email.body_text:
        word_count = len(email.body_text.split())
        line_count = len(email.body_text.split('\n'))
        print(f"Text content: {word_count} words, {line_count} lines")

        # Preview for AI context (first 200 characters)
        preview = email.body_text.strip()[:200]
        print(f"Content preview: {preview}{'...' if len(email.body_text) > 200 else ''}")

    if email.body_html:
        print("HTML content: Available for rich text processing")

    # Attachment analysis
    if email.attachments:
        print(f"Attachments ({len(email.attachments)}):")
        for attachment in email.attachments:
            size_mb = attachment.size_bytes / (1024 * 1024)
            print(f"  - {attachment.filename}")
            print(f"    Size: {size_mb:.1f}MB")
            print(f"    Type: {attachment.attachment_type.value}")


async def demonstrate_folder_operations(client):
    """Demonstrate folder-specific email retrieval."""

    print("\n5. Folder-Based Email Retrieval")
    print("-" * 40)

    folders_to_analyze = ["INBOX", "SENT", "DRAFT"]

    for folder in folders_to_analyze:
        try:
            folder_emails = await client.get_emails(
                folder=folder,
                limit=5,
                include_body=False
            )
            print(f"{folder}: {len(folder_emails)} emails (headers only)")

            if folder_emails:
                latest = folder_emails[0]
                subject = latest.subject[:40] + "..." if len(latest.subject) > 40 else latest.subject
                print(f"  Latest: {subject}")

        except Exception as e:
            print(f"{folder}: Error - {str(e)}")


def print_setup_instructions():
    """Print detailed setup instructions."""

    print("\nSetup Instructions:")
    print("1. Go to Google Cloud Console (https://console.cloud.google.com/)")
    print("2. Create new project or select existing one")
    print("3. Enable Gmail API")
    print("4. Create OAuth2 credentials (Desktop application)")
    print("5. Download credentials.json file")
    print("6. Place credentials.json in project root")


def print_capabilities_summary():
    """Print summary of demonstrated AI assistant capabilities."""

    print("AI Assistant Capabilities Demonstrated:")
    print("- Account context gathering and statistics")
    print("- Recent email analysis with metadata extraction")
    print("- Advanced search with multiple query types")
    print("- Content analysis for text processing")
    print("- Attachment identification and processing")
    print("- Folder-based email organization")
    print("- Comprehensive error handling patterns")


async def quick_email_summary():
    """Quick email summary for rapid status checking."""

    print("Quick Email Summary")
    print("=" * 30)

    config = GmailConfig()
    client = GmailClient(config)

    try:
        async with client:
            # Get today's emails
            emails = await client.get_recent_emails(days=1)
            print(f"Today's emails: {len(emails)}")

            # Count unread emails
            unread_emails = [email for email in emails if 'UNREAD' in email.labels]
            print(f"Unread emails: {len(unread_emails)}")

            # Show latest email if available
            if emails:
                latest = emails[0]
                subject = latest.subject[:50] + "..." if len(latest.subject) > 50 else latest.subject
                print(f"Latest email: {subject}")
                print(f"From: {latest.sender.name or latest.sender.address}")

    except Exception as e:
        print(f"Error retrieving email summary: {e}")


def main():
    """Main function with operation selection menu."""

    print("Advanced Gmail Operations Examples")
    print("=" * 40)
    print("1. Full advanced operations demo")
    print("2. Quick email summary")
    print("3. Exit")

    while True:
        try:
            choice = input("\nSelect option (1-3): ").strip()

            if choice == "1":
                asyncio.run(demonstrate_advanced_features())
                break
            elif choice == "2":
                asyncio.run(quick_email_summary())
                break
            elif choice == "3":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please select 1, 2, or 3.")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            break


if __name__ == "__main__":
    main()
