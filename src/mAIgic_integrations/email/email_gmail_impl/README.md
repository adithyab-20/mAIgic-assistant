# Gmail Email Implementation

Gmail implementation of the EmailClient interface for the mAIgic Assistant, providing comprehensive access to Gmail via the Gmail API with OAuth2 authentication.

## Features

- **Full OAuth2 Integration**: Complete authentication flow with token refresh
- **Comprehensive Email Operations**: Read, search, and manage Gmail emails  
- **Async/Await Support**: Non-blocking operations throughout
- **Rich Email Parsing**: Handle text, HTML, and attachments
- **Robust Error Handling**: Specific exceptions for different failure modes
- **Type Safety**: Complete type hints and data validation

## Quick Start

### Prerequisites

- Python 3.12+
- Gmail account with API access
- Google Cloud Console project with Gmail API enabled

### Setup Instructions

1. **Create Google Cloud Project**
   ```
   - Go to Google Cloud Console (https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the Gmail API
   ```

2. **Configure OAuth2 Credentials**
   ```
   - Go to APIs & Services > Credentials
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop application"
   - Download the credentials file as credentials.json
   ```

3. **Install Dependencies**
   ```bash
   uv sync --extra email
   ```

4. **Basic Usage**
   ```python
   from mAIgic_integrations.email import GmailClient, GmailConfig
   
   config = GmailConfig(
       credentials_path="credentials.json",
       token_path="token.json"
   )
   
   async with GmailClient(config) as client:
       # Get recent emails
       emails = await client.get_recent_emails(days=7)
       print(f"Found {len(emails)} recent emails")
       
       # Search emails
       results = await client.search_emails("important")
       
       # Get account statistics
       stats = await client.get_account_info()
       print(f"Total messages: {stats.total_messages}")
   ```

## Configuration

### GmailConfig Options

```python
config = GmailConfig(
    credentials_path="credentials.json",  # OAuth2 credentials file
    token_path="token.json",              # Saved authentication tokens
    timeout_seconds=30,                   # Request timeout
    max_retries=3,                        # Maximum retry attempts
    scopes=[                              # Gmail API scopes
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.labels'
    ]
)
```

### Environment Variables

Configure via environment variables:

```bash
export GMAIL_CREDENTIALS_PATH="path/to/credentials.json"
export GMAIL_TOKEN_PATH="path/to/token.json"
export GMAIL_TIMEOUT_SECONDS="45"
export GMAIL_MAX_RETRIES="5"
```

```python
config = GmailConfig.from_env()
```

## API Reference

### Core Methods

- **`get_emails(folder, limit, include_body, since_days)`** - Retrieve emails with filtering
- **`search_emails(query, limit)`** - Search emails using Gmail query syntax
- **`get_email(message_id)`** - Get specific email with full content
- **`get_account_info()`** - Account statistics and information
- **`download_attachment(message_id, attachment_id)`** - Download email attachments

### Email Data Structure

```python
@dataclass
class Email:
    message_id: str
    sender: EmailAddress
    recipients: List[EmailAddress]
    cc_recipients: List[EmailAddress]
    subject: str
    body_text: Optional[str]
    body_html: Optional[str]
    attachments: List[Attachment]
    date_received: Optional[datetime]
    labels: List[str]
```

## Examples

See the examples directory for complete usage examples:

- **basic_operations.py** - Fundamental Gmail operations
- **advanced_operations.py** - Comprehensive AI integration patterns  
- **credential_setup.py** - Credential setup and validation tool

## Testing

```bash
# Run Gmail implementation tests
uv run pytest src/mAIgic_integrations/email/email_gmail_impl/tests/ -v

# Run specific test categories
uv run pytest src/mAIgic_integrations/email/email_gmail_impl/tests/test_clients.py -v
uv run pytest src/mAIgic_integrations/email/email_gmail_impl/tests/test_config.py -v
```

## Error Handling

The implementation provides specific exceptions for different failure modes:

- **`EmailConnectionError`** - Network or service connection issues
- **`EmailAuthenticationError`** - OAuth2 or credential problems
- **`EmailNotFoundError`** - Missing emails or attachments
- **`EmailReceiveError`** - General email retrieval failures
- **`EmailSearchError`** - Search operation failures

## OAuth2 Scopes

The implementation uses these Gmail API scopes:

- `gmail.readonly` - Read emails and account information
- `gmail.modify` - Modify emails (mark read, archive, etc.)
- `gmail.labels` - Manage Gmail labels and folders

## File Structure

After successful setup:

```
project_root/
├── credentials.json     # OAuth2 credentials from Google Cloud Console
├── token.json          # Saved authentication tokens (auto-generated)
└── ...
```

## Security Notes

- Keep `credentials.json` secure and never commit to version control
- `token.json` is auto-generated and contains refresh tokens
- Tokens are automatically refreshed when expired
- All authentication follows Google's OAuth2 best practices 