# Gmail Examples

Professional Gmail integration examples using the registry pattern.

## Quick Setup

### 1. **Run Setup Command**
```bash
uv run maigic-integrations-setup --service gmail
```

This will:
- Guide you through Google Cloud Console setup
- Create OAuth2 credentials (reuses Calendar credentials if available)
- Save credential metadata for the registry system
- Test the connection

### 2. **Run Examples**
```bash
uv run python src/mAIgic_integrations/email/email_gmail_impl/examples/basic_gmail_operations.py
```

## Examples

### `basic_gmail_operations.py`
Demonstrates the **registry pattern** for Gmail:
- **Automatic credential management** via metadata files
- **Retrieving recent emails**
- **Searching emails with queries**
- **Account statistics**

**Key Benefits:**
- No manual credential paths
- Supports multiple users/profiles
- Professional architecture

## Google Cloud Console Setup

When you run the setup command, you'll need:

### 1. **Create Google Cloud Project** (if not done for Calendar)
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create new project or select existing one
- Note the project ID

### 2. **Enable Gmail API**
- Navigate to "APIs & Services" → "Library"
- Search for "Gmail API"
- Click "Enable"

### 3. **Create OAuth2 Credentials** (if not done for Calendar)
- Go to "APIs & Services" → "Credentials"
- Click "Create Credentials" → "OAuth 2.0 Client IDs"
- Choose "Desktop Application"
- Name: "mAIgic Gmail Integration"
- Download the `credentials.json` file

**Note**: If you already set up Calendar, Gmail will offer to reuse those credentials.

### 4. **Complete Setup**
- The setup command will prompt for the `credentials.json` file location
- It will handle OAuth flow and create metadata files
- Test connection automatically

## How It Works

### Registry Pattern
```python
from mAIgic_integrations import create_email_client

# This automatically uses your configured credentials
client = create_email_client("google_gmail")
```

### Credential Storage
```
credentials/
├── c21f969b_google_gmail.json       # Metadata (registry uses this)
└── google_gmail/
    ├── credentials.json             # OAuth2 app credentials
    └── token.json                   # User access token
```

The **metadata file** contains:
- Paths to actual OAuth files
- Configuration settings (timezone, read-only mode)
- User profile mapping

## Gmail API Scopes

The setup automatically configures these scopes:
- `https://www.googleapis.com/auth/gmail.readonly` - Read emails
- `https://www.googleapis.com/auth/gmail.modify` - Modify emails
- `https://www.googleapis.com/auth/gmail.labels` - Manage labels

## Multiple Users/Profiles

```bash
# Setup for different profiles
uv run maigic-integrations-setup --profile work --service gmail
uv run maigic-integrations-setup --profile personal --service gmail

# Use specific profile in code
client = create_email_client("google_gmail", user_id="work")
```

## Troubleshooting

### Check Setup Status
```bash
uv run maigic-integrations-setup --list
```

Should show:
```
[READY]              google_gmail
```

### Test Connection
```bash
uv run maigic-integrations-setup --test
```

### Common Issues

**"No credentials found"**
- Re-run: `uv run maigic-integrations-setup --service gmail`
- Ensure metadata files exist in `credentials/`

**OAuth errors**
- Check Google Cloud Console credentials
- Ensure Gmail API is enabled
- Verify OAuth2 scopes

**Permission errors**
- Emails are read-only by default for security
- Check the `read_only` setting in metadata
- Ensure proper Gmail API scopes

**Rate limiting**
- Gmail API has rate limits per user and per project
- The client handles basic rate limiting automatically
- For high-volume operations, implement additional delays

## Security Considerations

- **Read-Only Mode**: Examples run in read-only mode by default
- **Scope Minimization**: Only request necessary permissions
- **Credential Security**: Never commit OAuth files to version control
- **Token Refresh**: The client handles token refresh automatically

## Next Steps

- **Integration Patterns**: Check `../../examples/` for multi-service usage
- **API Reference**: Explore `../email_api/` for full interface
- **Implementation**: Review `../clients.py` for advanced configuration 