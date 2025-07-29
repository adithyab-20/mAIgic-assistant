# mAIgic Assistant Setup Guide

Complete setup guide for mAIgic Assistant integrations and components.

## Overview

mAIgic Assistant provides:
- **Speech Processing**: OpenAI-powered speech-to-text and text-to-speech
- **Email Integration**: Gmail API with OAuth2 authentication
- **Calendar Integration**: Google Calendar with role-based permissions
- **Unified Credential Management**: Automatic service discovery and authentication

## Installation

```bash
git clone <repository-url>
cd mAIgic-assistant

# Base installation
uv sync

# With all components
uv sync --extra speech --extra email --extra calendar --extra dev
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Speech Processing
OPENAI_API_KEY=sk-your-openai-api-key

# Integration Control
GOOGLE_CALENDAR_ENABLED=true
GOOGLE_GMAIL_ENABLED=true

# Optional Configuration
MAIGIC_CREDENTIALS_DIR=credentials
MAIGIC_ENVIRONMENT=development
```

### Integration Setup

Use the unified setup wizard:

```bash
# Interactive setup for all services
uv run maigic-integrations-setup

# Setup specific services
uv run maigic-integrations-setup --service calendar
uv run maigic-integrations-setup --service gmail

# Check current status
uv run maigic-integrations-setup --list
```

## Google Cloud Console Setup

### Prerequisites

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project: "mAIgic Assistant"
   - Note the project ID

2. **Enable APIs**
   - Navigate to "APIs & Services" → "Library"
   - Enable "Google Calendar API"
   - Enable "Gmail API"

3. **Create OAuth2 Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Desktop Application"
   - Name: "mAIgic Integration"
   - Download `credentials.json`

### Service Configuration

The setup wizard will:
1. Create service directories automatically
2. Guide you through credential placement
3. Handle OAuth2 authorization flow
4. Test connections
5. Store configuration metadata

## Directory Structure

After setup, your credentials directory will contain:

```
credentials/
├── c21f969b_google_calendar.json    # Registry metadata
├── c21f969b_google_gmail.json       # Registry metadata
├── google_calendar/
│   ├── credentials.json             # OAuth2 app credentials
│   └── token.json                   # User access tokens
└── google_gmail/
    ├── credentials.json             # OAuth2 app credentials
    └── token.json                   # User access tokens
```

## Usage Examples

### Speech Processing

```python
from mAIgic_speech.speech_openai_impl import OpenAISpeechToTextClient, OpenAIConfig

config = OpenAIConfig(api_key="your-api-key")
client = OpenAISpeechToTextClient(config)

async with client:
    transcript = await client.transcribe("audio.wav")
    print(transcript)
```

### Email Operations

```python
from mAIgic_integrations import create_email_client

client = create_email_client("google_gmail")
async with client:
    emails = await client.get_recent_emails(count=10)
    for email in emails:
        print(f"{email.subject} from {email.sender}")
```

### Calendar Operations

```python
from mAIgic_integrations import create_calendar_client

client = create_calendar_client("google_calendar")
async with client:
    events = await client.get_events(time_range)
    for event in events:
        print(f"{event.title} at {event.time_slot}")
```

## Multiple Profiles

Support for multiple users or environments:

```bash
# Setup work profile
uv run maigic-integrations-setup --profile work --service calendar

# Setup personal profile  
uv run maigic-integrations-setup --profile personal --service calendar

# Use specific profile in code
work_calendar = create_calendar_client("google_calendar", user_id="work")
personal_calendar = create_calendar_client("google_calendar", user_id="personal")
```

## Testing

### Verify Setup

```bash
# Test all configured integrations
uv run maigic-integrations-setup --test

# Run component examples
uv run python src/mAIgic_speech/examples/batch_transcription.py --record
uv run python src/mAIgic_integrations/email/email_gmail_impl/examples/basic_gmail_operations.py
uv run python src/mAIgic_integrations/calendar/calendar_google_impl/examples/basic_calendar_operations.py
```

### Development Testing

```bash
# Run test suite
uv run pytest

# Test specific components
uv run pytest src/mAIgic_speech/
uv run pytest src/mAIgic_integrations/
```

## Troubleshooting

### Common Issues

**No integrations available**
- Ensure environment variables are set in `.env`
- Check that `GOOGLE_CALENDAR_ENABLED=true` and `GOOGLE_GMAIL_ENABLED=true`

**OAuth errors**
- Verify APIs are enabled in Google Cloud Console
- Ensure `credentials.json` is valid OAuth2 desktop application
- Check OAuth scopes and permissions

**Permission errors**
- Calendar: Only event organizers can modify events
- Gmail: Verify account permissions and API quotas

**Connection errors**
- Check network connectivity
- Verify API quotas in Google Cloud Console

### Reset Configuration

```bash
# Remove metadata files
rm credentials/c21f969b_*.json

# Remove OAuth tokens (keeps credentials.json)
rm credentials/*/token.json

# Re-run setup
uv run maigic-integrations-setup
```

## Development

### Code Quality

```bash
# Type checking
uv run mypy src/

# Linting and formatting
uv run ruff check src/
uv run ruff format src/

# Test coverage
uv run pytest --cov=src --cov-fail-under=80
```

### Architecture

The system uses a registry pattern for credential management:
- **Metadata files**: Store paths and configuration
- **Service directories**: Contain OAuth credentials and tokens
- **Automatic discovery**: Services are registered based on environment variables
- **Profile isolation**: Multiple users have separate credential stores

## Security

- OAuth files are never committed to version control
- Tokens are automatically refreshed
- Minimal permission scopes requested
- Secure credential storage with file-based backend 