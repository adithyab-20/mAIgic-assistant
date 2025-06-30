# Speech OpenAI Implementation

This component provides OpenAI implementations of the Speech API interfaces, including support for OpenAI's Audio API and Realtime API.

## Features

- **Traditional Audio API Support** - Whisper transcription and TTS synthesis
- **Realtime API Support** - Low-latency speech-to-speech conversations
- **Provider Agnostic Design** - Implements the core Speech API interfaces
- **Type Safe** - Full type annotations and mypy compliance
- **Async First** - High-performance, non-blocking operations

## Installation

This component is part of the mAIgic Assistant project. Install with OpenAI dependencies:

```bash
uv sync --extra openai
```

## Quick Start

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

# Use with existing Speech API interfaces
transcription = await stt_client.transcribe(audio_chunk)
audio_data = await tts_client.synthesize("Hello world!", voice_id="nova")
```

## Components

### Configuration

```python
from speech_openai_impl import OpenAIConfig

config = OpenAIConfig(
    api_key="your-openai-api-key",
    organization="your-org-id",  # Optional
    base_url="https://api.openai.com/v1",  # Default
    timeout=30  # Default
)
```

### Traditional Audio API Clients

#### OpenAISpeechToTextClient

Implements the `SpeechToTextClient` interface using OpenAI's Whisper models.

```python
from speech_openai_impl import OpenAISpeechToTextClient

stt_client = OpenAISpeechToTextClient(config)

# Batch transcription
transcription = await stt_client.transcribe(
    audio_chunk,
    language="en",
    prompt="Context for better accuracy"
)

# Streaming transcription
async for partial_result in stt_client.transcribe_stream(audio_chunk):
    print(f"Partial: {partial_result}")

# Real-time transcription
async for result in stt_client.transcribe_realtime(audio_stream):
    print(f"Live: {result}")
```

#### OpenAITextToSpeechClient

Implements the `TextToSpeechClient` interface using OpenAI's TTS models.

```python
from speech_openai_impl import OpenAITextToSpeechClient

tts_client = OpenAITextToSpeechClient(config)

# Synthesize speech
audio_data = await tts_client.synthesize(
    "Hello! This is OpenAI's text-to-speech.",
    voice_id="nova",  # Available: alloy, echo, fable, onyx, nova, shimmer
    language="en"
)

# Streaming synthesis
async for audio_chunk in tts_client.synthesize_stream("Long text..."):
    play_audio_chunk(audio_chunk)
```

### Realtime API Client

#### OpenAIRealtimeClient

Provides low-latency speech-to-speech interactions.

```python
from speech_openai_impl import OpenAIRealtimeClient

realtime_client = OpenAIRealtimeClient(config)

# Speech-to-speech conversation
session = await realtime_client.connect_speech_to_speech(
    model="gpt-4o-realtime-preview-2025-06-03",
    voice="alloy",
    system_prompt="You are a helpful AI assistant."
)

await session.initialize_session()

# Send audio and receive responses
async for audio_chunk in microphone_stream():
    await session.send_audio(audio_chunk.data)

async for event in session.receive_events():
    if event["type"] == "audio.output":
        play_audio(base64.b64decode(event["data"]["audio"]))

# Transcription-only session
transcription_session = await realtime_client.connect_transcription(
    model="gpt-4o-transcribe"
)

async for transcription in transcription_session.receive_transcriptions():
    print(f"Transcription: {transcription}")
```

## Voice Agent Patterns

### Chained Approach

Build voice agents by chaining STT → LLM → TTS:

```python
async def voice_agent_conversation():
    # Step 1: Transcribe user audio
    user_text = await stt_client.transcribe(user_audio)
    
    # Step 2: Generate AI response (using Chat Completions API)
    ai_response = f"I heard you say: '{user_text}'. How can I help you?"
    
    # Step 3: Convert response to speech
    audio_response = await tts_client.synthesize(ai_response, voice_id="nova")
    
    # Step 4: Play response
    play_audio(audio_response)
```

### Realtime Approach

Direct speech-to-speech for natural conversations:

```python
async def realtime_voice_agent():
    session = await realtime_client.connect_speech_to_speech(
        model="gpt-4o-realtime-preview-2025-06-03",
        voice="alloy"
    )
    
    await session.initialize_session()
    
    # Handle real-time conversation
    async for event in session.receive_events():
        if event["type"] == "audio.output":
            play_audio(base64.b64decode(event["data"]["audio"]))
        elif event["type"] == "text.output":
            print(f"AI: {event['data']['text']}")
```

## Error Handling

The component uses the same exception hierarchy as the main Speech API:

```python
from speech_api.exceptions import TranscriptionError, SynthesisError, APIError

try:
    transcription = await stt_client.transcribe(audio_chunk)
except TranscriptionError as e:
    print(f"Transcription failed: {e}")
except APIError as e:
    print(f"API error: {e}")
```

## Testing

Run the component tests:

```bash
# Run all tests
uv run pytest src/speech_openai_impl/tests/

# Run specific test files
uv run pytest src/speech_openai_impl/tests/test_openai_clients.py
uv run pytest src/speech_openai_impl/tests/test_realtime_sessions.py
```

## Dependencies

- `aiohttp>=3.8.0` - For HTTP requests to OpenAI API
- `websockets>=11.0.0` - For WebSocket connections to Realtime API
- `speech-api>=0.1.0` - Core Speech API interfaces

## License

This component is part of the mAIgic Assistant project and is licensed under the MIT License. 