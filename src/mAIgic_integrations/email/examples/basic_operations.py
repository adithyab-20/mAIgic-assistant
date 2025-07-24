#!/usr/bin/env python3
"""
Basic Gmail Operations Example

Demonstrates fundamental Gmail client operations including:
- Client configuration and connection
- Retrieving recent emails
- Searching emails with queries
- Accessing account statistics

Setup Requirements:
1. Download credentials.json from Google Cloud Console
2. Place in project root directory
3. Run this script for OAuth authentication on first use
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.mAIgic_integrations.email.email_gmail_impl import (  # noqa: E402
    GmailClient,
    GmailConfig,
)


async def demonstrate_basic_operations():
    """Demonstrate basic Gmail client operations."""

    # Create configuration using default credential paths
    config = GmailConfig()

    # Initialize client
    client = GmailClient(config)

    # Use client with async context manager for proper cleanup
    async with client:
        print("Connected to Gmail successfully")

        # Retrieve recent emails
        emails = await client.get_recent_emails(days=3)
        print(f"Retrieved {len(emails)} emails from the last 3 days")

        # Display first few emails
        print("\nRecent emails:")
        for i, email in enumerate(emails[:5], 1):
            print(f"{i}. Subject: {email.subject}")
            print(f"   From: {email.sender.address}")
            if email.date_received:
                print(f"   Date: {email.date_received.strftime('%Y-%m-%d %H:%M')}")
            print()

        # Search for specific emails
        search_results = await client.search_emails("important", limit=3)
        print(f"Found {len(search_results)} emails matching 'important'")

        # Display account statistics
        stats = await client.get_account_info()
        print("\nAccount Statistics:")
        print(f"Total messages: {stats.total_messages:,}")
        print(f"Unread messages: {stats.unread_messages:,}")
        print(f"Total folders: {stats.total_folders}")


if __name__ == "__main__":
    asyncio.run(demonstrate_basic_operations())
