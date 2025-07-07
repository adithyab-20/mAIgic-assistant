"""Core data types for the speech API."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Literal, Optional


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


@dataclass
class SpeechEvent:
    """Speech activity detection event."""
    type: Literal["started", "stopped", "detected"]
    timestamp: float
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TranscriptionEvent:
    """Real-time transcription event."""
    text: str
    is_final: bool
    confidence: Optional[float] = None
    language: Optional[str] = None
    timestamp: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class RealtimeSessionConfig:
    """Configuration for realtime transcription sessions."""
    model: str
    language: Optional[str] = None
    prompt: Optional[str] = None
    enable_speech_detection: bool = True
    enable_partial_results: bool = True
    audio_format: AudioFormat = AudioFormat.WAV
    sample_rate: int = 16000
    channels: int = 1
    bit_depth: int = 16
    metadata: Optional[Dict[str, Any]] = None
