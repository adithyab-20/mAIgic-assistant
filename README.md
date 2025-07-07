# mAIgic Assistant

A modular AI personal assistant framework with voice, email, and calendar integration capabilities. Built with clean component architecture and provider-agnostic design principles.

## 🏗️ Architecture

The project follows a **hierarchical component structure** inspired by John Ousterhout's "A Philosophy of Software Design":

```
mAIgic-assistant/
├── src/
│   ├── mAIgic_speech/          # Speech processing component
│   │   ├── speech_api/         # Abstract interfaces
│   │   ├── speech_openai_impl/ # OpenAI implementation
│   │   └── examples/           # Speech examples
│   ├── mAIgic_core/           # Assistant logic (future)
│   └── mAIgic_integrations/   # External integrations (future)
```

### Component Benefits
- **Independent Development** - Each component can be developed/tested separately
- **Optional Dependencies** - Install only what you need
- **Provider Agnostic** - Easy to swap implementations
- **Clean Interfaces** - Well-defined component boundaries

## 🚀 Installation

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

# Development tools
uv sync --extra dev

# Everything for development
uv sync --extra dev --extra speech --extra all
```

### Traditional pip Installation
```bash
# Base package
pip install mAIgic-assistant

# With speech capabilities
pip install "mAIgic-assistant[speech]"

# For development
pip install "mAIgic-assistant[dev]"
```

## 🎯 Components

### 🎤 Speech Component (`mAIgic_speech`)

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

### 🧠 Core Component (`mAIgic_core`) - *Coming Soon*

Central assistant logic and orchestration engine.

**Planned Features:**
- Session management
- Context correlation
- Multi-component coordination
- Configuration management

### 🔗 Integrations Component (`mAIgic_integrations`) - *Coming Soon*

External service integrations following the same pattern as speech.

**Planned Integrations:**
- **Email** - Gmail, Outlook, IMAP/SMTP
- **Calendar** - Google Calendar, Outlook Calendar, CalDAV
- **Logging** - Activity tracking and analytics

## 🎵 Speech Features

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

## 📚 Quick Start Examples

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

## 🧪 Development

### Environment Setup
```bash
# Install all development dependencies
uv sync --extra dev --extra speech

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
```

### Quality Standards
- **Coverage**: 80%+ required
- **Type Safety**: Full mypy compliance
- **Code Style**: Ruff formatting and linting
- **Testing**: Comprehensive unit and integration tests

## 📋 Project Status

### ✅ Completed
- **Speech Component** - Full implementation with OpenAI integration
- **Component Architecture** - Hierarchical structure with proper dependency isolation
- **CI/CD Pipeline** - Comprehensive testing, linting, and type checking
- **Documentation** - Component READMEs and examples

### 🚧 In Progress
- **Email Integration** - Gmail and IMAP implementations
- **Calendar Integration** - Google Calendar and CalDAV support
- **Core Assistant Logic** - Session management and orchestration

### 📅 Planned
- **Advanced Context Engine** - Cross-component data correlation
- **Plugin Architecture** - Third-party integration support
- **Web Interface** - Browser-based interaction
- **Mobile Integration** - iOS/Android companion apps

## 🤝 Contributing

We follow a **trunk-based development** workflow with Pull Requests:

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

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
