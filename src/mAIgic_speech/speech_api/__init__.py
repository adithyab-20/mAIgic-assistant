"""Speech API - Core interfaces for speech processing.

This library provides clean interface definitions for speech-to-text and
text-to-speech functionality with support for batch, streaming, and real-time processing.

Example:
    from speech_api import SpeechToTextClient, AudioChunk, AudioFormat

    # Use a provider implementation
    from speech_openai_impl import OpenAISpeechToTextClient, OpenAIConfig

    config = OpenAIConfig(api_key="your-api-key")
    client = OpenAISpeechToTextClient(config)

    async with client:
        # Batch transcription
        result = await client.transcribe(audio_chunk)

        # Streaming transcription
        async for partial in client.transcribe_stream(audio_chunk):
            print(partial)

        # Realtime transcription
        async for event in client.transcribe_realtime(audio_source, config):
            print(f"{'Final' if event.is_final else 'Partial'}: {event.text}")
"""

from .exceptions import (
    APIError,
    AudioError,
    AudioSourceError,
    RealtimeSessionError,
    RealtimeTranscriptionError,
    SessionClosedError,
    SessionConnectionError,
    SpeechAPIError,
    SynthesisError,
    TranscriptionError,
)
from .interfaces import (
    AudioSource,
    RealtimeTranscriptionSession,
    SpeechToTextClient,
    StreamingAudioSource,
    TextToSpeechClient,
)
from .types import (
    AudioChunk,
    AudioFormat,
    RealtimeSessionConfig,
    SpeechEvent,
    TranscriptionEvent,
)

__version__ = "0.1.0"

__all__ = [
    # Main interfaces
    "SpeechToTextClient",
    "TextToSpeechClient",
    "RealtimeTranscriptionSession",

    # Audio source interfaces
    "AudioSource",
    "StreamingAudioSource",

    # Data types
    "AudioChunk",
    "AudioFormat",
    "RealtimeSessionConfig",
    "SpeechEvent",
    "TranscriptionEvent",

    # Exceptions
    "SpeechAPIError",
    "TranscriptionError",
    "SynthesisError",
    "AudioError",
    "AudioSourceError",
    "APIError",
    "RealtimeSessionError",
    "RealtimeTranscriptionError",
    "SessionClosedError",
    "SessionConnectionError",
]
