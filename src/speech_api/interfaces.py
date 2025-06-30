"""Core interfaces for speech processing APIs.

This module defines the core interfaces for speech-to-text and text-to-speech
functionality, providing a clean abstraction layer for different providers.
"""

import asyncio
from abc import ABC, abstractmethod
from types import TracebackType
from typing import AsyncGenerator, List, Optional

from .types import AudioChunk, RealtimeSessionConfig, SpeechEvent, TranscriptionEvent


class AudioSource(ABC):
    """Interface for audio input sources.

    Provides a clean abstraction for different audio input methods:
    - Microphone capture
    - File streaming
    - Network audio streams
    - Test/mock audio sources
    """

    @abstractmethod
    async def start(self) -> None:
        """Start the audio source.

        Raises:
            AudioSourceError: If unable to start audio capture
        """
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the audio source and clean up resources.

        This method is idempotent - calling it multiple times is safe.
        """
        pass

    @abstractmethod
    async def read_chunk(self) -> Optional[bytes]:
        """Read the next audio chunk.

        Returns:
            Optional[bytes]: Audio data chunk, or None if no data available

        Raises:
            AudioSourceError: If error occurs during audio capture
        """
        pass

    @property
    @abstractmethod
    def sample_rate(self) -> int:
        """Get the audio sample rate in Hz."""
        pass

    @property
    @abstractmethod
    def channels(self) -> int:
        """Get the number of audio channels."""
        pass

    @property
    @abstractmethod
    def is_active(self) -> bool:
        """Check if the audio source is currently active."""
        pass

    async def __aenter__(self) -> "AudioSource":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        """Async context manager exit."""
        await self.stop()


class StreamingAudioSource(AudioSource):
    """Extended interface for streaming audio sources with async iteration."""

    def __aiter__(self) -> AsyncGenerator[bytes, None]:
        """Async iterator support for streaming audio."""
        return self._stream_chunks()

    async def _stream_chunks(self) -> AsyncGenerator[bytes, None]:
        """Stream audio chunks asynchronously."""
        while self.is_active:
            chunk = await self.read_chunk()
            if chunk:
                yield chunk
            else:
                # Small delay to avoid busy waiting
                await asyncio.sleep(0.01)


class RealtimeTranscriptionSession(ABC):
    """Interface for realtime transcription sessions.

    This interface provides an abstraction for realtime speech transcription
    across different providers. It supports:
    - Audio streaming to the transcription service
    - Receiving transcription events (partial and final)
    - Speech activity detection events
    - Proper resource management via context manager
    """

    @abstractmethod
    async def send_audio(self, audio_data: bytes) -> None:
        """Send audio chunk to the transcription session.

        Args:
            audio_data: Raw audio bytes (typically PCM16, 16kHz, mono)

        Raises:
            SessionClosedError: If the session is already closed
            SessionConnectionError: If connection to service is lost
            RealtimeTranscriptionError: For other transcription errors
        """
        pass

    @abstractmethod
    async def receive_transcriptions(self) -> AsyncGenerator[TranscriptionEvent, None]:
        """Receive transcription events from the session.

        Yields:
            TranscriptionEvent: Events containing transcribed text with metadata

        Raises:
            SessionClosedError: If the session is closed
            RealtimeTranscriptionError: For transcription processing errors
        """
        yield  # type: ignore[misc]

    @abstractmethod
    async def receive_speech_events(self) -> AsyncGenerator[SpeechEvent, None]:
        """Receive speech activity detection events.

        Yields:
            SpeechEvent: Events indicating speech start/stop detection

        Raises:
            SessionClosedError: If the session is closed
            RealtimeTranscriptionError: For speech detection errors
        """
        yield  # type: ignore[misc]

    @abstractmethod
    async def close(self) -> None:
        """Close the session and clean up resources.

        This method is idempotent - calling it multiple times is safe.
        """
        pass

    @property
    @abstractmethod
    def is_closed(self) -> bool:
        """Check if the session is closed.

        Returns:
            bool: True if session is closed, False otherwise
        """
        pass

    async def __aenter__(self) -> "RealtimeTranscriptionSession":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        """Async context manager exit."""
        await self.close()


class SpeechToTextClient(ABC):
    """Interface for converting speech to text.

    Supports multiple modes:
    - Batch transcription (complete audio files)
    - Streaming transcription (chunks with streaming results)
    - Realtime transcription (live audio sessions)
    """

    @abstractmethod
    async def transcribe(
        self,
        audio: AudioChunk,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> str:
        """Transcribe complete audio to text (batch mode).

        Args:
            audio: Audio chunk to transcribe
            language: Language code (e.g., 'en', 'es') for better accuracy
            prompt: Context prompt to improve transcription accuracy

        Returns:
            str: Transcribed text

        Raises:
            TranscriptionError: If transcription fails
            APIError: If API request fails
        """
        pass

    @abstractmethod
    async def transcribe_stream(
        self,
        audio: AudioChunk,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Transcribe complete audio with streaming results.

        Args:
            audio: Audio chunk to transcribe
            language: Language code for better accuracy
            prompt: Context prompt to improve transcription accuracy

        Yields:
            str: Partial transcription results as they become available

        Raises:
            TranscriptionError: If transcription fails
            APIError: If API request fails
        """
        yield  # type: ignore[misc]

    @abstractmethod
    async def transcribe_realtime(
        self,
        audio_source: AudioSource,
        config: RealtimeSessionConfig,
    ) -> AsyncGenerator[TranscriptionEvent, None]:
        """Transcribe audio in real-time.

        This method provides a clean way to perform realtime transcription
        regardless of the underlying provider implementation.

        Args:
            audio_source: Audio source to transcribe from
            config: Configuration for the realtime session

        Yields:
            TranscriptionEvent: Real-time transcription events with metadata

        Raises:
            TranscriptionError: If transcription fails
            SessionConnectionError: If unable to connect to service
            RealtimeSessionError: For other session errors
        """
        yield  # type: ignore[misc]

    @abstractmethod
    async def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes.

        Returns:
            List[str]: Language codes (e.g., ['en', 'es', 'fr'])
        """
        pass


class TextToSpeechClient(ABC):
    """Interface for converting text to speech.

    Supports both batch and streaming synthesis modes.
    """

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        language: Optional[str] = None,
    ) -> bytes:
        """Convert text to audio (batch mode).

        Args:
            text: Text to convert to speech
            voice_id: Voice identifier for synthesis
            language: Language code for synthesis

        Returns:
            bytes: Audio data (format depends on implementation)

        Raises:
            SynthesisError: If synthesis fails
            APIError: If API request fails
        """
        pass

    @abstractmethod
    async def synthesize_stream(
        self,
        text: str,
        voice_id: Optional[str] = None,
        language: Optional[str] = None,
    ) -> AsyncGenerator[bytes, None]:
        """Convert text to audio with streaming output.

        Args:
            text: Text to convert to speech
            voice_id: Voice identifier for synthesis
            language: Language code for synthesis

        Yields:
            bytes: Audio chunks as they become available

        Raises:
            SynthesisError: If synthesis fails
            APIError: If API request fails
        """
        yield  # type: ignore[misc]

    @abstractmethod
    async def get_available_voices(self) -> List[str]:
        """Get list of available voice IDs.

        Returns:
            List[str]: Available voice identifiers
        """
        pass
