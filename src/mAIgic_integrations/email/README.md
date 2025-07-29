# Email Integration

Gmail integration with comprehensive email operations and OAuth2 authentication for the mAIgic Assistant.

## Overview

This package provides:
- **Abstract Email Interfaces**: Clean `EmailClient` and `EmailProvider` interfaces
- **Gmail Implementation**: Full-featured Gmail client with OAuth2 authentication
- **Async Support**: Complete async/await patterns throughout
- **Type Safety**: Comprehensive type hints and data models
- **Error Handling**: Robust exception hierarchy for all failure modes

## Architecture

```
email/
├── email_api/           # Abstract interfaces and types
├── email_gmail_impl/    # Gmail implementation
└── examples/            # Usage examples
```

## Installation

```bash
# Install with email capabilities
uv sync --extra email
```

## Setup

### Google Cloud Console

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing
   - Enable Gmail API

2. **Configure OAuth2**
   - Go to APIs & Services > Credentials
   - Create OAuth client ID (Desktop application)
   - Download `credentials.json`

### Using Setup Wizard

```bash
# Interactive setup
uv run maigic-integrations-setup --service gmail

# Check status
uv run maigic-integrations-setup --list
```

## Usage

### Direct Client Usage

```python
from mAIgic_integrations.email import GmailClient, GmailConfig

config = GmailConfig(
    credentials_path="credentials.json",
    token_path="token.json"
)

async with GmailClient(config) as client:
    # Get recent emails
    emails = await client.get_recent_emails(days=7)
    
    # Search emails
    results = await client.search_emails("project status")
    
    # Get account info
    stats = await client.get_account_info()
```

### Registry Pattern

```python
from mAIgic_integrations import create_email_client

# Automatic credential discovery
client = create_email_client("google_gmail")
async with client:
    emails = await client.get_recent_emails(count=10)
    for email in emails:
        print(f"{email.subject} from {email.sender}")
```

## Core Components

### EmailClient Interface

Main interface providing:
- `get_emails()` - Retrieve emails with filtering
- `search_emails()` - Search with query strings
- `get_email()` - Get specific email by ID
- `get_account_info()` - Account statistics
- `download_attachment()` - Attachment handling

### Data Types

- **Email**: Complete email representation with headers, body, attachments
- **EmailAddress**: Email address with optional display name
- **EmailStats**: Account statistics and metrics
- **Attachment**: File attachment handling with download support

### Exception Hierarchy

Comprehensive error handling:
- `EmailConnectionError` - Connection failures
- `EmailAuthenticationError` - Authentication issues
- `EmailNotFoundError` - Missing emails/attachments
- `EmailSearchError` - Search operation failures

## Examples

Run the provided examples:

```bash
uv run python src/mAIgic_integrations/email/email_gmail_impl/examples/basic_gmail_operations.py
```

## Testing

```bash
# Run all email tests
uv run pytest src/mAIgic_integrations/email/ -v

# Run Gmail implementation tests only
uv run pytest src/mAIgic_integrations/email/email_gmail_impl/tests/ -v
```

## Development

### Type Checking

```bash
uv run mypy src/mAIgic_integrations/email/
```

### Code Quality

```bash
uv run ruff check src/mAIgic_integrations/email/
uv run ruff format src/mAIgic_integrations/email/
``` 