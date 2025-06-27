# mAIgic Assistant - Speech API

A clean interface library for speech-to-text and text-to-speech functionality, designed for hands-free voice assistants and earpiece applications. Built with provider-agnostic design principles and comprehensive type safety.

## Features

- **Provider Agnostic** - Easy integration with OpenAI, local models, and other speech services
- **Real-time Streaming** - Support for live audio processing and streaming responses
- **Type Safe** - Full type annotations with mypy compliance
- **Async First** - Built for high-performance, non-blocking audio processing


## Installation

```bash
# Clone the repository
git clone <repository-url>
cd mAIgic-assistant

# Install with development dependencies
uv sync --extra dev
```

## Quick Start

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

## Processing Modes

### Speech-to-Text

| Mode | Method | Input | Output | Use Case |
|------|--------|-------|--------|----------|
| **Batch** | `transcribe()` | Complete audio file | Full transcription | Voice memos, recordings |
| **Streaming** | `transcribe_stream()` | Complete audio file | Partial results | Long recordings, progress feedback |
| **Real-time** | `transcribe_realtime()` | Live audio stream | Live results | Live conversation, wake word detection |

### Text-to-Speech

| Mode | Method | Input | Output | Use Case |
|------|--------|-------|--------|----------|
| **Batch** | `synthesize()` | Complete text | Full audio file | Short responses, file generation |
| **Streaming** | `synthesize_stream()` | Complete text | Audio chunks | Long responses, real-time playback |

## Usage Examples

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
async def audio_stream():
    while True:
        chunk = await get_microphone_chunk()
        yield AudioChunk(data=chunk)

async for transcription in stt_client.transcribe_realtime(audio_stream()):
    print(f"Live: {transcription}")
    # "Hey"
    # "Hey assistant"
    # "Hey assistant, what's the weather like?"
```

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

## Development

### Running Tests

```bash
# Run tests with coverage
uv run pytest

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/
```

### Project Structure

```