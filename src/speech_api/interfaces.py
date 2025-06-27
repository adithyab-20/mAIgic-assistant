"""Speech to Text and Text to Speech interfaces."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Optional

from .types import AudioChunk


class SpeechToTextClient(ABC):
    """Interface for converting speech to text."""

    @abstractmethod
    async def transcribe(
        self,
        audio: AudioChunk,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> str:
        """Transcribe complete audio to text (batch mode)."""
        pass

    @abstractmethod
    async def transcribe_stream(
        self,
        audio: AudioChunk,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Transcribe complete audio with streaming results."""
        yield  # type: ignore[misc]

    @abstractmethod
    async def transcribe_realtime(
        self,
        audio_stream: AsyncGenerator[AudioChunk, None],
        language: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Real-time transcription of ongoing speech."""
        yield  # type: ignore[misc]

    @abstractmethod
    async def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes."""
        pass


class TextToSpeechClient(ABC):
    """Interface for converting text to speech."""

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        language: Optional[str] = None,
    ) -> bytes:
        """Convert text to audio (batch mode)."""
        pass

    @abstractmethod
    async def synthesize_stream(
        self,
        text: str,
        voice_id: Optional[str] = None,
        language: Optional[str] = None,
    ) -> AsyncGenerator[bytes, None]:
        """Convert text to audio with streaming output."""
        yield  # type: ignore[misc]

    @abstractmethod
    async def get_available_voices(self) -> List[str]:
        """Get list of available voice IDs."""
        pass
