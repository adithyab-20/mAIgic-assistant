# Email Integration Package

A unified email interface for the mAIgic Assistant with clean architecture supporting multiple email providers.

## Overview

This package provides a comprehensive email integration system with:

- **Abstract Interfaces**: Clean `EmailClient` and `EmailProvider` interfaces
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

## Quick Start

### Gmail Setup

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing
   - Enable Gmail API

2. **Configure OAuth2**
   - Go to APIs & Services > Credentials
   - Create OAuth client ID (Desktop application)
   - Download `credentials.json`

3. **Install and Use**
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

## Core Components

### EmailClient Interface

The main interface providing:
- `get_emails()` - Retrieve emails with filtering
- `search_emails()` - Search with query strings
- `get_email()` - Get specific email by ID
- `get_account_info()` - Account statistics
- `download_attachment()` - Attachment handling

### Data Types

- **Email**: Complete email representation
- **EmailAddress**: Email address with optional display name
- **EmailStats**: Account statistics and metrics
- **Attachment**: File attachment handling

### Exception Hierarchy

Comprehensive error handling:
- `EmailConnectionError` - Connection failures
- `EmailAuthenticationError` - Authentication issues
- `EmailNotFoundError` - Missing emails/attachments
- `EmailSearchError` - Search operation failures

## Examples

See the `examples/` directory for:
- **basic_operations.py** - Fundamental Gmail operations
- **advanced_operations.py** - Comprehensive AI integration
- **credential_setup.py** - Credential setup and validation tool

## Testing

```bash
# Run all email tests
uv run pytest src/mAIgic_integrations/email/ -v

# Run Gmail implementation tests only
uv run pytest src/mAIgic_integrations/email/email_gmail_impl/tests/ -v
```

## Future Providers

The architecture supports additional email providers:
- Outlook/Exchange
- Yahoo Mail
- IMAP/SMTP servers

Each provider implements the same `EmailClient` interface for consistent usage patterns. 