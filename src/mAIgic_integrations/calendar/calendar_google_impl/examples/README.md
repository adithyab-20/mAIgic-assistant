# Google Calendar Examples

Professional Google Calendar integration examples using the registry pattern.

## Quick Setup

### 1. **Run Setup Command**
```bash
uv run maigic-integrations-setup --service calendar
```

This will:
- Guide you through Google Cloud Console setup
- Create OAuth2 credentials
- Save credential metadata for the registry system
- Test the connection

### 2. **Run Examples**
```bash
uv run python src/mAIgic_integrations/calendar/calendar_google_impl/examples/basic_calendar_operations.py
```

## Examples

### `basic_calendar_operations.py`
Demonstrates the **registry pattern** for Google Calendar:
- **Automatic credential management** via metadata files
- **Retrieving upcoming events**
- **Creating calendar events**
- **Finding available time slots**
- **Event cleanup**

**Key Benefits:**
- No manual credential paths
- Supports multiple users/profiles
- Professional architecture

## Google Cloud Console Setup

When you run the setup command, you'll need:

### 1. **Create Google Cloud Project**
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create new project or select existing one
- Note the project ID

### 2. **Enable Google Calendar API**
- Navigate to "APIs & Services" → "Library"
- Search for "Google Calendar API"
- Click "Enable"

### 3. **Create OAuth2 Credentials**
- Go to "APIs & Services" → "Credentials"
- Click "Create Credentials" → "OAuth 2.0 Client IDs"
- Choose "Desktop Application"
- Name: "mAIgic Calendar Integration"
- Download the `credentials.json` file

### 4. **Complete Setup**
- The setup command will prompt for the `credentials.json` file location
- It will handle OAuth flow and create metadata files
- Test connection automatically

## How It Works

### Registry Pattern
```python
from mAIgic_integrations import create_calendar_client

# This automatically uses your configured credentials
client = create_calendar_client("google_calendar")
```

### Credential Storage
```
credentials/
├── c21f969b_google_calendar.json    # Metadata (registry uses this)
└── google_calendar/
    ├── credentials.json             # OAuth2 app credentials
    └── token.json                   # User access token
```

The **metadata file** contains:
- Paths to actual OAuth files
- Configuration settings (timezone, read-only mode)
- User profile mapping

## Multiple Users/Profiles

```bash
# Setup for different profiles
uv run maigic-integrations-setup --profile work --service calendar
uv run maigic-integrations-setup --profile personal --service calendar

# Use specific profile in code
client = create_calendar_client("google_calendar", user_id="work")
```

## Troubleshooting

### Check Setup Status
```bash
uv run maigic-integrations-setup --list
```

Should show:
```
[READY]              google_calendar
```

### Test Connection
```bash
uv run maigic-integrations-setup --test
```

### Common Issues

**"No credentials found"**
- Re-run: `uv run maigic-integrations-setup --service calendar`
- Ensure metadata files exist in `credentials/`

**OAuth errors**
- Check Google Cloud Console credentials
- Ensure Calendar API is enabled
- Verify OAuth2 scopes

**Permission errors**
- Events can only be modified by their organizer
- Use `create_my_event()` for events you organize
- Use `respond_to_invitation()` for events you're invited to

## Next Steps

- **Integration Patterns**: Check `../../examples/` for multi-service usage
- **API Reference**: Explore `../calendar_api/` for full interface
- **Implementation**: Review `../clients.py` for advanced configuration 