"""OpenAI implementation for the Speech API.

This module provides OpenAI implementations of the Speech API interfaces,
including support for OpenAI's Audio API and Realtime API.

Example:
    from speech_openai_impl import OpenAISpeechToTextClient, OpenAIConfig

    config = OpenAIConfig(api_key="your-api-key")
    client = OpenAISpeechToTextClient(config)

    async with client:
        # Use the client for transcription
        result = await client.transcribe(audio_chunk)
"""

from .audio_sources import (
    FileAudioSource,
    PyAudioMicrophoneSource,
)
from .clients import (
    OpenAISpeechToTextClient,
    OpenAITextToSpeechClient,
)
from .config import OpenAIConfig
from .sessions import (
    OpenAIRealtimeClient,
    OpenAIRealtimeTranscriptionSession,
    RealtimeSpeechToSpeechSession,
)

__version__ = "0.1.0"

__all__ = [
    # Configuration
    "OpenAIConfig",

    # Speech-to-Text clients
    "OpenAISpeechToTextClient",

    # Text-to-Speech clients
    "OpenAITextToSpeechClient",

    # Realtime API client
    "OpenAIRealtimeClient",

    # Session classes (internal use)
    "OpenAIRealtimeTranscriptionSession",
    "RealtimeSpeechToSpeechSession",

    # Audio sources
    "PyAudioMicrophoneSource",
    "FileAudioSource",
]
