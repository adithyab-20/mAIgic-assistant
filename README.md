# mAIgic Assistant

A modular AI personal assistant framework with voice, email, and calendar integration capabilities. Built with clean component architecture and provider-agnostic design principles.

## Architecture

The project follows a hierarchical component structure for maintainability and extensibility:

```
mAIgic-assistant/
├── src/
│   ├── mAIgic_speech/          # Speech processing component
│   │   ├── speech_api/         # Abstract interfaces
│   │   ├── speech_openai_impl/ # OpenAI implementation
│   │   └── examples/           # Speech examples
│   ├── mAIgic_core/           # Assistant logic
│   └── mAIgic_integrations/   # External integrations
│       ├── email/             # Email integration
│       │   ├── email_api/     # Abstract interfaces
│       │   └── email_gmail_impl/ # Gmail implementation
│       └── calendar/          # Calendar integration
│           └── calendar_api/  # Abstract interfaces
```

## Installation

### Base Installation
```bash
# Clone and install base package
git clone <repository-url>
cd mAIgic-assistant
uv sync
```

### Optional Features
```bash
# Speech capabilities (OpenAI integration)
uv sync --extra speech

# Email integration (Gmail)
uv sync --extra email

# Calendar integration
uv sync --extra calendar

# Development tools
uv sync --extra dev

# Everything for development
uv sync --extra dev --extra speech --extra email --extra calendar --extra all
```

### Traditional pip Installation
```bash
# Base package
pip install mAIgic-assistant

# With speech capabilities
pip install "mAIgic-assistant[speech]"

# With email integration
pip install "mAIgic-assistant[email]"

# With calendar integration
pip install "mAIgic-assistant[calendar]"

# With all integrations
pip install "mAIgic-assistant[speech,email,calendar]"

# For development
pip install "mAIgic-assistant[dev]"
```

## Components

### Speech Component (`mAIgic_speech`)

Complete speech processing with speech-to-text, text-to-speech, and real-time transcription.

**Dependencies:** `aiohttp`, `websockets`, `pyaudio`

```python
from mAIgic_speech.speech_api import AudioFormat
from mAIgic_speech.speech_openai_impl import OpenAISpeechToTextClient, OpenAIConfig

# Configure and use
config = OpenAIConfig(api_key="your-api-key")
client = OpenAISpeechToTextClient(config)

async with client:
    transcript = await client.transcribe("audio.wav", AudioFormat.WAV)
    print(transcript)
```

**Features:**
- Provider-agnostic interfaces
- OpenAI Whisper + TTS integration
- Real-time WebSocket transcription
- Multiple processing modes (batch/streaming/realtime)

### Email Integration (`mAIgic_integrations/email`)

Gmail integration with comprehensive email operations for AI assistants.

**Dependencies:** `google-api-python-client`, `google-auth`

```python
from mAIgic_integrations.email import GmailClient, GmailConfig

# Configure and use
config = GmailConfig(
    credentials_path="credentials.json",
    token_path="token.json"
)

async with GmailClient(config) as client:
    emails = await client.get_recent_emails(count=10)
    for email in emails:
        print(f"{email.subject} - {email.sender}")
```

**Features:**
- Gmail API integration with OAuth2
- Rich email data models  
- Advanced search capabilities
- Account information and statistics

### Calendar Integration (`mAIgic_integrations/calendar`)

Role-based calendar integration with intelligent scheduling support for AI assistants.

**Current Status:** Interface defined, providers in development

```python
from mAIgic_integrations.calendar import (
    CalendarClient, Event, TimeSlot, CalendarDateTime
)

# Future Google Calendar implementation
# async with GoogleCalendarClient(config) as client:
#     today = CalendarDateTime.now()
#     events = await client.get_events(TimeSlot(today, today.add_hours(24)))
#     
#     meeting = Event(title="Team Meeting", time_slot=time_slot)
#     result = await client.create_my_event(meeting)
```

**Features:**
- Role-based permission model (organizer vs attendee)
- Rich event data with conflict detection
- Time abstraction with timezone support
- Availability finding and smart scheduling

## Speech Features

### Processing Modes

| Mode | Method | Input | Output | Use Case |
|------|--------|-------|--------|----------|
| **Batch** | `client.transcribe()` | Complete audio file | Full transcription | Voice memos, recordings |
| **Streaming** | `client.transcribe_stream()` | Complete audio file | Partial results | Long recordings, progress feedback |
| **Real-time** | `client.transcribe_realtime()` | Live audio stream | Live results | Live conversation, wake word detection |

### OpenAI Integration

- **Whisper Models** - High-accuracy speech-to-text with `gpt-4o-mini-transcribe` and `gpt-4o-transcribe`
- **TTS Models** - Natural-sounding text-to-speech with multiple voices
- **Realtime API** - Low-latency speech-to-speech conversations
- **Multi-language Support** - 99+ languages supported

## Quick Start Examples

### Prerequisites
```bash
# Set up your OpenAI API key
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

### Basic Transcription
```python
from mAIgic_speech.speech_api import AudioChunk, RealtimeSessionConfig
from mAIgic_speech.speech_openai_impl import OpenAIConfig, OpenAISpeechToTextClient

config = OpenAIConfig(api_key="your-key")
client = OpenAISpeechToTextClient(config)

# Batch transcription
transcription = await client.transcribe(
    audio_chunk,
    language="en",
    prompt="Context for better accuracy"
)

# Streaming transcription
async for partial in client.transcribe_stream(audio_chunk, language="en"):
    print(f"Partial: {partial}")

# Realtime transcription
realtime_config = RealtimeSessionConfig(model="gpt-4o-transcribe")
async for event in client.transcribe_realtime(audio_source, realtime_config):
    if event.text:
        print(f"Live: {event.text}")
```

### Working Examples

Run these examples immediately after installation:

```bash
# Install speech dependencies
uv sync --extra speech

# Try the examples
uv run python src/mAIgic_speech/examples/batch_transcription.py --record
uv run python src/mAIgic_speech/examples/streaming_transcription.py --record  
uv run python src/mAIgic_speech/examples/realtime_transcription.py
```

## Development

### Environment Setup
```bash
# Install all development dependencies
uv sync --extra dev --extra speech --extra email --extra calendar

# Run tests
uv run pytest

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/
```

### Component Testing
```bash
# Test specific components
uv run pytest src/mAIgic_speech/
uv run pytest src/mAIgic_speech/speech_api/tests/
uv run pytest src/mAIgic_speech/speech_openai_impl/tests/

# Test email integration
uv run pytest src/mAIgic_integrations/email/
uv run pytest src/mAIgic_integrations/email/email_api/tests/
uv run pytest src/mAIgic_integrations/email/email_gmail_impl/tests/

# Test calendar integration
uv run pytest src/mAIgic_integrations/calendar/
uv run pytest src/mAIgic_integrations/calendar/calendar_api/tests/
```

### Quality Standards
- **Coverage**: 80%+ required
- **Type Safety**: Full mypy compliance
- **Code Style**: Ruff formatting and linting
- **Testing**: Comprehensive unit and integration tests


## Contributing

We follow a trunk-based development workflow with Pull Requests:

1. Fork the repository
2. Create a feature branch (`feat/feature-name`)
3. Make your changes following our [PR template](.github/pull_request_template.md)
4. Ensure tests pass and coverage is maintained
5. Submit a pull request

### Quality Checklist
- [ ] Tests pass: `uv run pytest`
- [ ] Types check: `uv run mypy src/`
- [ ] Linting passes: `uv run ruff check src/`
- [ ] Coverage maintained: `uv run pytest --cov=src --cov-fail-under=80`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
