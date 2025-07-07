# mAIgic Assistant - Speech API

A clean interface library for speech-to-text and text-to-speech functionality, designed for hands-free voice assistants and earpiece applications. Built with provider-agnostic design principles and comprehensive type safety.

## Features

- **Provider Agnostic** - Easy integration with OpenAI, local models, and other speech services
- **Consistent API Design** - Same interface across batch, streaming, and realtime modes
- **Real-time Streaming** - Support for live audio processing and streaming responses
- **Type Safe** - Full type annotations with mypy compliance
- **Async First** - Built for high-performance, non-blocking audio processing
- **Modular Components** - Separate components for core interfaces and provider implementations

## Components

### Core Speech API (`speech_api`)
- Clean interface definitions for speech processing
- Provider-agnostic design with consistent client interface
- Type-safe data structures
- Exception hierarchy

### OpenAI Implementation (`speech_openai_impl`)
- OpenAI Audio API integration (Whisper + TTS)
- OpenAI Realtime API support
- Low-latency speech-to-speech conversations
- Voice agent building capabilities

## Architecture

### Client-First Design

The library follows a **client-first design** where all functionality is accessed through clean client interfaces:

```python
# Single client for all speech processing
client = OpenAISpeechToTextClient(config)

# All transcription modes use the same client
await client.transcribe(audio)           # Batch
async for result in client.transcribe_stream(audio):  # Streaming
async for event in client.transcribe_realtime(source, config):  # Realtime
```

### Internal Implementation

The library uses internal session management for realtime functionality, but users never need to interact with sessions directly:

- **`clients.py`** - Public client interfaces (what you use)
- **`sessions.py`** - Internal session implementations (implementation detail)
- **`audio_sources.py`** - Audio input abstractions

### Why Sessions Exist

Sessions handle the complex WebSocket communication and state management required for realtime transcription. The `transcribe_realtime()` method internally:

1. Creates a session
2. Manages the WebSocket connection
3. Streams audio from your source
4. Yields transcription events
5. Handles cleanup automatically

This complexity is hidden behind the simple `client.transcribe_realtime()` interface.

## Installation

See the [Prerequisites](#prerequisites) section above for installation instructions.

## Quick Start

### Prerequisites

```bash
# Clone the repository
git clone <repository-url>
cd mAIgic-assistant

# Install with development dependencies
uv sync --extra dev

# Install with OpenAI support
uv sync --extra openai

# For audio recording functionality (optional)
pip install pyaudio
```

**Set up your OpenAI API key:**
```bash
# Create a .env file in the project root
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

### API Design

The library provides a **consistent client interface** that works across all transcription modes:

```python
from speech_api import SpeechToTextClient, AudioChunk, RealtimeSessionConfig
from speech_openai_impl import OpenAIConfig, OpenAISpeechToTextClient

# Single client for all transcription modes
config = OpenAIConfig(api_key="your-openai-api-key")
client = OpenAISpeechToTextClient(config)

# 1. Batch transcription (complete audio files)
result = await client.transcribe(audio_chunk, language="en")

# 2. Streaming transcription (partial results)
async for partial in client.transcribe_stream(audio_chunk, language="en"):
    print(f"Partial: {partial}")

# 3. Realtime transcription (live audio)
config = RealtimeSessionConfig(model="gpt-4o-transcribe")
async for event in client.transcribe_realtime(audio_source, config):
    print(f"Live: {event.text}")
```

### Basic Usage

```python
from speech_api import SpeechToTextClient, TextToSpeechClient, AudioChunk

# Initialize your speech processing clients
stt_client = YourSpeechToTextClient()
tts_client = YourTextToSpeechClient()

# Transcribe audio
audio_chunk = AudioChunk(data=audio_bytes)
transcription = await stt_client.transcribe(
    audio_chunk,
    language="en",
    prompt="Context for better transcription accuracy"
)

# Synthesize speech
audio_data = await tts_client.synthesize(
    "Hello, how can I help you today?",
    voice_id="nova",
    language="en"
)
```

### OpenAI Integration

```python
from speech_openai_impl import (
    OpenAIConfig,
    OpenAISpeechToTextClient,
    OpenAITextToSpeechClient,
    OpenAIRealtimeClient
)

# Configure OpenAI
config = OpenAIConfig(api_key="your-openai-api-key")

# Create clients
stt_client = OpenAISpeechToTextClient(config)
tts_client = OpenAITextToSpeechClient(config)

# Text-to-Speech
audio_data = await tts_client.synthesize(
    "Hello! This is OpenAI's text-to-speech.",
    voice_id="nova"
)

# Speech-to-Text (all modes use the same client)
transcription = await stt_client.transcribe(audio_chunk)

# Real-time voice agent
realtime_client = OpenAIRealtimeClient(config)
session = await realtime_client.connect_speech_to_speech(
    model="gpt-4o-realtime-preview-2025-06-03",
    voice="alloy"
)
```

## Processing Modes

### Speech-to-Text

| Mode | Method | Input | Output | Use Case |
|------|--------|-------|--------|----------|
| **Batch** | `client.transcribe()` | Complete audio file | Full transcription | Voice memos, recordings |
| **Streaming** | `client.transcribe_stream()` | Complete audio file | Partial results | Long recordings, progress feedback |
| **Real-time** | `client.transcribe_realtime()` | Live audio stream | Live results | Live conversation, wake word detection |

**Key Benefits:**
- ✅ **Single Client** - All modes use the same `SpeechToTextClient`
- ✅ **Consistent Interface** - Same parameter patterns across modes
- ✅ **Unified Error Handling** - All methods raise `TranscriptionError`
- ✅ **Provider Agnostic** - Easy to swap providers without changing code
- ✅ **Clean Mental Model** - `client.method(input) → output`

### Text-to-Speech

| Mode | Method | Input | Output | Use Case |
|------|--------|-------|--------|----------|
| **Batch** | `synthesize()` | Complete text | Full audio file | Short responses, file generation |
| **Streaming** | `synthesize_stream()` | Complete text | Audio chunks | Long responses, real-time playback |

## OpenAI Features

### Traditional Audio API

- **Whisper + GPT-4o Transcription** - High-accuracy speech-to-text with newer `gpt-4o-mini-transcribe` and `gpt-4o-transcribe` models
- **Native Streaming** - OpenAI's built-in streaming transcription support with `stream=True`
- **TTS Models** - Natural-sounding text-to-speech with multiple voices
- **Multi-language Support** - 99+ languages supported
- **Batch Processing** - Process complete audio files

### Realtime API

- **Low-latency Conversations** - Real-time speech-to-speech interactions
- **Streaming Transcription** - Live audio transcription with voice activity detection
- **WebSocket Support** - Direct connection to OpenAI's realtime models
- **Voice Agent Building** - Complete voice assistant capabilities

### Voice Agent Patterns

- **Chained Approach** - STT → LLM → TTS for controlled responses
- **Realtime Approach** - Direct speech-to-speech for natural conversations
- **Hybrid Patterns** - Combine both approaches for optimal performance

## Usage Examples

### Transcription API

```python
from speech_api import AudioChunk, RealtimeSessionConfig
from speech_openai_impl import OpenAIConfig, OpenAISpeechToTextClient

config = OpenAIConfig(api_key="your-key")
client = OpenAISpeechToTextClient(config)

# 1. Batch transcription
transcription = await client.transcribe(
    audio_chunk,
    language="en",
    prompt="Context for better accuracy"
)

# 2. Streaming transcription
async for partial in client.transcribe_stream(
    audio_chunk,
    language="en"
):
    print(f"Partial: {partial}")

# 3. Realtime transcription
realtime_config = RealtimeSessionConfig(
    model="gpt-4o-transcribe",
    language="en",
    enable_partial_results=True
)

async for event in client.transcribe_realtime(audio_source, realtime_config):
    if event.text:
        print(f"Live: {event.text}")
```

### Batch Processing

```python
# Transcribe a complete audio file
transcription = await stt_client.transcribe(audio_chunk)
print(transcription)  # "Hello world, how are you today?"

# Synthesize complete text to audio
audio_data = await tts_client.synthesize("Your meeting is at 2 PM")
with open("response.mp3", "wb") as f:
    f.write(audio_data)
```

### Streaming Processing

```python
# Stream transcription results
async for partial_result in stt_client.transcribe_stream(audio_chunk):
    print(f"Partial: {partial_result}")
    # "Hello"
    # "Hello world"
    # "Hello world, how are you today?"

# Stream audio synthesis
async for audio_chunk in tts_client.synthesize_stream("Long text to synthesize"):
    play_audio_chunk(audio_chunk)  # Start playing immediately
```

### Real-time Processing

```python
# Real-time transcription from microphone
from speech_openai_impl import PyAudioMicrophoneSource

audio_source = PyAudioMicrophoneSource(sample_rate=16000)
config = RealtimeSessionConfig(model="gpt-4o-transcribe")

async for event in client.transcribe_realtime(audio_source, config):
    if event.text:
        print(f"Live: {event.text}")
        # "Hey"
        # "Hey assistant"
        # "Hey assistant, what's the weather like?"
```

### OpenAI Realtime Voice Agent

```python
# Connect to OpenAI Realtime API
session = await realtime_client.connect_speech_to_speech(
    model="gpt-4o-realtime-preview-2025-06-03",
    voice="alloy",
    system_prompt="You are a helpful AI assistant."
)

await session.initialize_session()

# Send audio and receive responses
async def voice_conversation():
    async for audio_chunk in microphone_stream():
        await session.send_audio(audio_chunk.data)
    
    async for event in session.receive_events():
        if event["type"] == "audio.output":
            play_audio(base64.b64decode(event["data"]["audio"]))
        elif event["type"] == "text.output":
            print(f"AI: {event['data']['text']}")

await voice_conversation()
```

## Working Examples

The `examples/` directory contains fully functional examples with built-in audio recording:

### Try It Now

```bash
# Batch transcription with recording
uv run python examples/batch_transcription.py --record

# Streaming transcription with recording  
uv run python examples/streaming_transcription.py --record

# Realtime transcription from microphone
uv run python examples/realtime_transcription.py
```

### Example Features

- **🎤 Built-in Recording** - Record audio directly from your microphone
- **📁 File Support** - Use existing audio files (WAV, MP3, FLAC, OGG)
- **🔄 Interactive Mode** - Prompted choices when no arguments provided
- **🧹 Auto Cleanup** - Temporary files automatically removed
- **⚡ Multiple Models** - Uses latest `gpt-4o-mini-transcribe` for quality

See the [examples README](examples/README.md) for detailed documentation.

## API Reference

### SpeechToTextClient

```python
class SpeechToTextClient(ABC):
    async def transcribe(
        self,
        audio: AudioChunk,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> str:
        """Transcribe complete audio to text."""

    async def transcribe_stream(
        self,
        audio: AudioChunk,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Transcribe with streaming partial results."""

    async def transcribe_realtime(
        self,
        audio_stream: AsyncGenerator[AudioChunk, None],
        language: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Real-time transcription of live audio."""

    async def get_supported_languages(self) -> List[str]:
        """Get supported language codes."""
```

### TextToSpeechClient

```python
class TextToSpeechClient(ABC):
    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        language: Optional[str] = None,
    ) -> bytes:
        """Convert text to audio."""

    async def synthesize_stream(
        self,
        text: str,
        voice_id: Optional[str] = None,
        language: Optional[str] = None,
    ) -> AsyncGenerator[bytes, None]:
        """Convert text to streaming audio."""

    async def get_available_voices(self) -> List[str]:
        """Get available voice options."""
```

### OpenAI Realtime Client

```python
class OpenAIRealtimeClient:
    async def connect_speech_to_speech(
        self,
        model: str = "gpt-4o-realtime-preview-2025-06-03",
        voice: str = "alloy",
        system_prompt: Optional[str] = None,
    ) -> OpenAIRealtimeSession:
        """Connect to OpenAI Realtime API for speech-to-speech conversation."""

    async def connect_transcription(
        self,
        model: str = "gpt-4o-transcribe",
    ) -> OpenAIRealtimeTranscriptionSession:
        """Connect to OpenAI Realtime API for transcription-only use case."""
```

## Data Types

### AudioChunk
```python
@dataclass
class AudioChunk:
    data: bytes
    sample_rate: int = 16000
    channels: int = 1
    bit_depth: int = 16
    format: AudioFormat = AudioFormat.WAV
    duration_ms: Optional[int] = None
```

### AudioFormat
```python
class AudioFormat(Enum):
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"
```

## Async Generator Patterns

### Interface Design

The library uses a clean async generator pattern that follows Python best practices:

```python
# Abstract interface methods that return AsyncGenerator
@abstractmethod
async def transcribe_stream(...) -> AsyncGenerator[str, None]:
    """Streaming transcription interface."""
    yield  # type: ignore[misc]  # Required for mypy compatibility

# Implementation uses standard async generator syntax
async def transcribe_stream(...) -> AsyncGenerator[str, None]:
    """Actual implementation with real yielding."""
    for partial_result in process_audio_stream():
        yield partial_result
```

### Usage Patterns

All streaming methods return async generators that can be consumed directly:

```python
# Clean, intuitive usage
async for chunk in client.transcribe_stream(audio):
    print(chunk)

async for audio_chunk in client.synthesize_stream(text):
    play_audio(audio_chunk)
```

## Error Handling

The library provides a comprehensive exception hierarchy:

- `SpeechAPIError` - Base exception for all speech API errors
- `TranscriptionError` - Errors during speech-to-text processing
- `SynthesisError` - Errors during text-to-speech synthesis
- `AudioError` - Errors related to audio format or content
- `APIError` - Errors from underlying API providers


## Running Tests

```bash
# Run tests with coverage
uv run pytest

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/
```

### Component Testing

```bash
# Test core speech API
uv run pytest src/speech_api/tests/

# Test OpenAI implementation
uv run pytest src/speech_openai_impl/tests/

# Test specific components
uv run pytest src/speech_openai_impl/tests/test_openai_clients.py
uv run pytest src/speech_openai_impl/tests/test_realtime_sessions.py
```

### OpenAI Integration Testing

```bash
# Install OpenAI dependencies
uv sync --extra openai

# Run examples
uv run python examples/openai_integration_example.py
```

## Documentation

- [OpenAI Integration Guide](docs/openai_integration.md) - Comprehensive guide for OpenAI features
- [API Reference](docs/api_reference.md) - Complete API documentation
- [Examples](examples/README.md) - Working examples with audio recording
- [Component Documentation](src/speech_openai_impl/README.md) - OpenAI implementation details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
