# Gmail Integration Examples

Professional examples demonstrating Gmail integration patterns for the mAIgic Assistant.

## Available Examples

### credential_setup.py
**Credential Setup and Validation Tool**

Interactive utility for setting up and validating Gmail API credentials with comprehensive troubleshooting support.

```bash
uv run python src/mAIgic_integrations/email/examples/credential_setup.py
```

Features:
- Validates `credentials.json` format and OAuth2 structure
- Provides step-by-step Google Cloud Console setup instructions
- Checks authentication token status and file permissions
- Interactive troubleshooting for common configuration issues
- Complete setup verification workflow

### basic_operations.py
**Fundamental Gmail Operations**

Demonstrates core Gmail client functionality with clean, production-ready code patterns.

```bash
uv run python src/mAIgic_integrations/email/examples/basic_operations.py
```

Operations demonstrated:
- Client configuration and secure connection management
- Recent email retrieval with date filtering
- Email search operations with query processing
- Account statistics and metadata access
- Proper async context management and cleanup

### advanced_operations.py
**Comprehensive Gmail Integration**

Advanced example showcasing Gmail client capabilities for AI assistant integration with comprehensive error handling.

```bash
uv run python src/mAIgic_integrations/email/examples/advanced_operations.py
```

Features demonstrated:
- Account information analysis for AI context gathering
- Email content inspection and metadata extraction
- Advanced search operations with multiple query types
- Attachment identification and processing workflows
- Folder-based email organization and retrieval
- Production-ready error handling and recovery patterns

## Prerequisites

### Required Setup

1. **Google Cloud Project Configuration**
   - Gmail API enabled in Google Cloud Console
   - OAuth2 credentials configured as Desktop application
   - OAuth consent screen properly configured

2. **Credential Files**
   ```
   credentials.json - OAuth2 credentials from Google Cloud Console
   token.json       - Authentication tokens (auto-generated on first use)
   ```

3. **Dependencies**
   ```bash
   uv sync --extra email
   ```

## Usage Patterns

### Client Configuration
```python
from mAIgic_integrations.email import GmailClient, GmailConfig

# File-based configuration
config = GmailConfig(
    credentials_path="credentials.json",
    token_path="token.json"
)

# Environment-based configuration
config = GmailConfig.from_env()

# Use with async context manager
async with GmailClient(config) as client:
    # Gmail operations here
    pass
```

### Error Handling
```python
from mAIgic_integrations.email import (
    GmailClient, 
    EmailConnectionError,
    EmailAuthenticationError,
    EmailConfigurationError
)

try:
    async with GmailClient(config) as client:
        emails = await client.get_recent_emails()
except EmailAuthenticationError:
    print("Authentication failed - verify credentials")
except EmailConnectionError:
    print("Connection failed - check network and quotas")
except EmailConfigurationError:
    print("Configuration error - validate setup")
```

### Configuration Management
```python
# Production configuration with custom settings
config = GmailConfig(
    credentials_path="path/to/credentials.json",
    token_path="path/to/token.json",
    timeout_seconds=45,
    max_retries=5,
    scopes=[
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
)
```

## Running Examples

### Development Workflow
```bash
# Step 1: Validate setup
uv run python src/mAIgic_integrations/email/examples/credential_setup.py

# Step 2: Test basic operations
uv run python src/mAIgic_integrations/email/examples/basic_operations.py

# Step 3: Explore advanced features
uv run python src/mAIgic_integrations/email/examples/advanced_operations.py
```

### Debug Mode
```bash
# Run with Python debugging
uv run python -m pdb src/mAIgic_integrations/email/examples/advanced_operations.py

# Enable verbose logging
export GMAIL_DEBUG=true
uv run python src/mAIgic_integrations/email/examples/basic_operations.py
```

## Best Practices

### Authentication Security
- Store credentials outside version control (add to .gitignore)
- Use environment variables for production deployments
- Implement proper credential rotation procedures
- Monitor OAuth token expiration and refresh cycles

### Error Handling
- Implement specific exception handling for different failure modes
- Use retry logic with exponential backoff for transient failures
- Provide meaningful error messages for troubleshooting
- Log authentication and connection events appropriately

### Performance Optimization
- Use async/await patterns consistently throughout application
- Implement appropriate rate limiting to respect Gmail API quotas
- Cache frequently accessed data when appropriate
- Batch operations for bulk email processing

### Code Quality
- Follow type safety with comprehensive type hints
- Validate input parameters before API calls
- Handle edge cases (empty results, malformed data)
- Use proper resource cleanup with context managers

## Troubleshooting

### Common Setup Issues

**Missing credentials.json**
```
Solution: Run credential_setup.py for guided configuration
```

**OAuth authentication failures**
```
Solution: Delete token.json and re-authenticate via browser
```

**Gmail API quota exceeded**
```
Solution: Implement rate limiting or request quota increase
```

**Network connectivity problems**
```
Solution: Verify firewall settings and proxy configuration
```

### Debug Information

Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Your Gmail client code here
```

## Integration Patterns

These examples demonstrate patterns suitable for:

### AI Assistant Context Gathering
- Account statistics for user context
- Recent email summarization
- Content analysis for conversation context
- Attachment processing for document analysis

### Automated Email Processing
- Inbox monitoring and filtering
- Email classification and routing
- Content extraction and parsing
- Attachment download and processing

### User Interface Integration
- Email list generation for user interfaces
- Search functionality with natural language queries
- Account management and statistics display
- Real-time email status updates

All examples follow production-ready patterns with comprehensive error handling, type safety, and async/await usage throughout.