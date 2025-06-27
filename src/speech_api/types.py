"""Core data types for the speech API."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class AudioFormat(Enum):
    """Supported audio formats."""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"


@dataclass
class AudioChunk:
    """A chunk of audio data with metadata."""
    data: bytes
    sample_rate: int = 16000
    channels: int = 1
    bit_depth: int = 16
    format: AudioFormat = AudioFormat.WAV
    duration_ms: Optional[int] = None
