#!/usr/bin/env python3
"""
Basic Gmail Operations

Demonstrates core Gmail operations using the registry pattern:
- Client setup via registry (uses credential metadata)
- Retrieving recent emails
- Searching emails with queries
- Accessing account statistics

Prerequisites:
- Run: uv run maigic-integrations-setup --service gmail
- Ensure credentials are properly configured

Usage:
    uv run python src/mAIgic_integrations/email/email_gmail_impl/examples/basic_gmail_operations.py
"""

import asyncio
import logging

# Use the high-level registry pattern
from mAIgic_integrations import create_email_client
from mAIgic_integrations.email import (
    EmailAPIError,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_client():
    """Initialize Gmail client via registry."""
    try:
        # This uses the credential metadata files created by setup
        client = create_email_client("google_gmail")
        return client
    except Exception as e:
        raise RuntimeError(
            f"Failed to create email client: {e}\n"
            "Run: uv run maigic-integrations-setup --service gmail"
        )


async def get_recent_emails(client, days: int = 7):
    """Retrieve recent emails."""
    print(f"Retrieving emails from the last {days} days...")

    try:
        emails = await client.get_recent_emails(days=days)
        print(f"Found {len(emails)} emails")

        if emails:
            print("\nRecent emails:")
            for i, email in enumerate(emails[:5], 1):
                print(f"  {i}. {email.subject}")
                print(f"     From: {email.sender}")
                print(f"     Date: {email.date_received or email.date_sent}")
                if email.has_attachments:
                    print("     Attachments: Yes")
        else:
            print("No emails found in the specified time range")

        return emails
    except EmailAPIError as e:
        print(f"Error retrieving emails: {e}")
        return []


async def search_emails(client, query: str = "important"):
    """Search emails with a query."""
    print(f"\nSearching for emails with query: '{query}'...")

    try:
        emails = await client.search_emails(query, limit=10)
        print(f"Found {len(emails)} matching emails")

        if emails:
            print("\nSearch results:")
            for i, email in enumerate(emails[:3], 1):
                print(f"  {i}. {email.subject}")
                print(f"     From: {email.sender}")
                print(f"     Date: {email.date_received or email.date_sent}")

        return emails
    except EmailAPIError as e:
        print(f"Error searching emails: {e}")
        return []


async def get_account_stats(client):
    """Get basic account statistics."""
    print("\nRetrieving account statistics...")

    try:
        # Get counts from different searches
        total_emails = await client.search_emails("*", limit=1000)
        unread_emails = await client.search_emails("is:unread", limit=100)

        print("Account Statistics:")
        print(f"  Total emails (sample): {len(total_emails)}")
        print(f"  Unread emails: {len(unread_emails)}")

        # Get recent activity
        recent_emails = await client.get_recent_emails(days=1)
        print(f"  Emails in last 24 hours: {len(recent_emails)}")

    except EmailAPIError as e:
        print(f"Error retrieving statistics: {e}")


async def main():
    """Run basic Gmail operations demo."""
    print("Gmail Basic Operations (Registry Pattern)")
    print("=" * 45)

    try:
        # Setup client using registry pattern
        client = await setup_client()

        async with client:
            print("Connected to Gmail successfully")

            # Get recent emails
            await get_recent_emails(client, days=7)

            # Search emails
            await search_emails(client, "meeting OR calendar")

            # Get account stats
            await get_account_stats(client)

        print("\nDemo completed successfully!")
        print("\nNote: This example uses the registry pattern which:")
        print("- Automatically handles credential management")
        print("- Supports multiple users and profiles")
        print("- Uses metadata files created by the setup system")

    except Exception as e:
        print(f"Demo failed: {e}")
        print("\nTroubleshooting:")
        print("1. Run: uv run maigic-integrations-setup --service gmail")
        print("2. Check setup status: uv run maigic-integrations-setup --list")
        print("3. Ensure Gmail API is enabled in Google Cloud Console")
        print("4. Verify Gmail API scopes are properly configured")


if __name__ == "__main__":
    asyncio.run(main())
