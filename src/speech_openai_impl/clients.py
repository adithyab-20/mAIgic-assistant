"""OpenAI client implementations for speech-to-text and text-to-speech APIs."""

import asyncio
import json
import logging
from types import TracebackType
from typing import AsyncGenerator, List, Optional

import aiohttp
from aiohttp import ClientSession

from speech_api.exceptions import (
    APIError,
    RealtimeSessionError,
    SessionConnectionError,
    SynthesisError,
    TranscriptionError,
)
from speech_api.interfaces import AudioSource, SpeechToTextClient, TextToSpeechClient
from speech_api.types import AudioChunk, RealtimeSessionConfig, TranscriptionEvent

from .config import OpenAIConfig
from .sessions import OpenAIRealtimeClient

# Set up logging
logger = logging.getLogger(__name__)


class OpenAISpeechToTextClient(SpeechToTextClient):
    """OpenAI Speech-to-Text client implementation."""

    def __init__(self, config: OpenAIConfig):
        if not config.api_key:
            raise ValueError("OpenAI API key is required")
        self.config = config
        self._session: Optional[ClientSession] = None
        self._realtime_client: Optional[OpenAIRealtimeClient] = None

    async def _get_session(self) -> ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self._session

    async def _get_realtime_client(self) -> OpenAIRealtimeClient:
        """Get or create realtime client."""
        if self._realtime_client is None:
            self._realtime_client = OpenAIRealtimeClient(self.config)
        return self._realtime_client

    async def close(self) -> None:
        """Close the client session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> "OpenAISpeechToTextClient":
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

    async def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return ["en"]  # English-only implementation

    async def transcribe(
        self,
        audio: AudioChunk,
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> str:
        """Transcribe audio to text."""
        if not audio.data:
            raise ValueError("Audio data cannot be empty")

        session = await self._get_session()

        try:
            # Prepare multipart form data
            data = aiohttp.FormData()
            data.add_field('model', 'gpt-4o-mini-transcribe')  # Use newer, higher quality model
            data.add_field('file', audio.data,
                          filename=f'audio.{audio.format.value}',
                          content_type=f'audio/{audio.format.value}')
            data.add_field('response_format', 'text')

            if language:
                data.add_field('language', language)
            if prompt:
                data.add_field('prompt', prompt)

            headers = {
                "Authorization": f"Bearer {self.config.api_key}"
            }

            async with session.post(
                "https://api.openai.com/v1/audio/transcriptions",
                data=data,
                headers=headers
            ) as response:
                if response.status == 401:
                    raise APIError("Invalid API key")
                elif response.status == 429:
                    raise APIError("Rate limit exceeded")
                elif response.status >= 400:
                    error_text = await response.text()
                    raise APIError(f"HTTP {response.status}: {error_text}")

                response.raise_for_status()
                result: str = await response.text()
                return result

        except aiohttp.ClientError as e:
            logger.error(f"Network error during transcription: {e}")
            raise TranscriptionError(f"Network error: {e}")
        except Exception as e:
            if isinstance(e, (APIError, TranscriptionError)):
                raise
            logger.error(f"Unexpected error during transcription: {e}")
            raise TranscriptionError(f"Transcription failed: {e}")

    async def transcribe_stream(
        self,
        audio: AudioChunk,
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Stream transcription results."""
        if not audio.data:
            raise ValueError("Audio data cannot be empty")

        session = await self._get_session()

        try:
            # Prepare multipart form data
            data = aiohttp.FormData()
            data.add_field('model', 'gpt-4o-mini-transcribe')  # Use streaming-capable model
            data.add_field('file', audio.data,
                          filename=f'audio.{audio.format.value}',
                          content_type=f'audio/{audio.format.value}')
            data.add_field('response_format', 'text')
            data.add_field('stream', 'true')  # Enable streaming

            if language:
                data.add_field('language', language)
            if prompt:
                data.add_field('prompt', prompt)

            headers = {
                "Authorization": f"Bearer {self.config.api_key}"
            }

            async with session.post(
                "https://api.openai.com/v1/audio/transcriptions",
                data=data,
                headers=headers
            ) as response:
                if response.status == 401:
                    raise APIError("Invalid API key")
                elif response.status == 429:
                    raise APIError("Rate limit exceeded")
                elif response.status >= 400:
                    error_text = await response.text()
                    raise APIError(f"HTTP {response.status}: {error_text}")

                response.raise_for_status()

                # Handle streaming response - Server-Sent Events format
                buffer = ""
                async for chunk in response.content.iter_any():
                    if chunk:
                        buffer += chunk.decode('utf-8')

                        # Process complete lines
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            line = line.strip()

                            if not line:
                                continue

                            # Handle Server-Sent Events format
                            if line.startswith('data: '):
                                data_content = line[6:]  # Remove 'data: ' prefix

                                # Skip special SSE messages
                                if data_content == '[DONE]':
                                    break

                                try:
                                    # Parse JSON event
                                    event_data = json.loads(data_content)

                                    # Extract text delta from transcript events
                                    if event_data.get('type') == 'transcript.text.delta':
                                        delta_text = event_data.get('delta', '')
                                        if delta_text:
                                            yield delta_text
                                    elif event_data.get('type') == 'transcript.text.done':
                                        # Final event indicates completion - don't yield to avoid duplication
                                        break

                                except json.JSONDecodeError:
                                    # If it's not JSON, it might be plain text
                                    if data_content.strip():
                                        yield data_content.strip()

                            # Handle plain text responses (fallback)
                            elif line and not line.startswith(':'):
                                yield line

        except aiohttp.ClientError as e:
            logger.error(f"Network error during streaming transcription: {e}")
            raise TranscriptionError(f"Network error: {e}")
        except Exception as e:
            if isinstance(e, (APIError, TranscriptionError)):
                raise
            logger.error(f"Unexpected error during streaming transcription: {e}")
            raise TranscriptionError(f"Streaming transcription failed: {e}")

    async def transcribe_realtime(
        self,
        audio_source: AudioSource,
        config: RealtimeSessionConfig,
    ) -> AsyncGenerator[TranscriptionEvent, None]:
        """Transcribe audio in real-time.

        This method provides a clean way to perform realtime transcription
        by combining audio source streaming with transcription session management.

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
        if not config.model:
            raise ValueError("Model is required in RealtimeSessionConfig")

        try:
            # Create realtime session
            realtime_client = await self._get_realtime_client()
            session = await realtime_client.connect_transcription(config.model)
            logger.info(f"Starting realtime transcription with model: {config.model}")

            async with session:
                async with audio_source:
                    # Create tasks for concurrent audio sending and event receiving
                    audio_task = None
                    event_task = None

                    try:
                        # Start event receiving task
                        event_queue: asyncio.Queue[Optional[TranscriptionEvent]] = asyncio.Queue()

                        async def event_receiver() -> None:
                            """Receive events from the realtime session."""
                            try:
                                async for event in session.receive_transcriptions():
                                    await event_queue.put(event)
                            except Exception as e:
                                logger.error(f"Error in event receiver: {e}")
                            finally:
                                await event_queue.put(None)  # Signal completion

                        event_task = asyncio.create_task(event_receiver())

                        # Start audio sending task
                        async def audio_sender() -> None:
                            """Send audio from the audio source to the session."""
                            try:
                                # Start the audio source
                                await audio_source.start()

                                try:
                                    # Send audio chunks
                                    while audio_source.is_active:
                                        chunk = await audio_source.read_chunk()
                                        if chunk is None:
                                            await asyncio.sleep(0.01)  # Small delay if no data
                                            continue
                                        await session.send_audio(chunk)
                                finally:
                                    await audio_source.stop()
                            except Exception as e:
                                logger.error(f"Error in audio sender: {e}")

                        audio_task = asyncio.create_task(audio_sender())

                        # Yield events as they arrive
                        while True:
                            event = await event_queue.get()
                            if event is None:  # End signal
                                break
                            yield event

                    finally:
                        # Clean up tasks
                        if audio_task:
                            audio_task.cancel()
                            try:
                                await audio_task
                            except asyncio.CancelledError:
                                pass

                        if event_task:
                            event_task.cancel()
                            try:
                                await event_task
                            except asyncio.CancelledError:
                                pass

        except Exception as e:
            logger.error(f"Error in realtime transcription: {e}")
            if isinstance(e, (TranscriptionError, SessionConnectionError, RealtimeSessionError)):
                raise
            raise TranscriptionError(f"Realtime transcription failed: {e}")


class OpenAITextToSpeechClient(TextToSpeechClient):
    """OpenAI Text-to-Speech client implementation."""

    def __init__(self, config: OpenAIConfig):
        if not config.api_key:
            raise ValueError("OpenAI API key is required")
        self.config = config
        self._session: Optional[ClientSession] = None

    async def _get_session(self) -> ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self._session

    async def close(self) -> None:
        """Close the client session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> "OpenAITextToSpeechClient":
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

    async def get_available_voices(self) -> List[str]:
        """Get list of available voices."""
        return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        language: Optional[str] = None
    ) -> bytes:
        """Synthesize text to speech."""
        if not text.strip():
            raise ValueError("Text cannot be empty")

        if voice_id is None:
            voice_id = "alloy"  # Default voice

        available_voices = await self.get_available_voices()
        if voice_id not in available_voices:
            raise ValueError(f"Voice '{voice_id}' not available. Available voices: {available_voices}")

        session = await self._get_session()

        try:
            data = {
                "model": "tts-1",
                "input": text,
                "voice": voice_id,
                "response_format": "mp3"
            }

            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }

            async with session.post(
                "https://api.openai.com/v1/audio/speech",
                json=data,
                headers=headers
            ) as response:
                if response.status == 401:
                    raise APIError("Invalid API key")
                elif response.status == 429:
                    raise APIError("Rate limit exceeded")
                elif response.status >= 400:
                    error_text = await response.text()
                    raise APIError(f"HTTP {response.status}: {error_text}")

                response.raise_for_status()
                result: bytes = await response.read()
                return result

        except aiohttp.ClientError as e:
            logger.error(f"Network error during synthesis: {e}")
            raise SynthesisError(f"Network error: {e}")
        except Exception as e:
            if isinstance(e, (APIError, SynthesisError)):
                raise
            logger.error(f"Unexpected error during synthesis: {e}")
            raise SynthesisError(f"Synthesis failed: {e}")

    async def synthesize_stream(
        self,
        text: str,
        voice_id: Optional[str] = None,
        language: Optional[str] = None
    ) -> AsyncGenerator[bytes, None]:
        """Stream synthesized speech."""
        # OpenAI TTS API doesn't support streaming yet
        # Return the full result as a single chunk
        result = await self.synthesize(text, voice_id, language)
        yield result
