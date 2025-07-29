# mAIgic Integrations

Unified integration system for external services with automatic credential management and service discovery.

## Overview

The mAIgic Integrations package provides a centralized system for managing external service connections:

- **Registry Pattern**: Automatic service discovery and client creation
- **Credential Management**: Secure OAuth and API key storage
- **Profile Support**: Multiple user and environment configurations
- **Type Safety**: Comprehensive type hints and error handling

## Architecture

```
mAIgic_integrations/
├── config.py              # Environment configuration
├── credentials.py          # Credential storage management
├── registry.py             # Service discovery and client factory
├── setup.py               # Interactive setup wizard
├── email/                 # Email integration components
│   ├── email_api/         # Abstract interfaces
│   └── email_gmail_impl/  # Gmail implementation
└── calendar/              # Calendar integration components
    ├── calendar_api/      # Abstract interfaces
    └── calendar_google_impl/ # Google Calendar implementation
```

## Installation

```bash
# Install with specific integrations
uv sync --extra email --extra calendar

# Install all integrations
uv sync --extra email --extra calendar
```

## Quick Start

### Environment Setup

Create a `.env` file:

```bash
# Enable integrations
GOOGLE_CALENDAR_ENABLED=true
GOOGLE_GMAIL_ENABLED=true

# Optional configuration
MAIGIC_CREDENTIALS_DIR=credentials
MAIGIC_ENVIRONMENT=development
```

### Interactive Setup

```bash
# Setup all integrations
uv run maigic-integrations-setup

# Setup specific service
uv run maigic-integrations-setup --service calendar
uv run maigic-integrations-setup --service gmail

# Check status
uv run maigic-integrations-setup --list
```

### Using Registry Pattern

```python
from mAIgic_integrations import create_calendar_client, create_email_client

# Automatic credential discovery
calendar = create_calendar_client("google_calendar")
email = create_email_client("google_gmail")

async with calendar:
    events = await calendar.get_events(time_range)
    
async with email:
    messages = await email.get_recent_emails(count=10)
```

## Core Components

### IntegrationRegistry

Central service discovery and client factory:

```python
from mAIgic_integrations import get_registry, get_available_integrations

# Get available services
services = get_available_integrations()
print(f"Available: {list(services.keys())}")

# Get registry instance
registry = get_registry()
client = registry.get_calendar_client("google_calendar")
```

### CredentialManager

Secure credential storage with automatic OAuth token management:

```python
from mAIgic_integrations import create_credential_manager

manager = create_credential_manager()

# Store credentials
await manager.store_credentials("google_calendar", {
    "credentials_path": "path/to/credentials.json",
    "token_path": "path/to/token.json"
})

# Retrieve credentials
creds = await manager.get_credentials("google_calendar", "default")
```

### IntegrationConfig

Environment-driven configuration:

```python
from mAIgic_integrations.config import IntegrationConfig

config = IntegrationConfig.from_env()
print(f"Calendar enabled: {config.google_calendar_enabled}")
print(f"Gmail enabled: {config.google_gmail_enabled}")
```

## Credential Management

### Directory Structure

The system maintains organized credential storage:

```
credentials/
├── c21f969b_google_calendar.json    # Registry metadata (default profile)
├── c21f969b_google_gmail.json       # Registry metadata (default profile)
├── google_calendar/
│   ├── credentials.json             # OAuth2 app credentials
│   └── token.json                   # User access tokens
└── google_gmail/
    ├── credentials.json             # OAuth2 app credentials
    └── token.json                   # User access tokens
```

### Metadata Files

Registry metadata files contain:
- Paths to OAuth credential files
- User profile mapping
- Service configuration (timezone, read-only mode)
- Authentication settings

### Profile Support

Multiple user profiles are supported:

```bash
# Setup work profile
uv run maigic-integrations-setup --profile work --service calendar

# Setup personal profile
uv run maigic-integrations-setup --profile personal --service calendar
```

```python
# Use specific profile
work_calendar = create_calendar_client("google_calendar", user_id="work")
personal_calendar = create_calendar_client("google_calendar", user_id="personal")
```

## Available Integrations

### Email Integration

Gmail integration with comprehensive operations:

```python
from mAIgic_integrations import create_email_client

client = create_email_client("google_gmail")
async with client:
    # Get recent emails
    emails = await client.get_recent_emails(days=7)
    
    # Search emails
    results = await client.search_emails("important project")
    
    # Get account statistics
    stats = await client.get_account_info()
```

### Calendar Integration

Google Calendar with role-based permissions:

```python
from mAIgic_integrations import create_calendar_client

client = create_calendar_client("google_calendar")
async with client:
    # Get today's events
    events = await client.get_events(time_range)
    
    # Create new event (as organizer)
    result = await client.create_my_event(event)
    
    # Respond to invitation (as attendee)
    await client.respond_to_invitation(event_id, response)
```

## Setup Wizard Features

The interactive setup wizard provides:

### Automatic Discovery

- Detects available integration providers
- Shows current configuration status
- Identifies missing credentials

### Guided Configuration

- Creates necessary directories
- Walks through OAuth2 setup
- Tests connections after configuration
- Provides clear error messages

### Batch Operations

- Setup multiple services at once
- Reuse credentials across compatible services
- Profile-specific configurations

## Testing

### Check Integration Status

```bash
# List all integrations and their status
uv run maigic-integrations-setup --list

# Test all configured integrations
uv run maigic-integrations-setup --test
```

### Development Testing

```bash
# Run integration tests
uv run pytest src/mAIgic_integrations/ -v

# Test specific components
uv run pytest src/mAIgic_integrations/email/ -v
uv run pytest src/mAIgic_integrations/calendar/ -v
```

## Error Handling

Comprehensive exception hierarchy for all operations:

### Connection Errors
- Network connectivity issues
- Service availability problems
- Rate limiting and quota exceeded

### Authentication Errors
- OAuth token expiry or revocation
- Invalid credentials
- Permission scope issues

### Configuration Errors
- Missing environment variables
- Invalid credential files
- Profile not found

## Development

### Adding New Integrations

1. **Create Provider Class**
   ```python
   class NewServiceProvider(IntegrationProvider):
       def get_name(self) -> str:
           return "new_service"
       
       def is_available(self) -> bool:
           # Check if dependencies are installed
           return True
       
       def create_client(self, **kwargs) -> NewServiceClient:
           # Create and return client instance
           pass
   ```

2. **Register Provider**
   ```python
   # In registry.py
   registry.register_provider(NewServiceProvider())
   ```

3. **Add Setup Logic**
   ```python
   # In setup.py
   def setup_new_service(self) -> bool:
       # Implementation setup logic
       pass
   ```

### Type Checking

```bash
uv run mypy src/mAIgic_integrations/
```

### Code Quality

```bash
uv run ruff check src/mAIgic_integrations/
uv run ruff format src/mAIgic_integrations/
```

## Security

- **Credential Isolation**: Each service has separate credential storage
- **Profile Separation**: Different users have isolated credential stores
- **Token Management**: Automatic OAuth token refresh and expiry handling
- **Scope Minimization**: Only request necessary permissions
- **Secure Storage**: Credentials never committed to version control 