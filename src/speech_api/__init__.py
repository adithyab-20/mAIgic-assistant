"""Speech API - Interface definitions for speech processing.

This library provides clean interface definitions for speech-to-text and
text-to-speech functionality with support for batch, streaming, and real-time processing.
"""

from .exceptions import (
    APIError,
    AudioError,
    SpeechAPIError,
    SynthesisError,
    TranscriptionError,
)
from .interfaces import (
    SpeechToTextClient,
    TextToSpeechClient,
)
from .types import (
    AudioChunk,
    AudioFormat,
)

__version__ = "0.1.0"

__all__ = [
    # Main interfaces
    "SpeechToTextClient",
    "TextToSpeechClient",

    # Data types
    "AudioChunk",
    "AudioFormat",

    # Exceptions
    "SpeechAPIError",
    "TranscriptionError",
    "SynthesisError",
    "AudioError",
    "APIError",
]
