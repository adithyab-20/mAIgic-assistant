# mAIgic Assistant

A modular AI personal assistant framework with speech processing, email, and calendar integration capabilities. Built with clean component architecture and provider-agnostic design principles.

## Architecture

```
mAIgic-assistant/
├── src/
│   ├── mAIgic_speech/          # Speech processing component
│   │   ├── speech_api/         # Abstract interfaces
│   │   ├── speech_openai_impl/ # OpenAI implementation
│   │   └── examples/           # Usage examples
│   ├── mAIgic_core/           # Core assistant logic
│   └── mAIgic_integrations/   # External service integrations
│       ├── email/             # Email integration
│       │   ├── email_api/     # Abstract interfaces
│       │   └── email_gmail_impl/ # Gmail implementation
│       └── calendar/          # Calendar integration
│           ├── calendar_api/  # Abstract interfaces
│           └── calendar_google_impl/ # Google Calendar implementation
```

## Quick Setup

For complete setup instructions, see [SETUP.md](SETUP.md).

## Installation

### Base Installation
```bash
git clone <repository-url>
cd mAIgic-assistant
uv sync
```

### Optional Components
```bash
# Speech capabilities
uv sync --extra speech

# Email integration
uv sync --extra email

# Calendar integration  
uv sync --extra calendar

# Development tools
uv sync --extra dev

# All components
uv sync --extra speech --extra email --extra calendar --extra dev
```

## Components

### Speech Processing (`mAIgic_speech`)

Provides speech-to-text, text-to-speech, and real-time transcription capabilities.

**Key Dependencies:** `openai`, `aiohttp`, `websockets`, `pyaudio`

```python
from mAIgic_speech.speech_api import AudioFormat
from mAIgic_speech.speech_openai_impl import OpenAISpeechToTextClient, OpenAIConfig

config = OpenAIConfig(api_key="your-api-key")
client = OpenAISpeechToTextClient(config)

async with client:
    transcript = await client.transcribe("audio.wav", AudioFormat.WAV)
    print(transcript)
```

**Processing Modes:**
- **Batch**: Complete audio file transcription
- **Streaming**: Progressive transcription with partial results  
- **Real-time**: Live audio stream processing

### Email Integration (`mAIgic_integrations/email`)

Gmail integration with comprehensive email operations and OAuth2 authentication.

**Key Dependencies:** `google-api-python-client`, `google-auth`

```python
from mAIgic_integrations.email import GmailClient, GmailConfig

config = GmailConfig(
    credentials_path="credentials.json",
    token_path="token.json"
)

async with GmailClient(config) as client:
    emails = await client.get_recent_emails(count=10)
    for email in emails:
        print(f"{email.subject} - {email.sender}")
```

### Calendar Integration (`mAIgic_integrations/calendar`) 

Google Calendar integration with role-based permissions and intelligent scheduling support.

**Key Dependencies:** `google-api-python-client`, `google-auth`, `pendulum`

```python
from mAIgic_integrations.calendar import GoogleCalendarClient, GoogleCalendarConfig

config = GoogleCalendarConfig(
    credentials_path="credentials.json",
    token_path="token.json"
)

async with GoogleCalendarClient(config) as client:
    events = await client.get_events(time_range)
    for event in events:
        print(f"{event.title} - {event.time_slot}")
```

### Integration Registry (`mAIgic_integrations`)

Unified credential management and service discovery system.

```python
from mAIgic_integrations import create_calendar_client, create_email_client

# Automatic credential discovery
calendar = create_calendar_client("google_calendar")
email = create_email_client("google_gmail")
```

## Setup

### Environment Configuration
```bash
# Create .env file
echo "OPENAI_API_KEY=your_api_key_here" > .env
echo "GOOGLE_CALENDAR_ENABLED=true" >> .env
echo "GOOGLE_GMAIL_ENABLED=true" >> .env
```

### Integration Setup
```bash
# Interactive setup wizard
uv run maigic-integrations-setup

# Setup specific services
uv run maigic-integrations-setup --service calendar
uv run maigic-integrations-setup --service gmail

# Check status
uv run maigic-integrations-setup --list
```

## Examples

### Speech Processing
```bash
uv run python src/mAIgic_speech/examples/batch_transcription.py --record
uv run python src/mAIgic_speech/examples/streaming_transcription.py --record
uv run python src/mAIgic_speech/examples/realtime_transcription.py
```

### Email Operations
```bash
uv run python src/mAIgic_integrations/email/email_gmail_impl/examples/basic_gmail_operations.py
```

### Calendar Operations
```bash
uv run python src/mAIgic_integrations/calendar/calendar_google_impl/examples/basic_calendar_operations.py
```

## Development

### Environment Setup
```bash
uv sync --extra dev --extra speech --extra email --extra calendar
```

### Testing
```bash
# Run all tests
uv run pytest

# Test specific components
uv run pytest src/mAIgic_speech/
uv run pytest src/mAIgic_integrations/email/
uv run pytest src/mAIgic_integrations/calendar/
```

### Code Quality
```bash
# Type checking
uv run mypy src/

# Linting and formatting
uv run ruff check src/
uv run ruff format src/
```

## Quality Standards

- **Coverage**: 80%+ test coverage required
- **Type Safety**: Full mypy compliance
- **Code Style**: Ruff formatting and linting standards
- **Documentation**: Comprehensive API documentation

## License

MIT License - see [LICENSE](LICENSE) file for details.
