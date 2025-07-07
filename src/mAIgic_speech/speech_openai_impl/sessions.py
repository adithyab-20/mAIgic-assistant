"""OpenAI Realtime API session implementations.

This module contains internal session implementations for OpenAI's Realtime API.
Users should use the client methods instead of these classes directly.

Example:
    # Use this (recommended)
    async for event in client.transcribe_realtime(audio_source, config):
        print(event.text)

    # Don't use sessions directly
    session = await client.create_realtime_session(config)
    async with session:
        # ... session management code
"""

import asyncio
import base64
import json
import logging
import time
from dataclasses import dataclass
from types import TracebackType
from typing import Any, AsyncGenerator, Dict, Optional

import websockets

from mAIgic_speech.speech_api import (
    RealtimeSessionError,
    RealtimeTranscriptionError,
    RealtimeTranscriptionSession,
    SessionClosedError,
    SessionConnectionError,
    SpeechEvent,
    TranscriptionEvent,
)

from .config import OpenAIConfig

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class RealtimeEvent:
    """Represents a realtime API event."""
    type: str
    data: Dict[str, Any]
    timestamp: Optional[float] = None


class OpenAIRealtimeTranscriptionSession(RealtimeTranscriptionSession):
    """OpenAI implementation of realtime transcription session."""

    def __init__(self, websocket: Any, config: OpenAIConfig, model: str = "gpt-4o-transcribe") -> None:
        self.websocket = websocket
        self.config = config
        self.model = model
        self._closed = False
        self._websocket_lock = asyncio.Lock()
        self._message_queue: asyncio.Queue[Optional[str]] = asyncio.Queue()
        self._receiver_task: Optional[asyncio.Task[None]] = None

    async def __aenter__(self) -> "OpenAIRealtimeTranscriptionSession":
        """Async context manager entry."""
        # Start the message receiver
        self._receiver_task = asyncio.create_task(self._receive_messages())
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        """Async context manager exit."""
        await self.close()

    async def _receive_messages(self) -> None:
        """Background task to receive all messages from websocket."""
        try:
            async for message in self.websocket:
                if self._closed:
                    break
                await self._message_queue.put(message)
        except Exception as conn_error:
            # Handle WebSocket connection errors (compatible with different websockets versions)
            if "connection" in str(conn_error).lower() and "closed" in str(conn_error).lower():
                logger.info("WebSocket connection closed by server")
                self._closed = True
            else:
                logger.error(f"WebSocket error: {conn_error}")
                self._closed = True
        finally:
            # Signal end of messages
            await self._message_queue.put(None)

    async def send_audio(self, audio_data: bytes) -> None:
        """Send audio data to the transcription session."""
        if self._closed:
            raise SessionClosedError("Session is closed")

        message = {
            "type": "input_audio_buffer.append",
            "audio": base64.b64encode(audio_data).decode('utf-8')
        }

        async with self._websocket_lock:
            try:
                await self.websocket.send(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send audio: {e}")
                raise SessionClosedError(f"Failed to send audio: {e}") from e

    async def receive_transcriptions(self) -> AsyncGenerator[TranscriptionEvent, None]:
        """Receive transcription events from the session."""
        try:
            while not self._closed:
                message = await self._message_queue.get()
                if message is None:  # Sentinel value for shutdown
                    break

                try:
                    data = json.loads(message)
                    event_type = data.get("type")

                    if event_type == "conversation.item.input_audio_transcription.delta":
                        # Handle streaming transcription deltas
                        delta_text = data.get("delta", "")
                        if delta_text:
                            yield TranscriptionEvent(
                                text=delta_text,
                                is_final=False,  # Delta events are partial
                                timestamp=time.time()
                            )
                    elif event_type == "conversation.item.input_audio_transcription.completed":
                        # Handle completed transcription
                        transcript = data.get("transcript", "")
                        yield TranscriptionEvent(
                            text=transcript,
                            is_final=True,
                            timestamp=time.time()
                        )
                    elif event_type == "conversation.item.input_audio_transcription.failed":
                        # Handle failed transcription
                        yield TranscriptionEvent(
                            text="",
                            is_final=True,
                            timestamp=time.time()
                        )
                    elif event_type == "error":
                        # Handle API errors
                        error_message = data.get("error", {}).get("message", "Unknown error")
                        error_type = data.get("error", {}).get("type", "unknown_error")
                        logger.error(f"API Error: {error_type} - {error_message}")
                        raise RealtimeSessionError(f"API Error: {error_type} - {error_message}")
                    elif event_type in ["transcription_session.created", "transcription_session.updated"]:
                        # Ignore session management events
                        continue
                    else:
                        # Handle other event types if needed
                        logger.debug(f"Unhandled event type: {event_type}")
                        continue

                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse message: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error processing transcription event: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error in receive_transcriptions: {e}")
            raise RealtimeSessionError(f"Failed to receive transcriptions: {e}") from e

    async def receive_speech_events(self) -> AsyncGenerator[SpeechEvent, None]:
        """Receive speech activity detection events."""
        if self._closed:
            raise SessionClosedError("Session is closed")

        try:
            while not self._closed:
                message = await self._message_queue.get()
                if message is None:  # End of messages
                    break

                try:
                    data = json.loads(message)
                    timestamp = time.time()

                    event_type = data.get("type")
                    if event_type == "input_audio_buffer.speech_started":
                        yield SpeechEvent(
                            type="started",
                            timestamp=timestamp,
                            metadata=data
                        )
                    elif event_type == "input_audio_buffer.speech_stopped":
                        yield SpeechEvent(
                            type="stopped",
                            timestamp=timestamp,
                            metadata=data
                        )
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse WebSocket message: {e}")
                    continue

        except Exception as e:
            self._closed = True
            logger.error(f"Error in speech event stream: {e}")
            raise RealtimeTranscriptionError(f"Error in speech event stream: {e}")

    async def close(self) -> None:
        """Close the session and clean up resources."""
        if self._closed:
            return  # Already closed, make it idempotent

        self._closed = True

        # Cancel the receiver task
        if self._receiver_task and not self._receiver_task.done():
            self._receiver_task.cancel()
            try:
                await self._receiver_task
            except asyncio.CancelledError:
                pass

        # Close WebSocket connection
        try:
            await self.websocket.close()
        except Exception as e:
            logger.warning(f"Error closing WebSocket: {e}")
            pass

    @property
    def is_closed(self) -> bool:
        """Check if the session is closed."""
        if self._closed:
            return True

        # For WebSocket objects, we'll assume they're open unless we know otherwise
        # The _closed flag will be set to True if we get connection errors
        return False

    async def configure_transcription(self, model: str) -> None:
        """Configure the transcription session."""
        if self._closed:
            raise SessionClosedError("Session is closed")

        message = {
            "type": "transcription_session.update",
            "session": {
                "input_audio_format": "pcm16",
                "input_audio_transcription": {
                    "model": model,
                    "prompt": "",
                    "language": "en"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.3,

                    "prefix_padding_ms": 500,
                    "silence_duration_ms": 700
                },
                "input_audio_noise_reduction": {
                    "type": "near_field"
                }
            }
        }

        async with self._websocket_lock:
            try:
                await self.websocket.send(json.dumps(message))
                logger.info(f"Configured transcription with model: {model}")
            except Exception as e:
                if "connection" in str(e).lower() and "closed" in str(e).lower():
                    self._closed = True
                    raise SessionConnectionError("WebSocket connection closed")
                else:
                    logger.error(f"Error configuring transcription: {e}")
                    raise RealtimeTranscriptionError(f"Error configuring transcription: {e}")


class RealtimeSpeechToSpeechSession:
    """OpenAI realtime speech-to-speech session."""

    def __init__(self, websocket: Any, config: OpenAIConfig) -> None:
        self.websocket = websocket
        self.config = config
        self._closed = False

    async def __aenter__(self) -> "RealtimeSpeechToSpeechSession":
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

    async def send_audio(self, audio_data: bytes) -> None:
        """Send audio data to the session."""
        if self._closed:
            raise SessionClosedError("Session is closed")

        message = {
            "type": "input_audio_buffer.append",
            "audio": base64.b64encode(audio_data).decode('utf-8')
        }

        try:
            await self.websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send audio: {e}")
            raise SessionClosedError(f"Failed to send audio: {e}") from e

    async def send_text(self, text: str) -> None:
        """Send text message to the session."""
        if self._closed:
            raise SessionClosedError("Session is closed")

        # First, create a conversation item
        conversation_message = {
            "type": "conversation.item.create",
            "item": {
                "content": [
                    {
                        "type": "text",
                        "text": text
                    }
                ]
            }
        }

        # Then, create a response
        response_message = {
            "type": "response.create"
        }

        try:
            await self.websocket.send(json.dumps(conversation_message))
            await self.websocket.send(json.dumps(response_message))
        except Exception as e:
            logger.error(f"Failed to send text: {e}")
            raise SessionClosedError(f"Failed to send text: {e}") from e

    async def receive_events(self) -> AsyncGenerator[RealtimeEvent, None]:
        """Receive events from the session."""
        if self._closed:
            raise SessionClosedError("Session is closed")

        try:
            async for message in self.websocket:
                if self._closed:
                    break

                try:
                    data = json.loads(message)
                    event_type = data.get("type", "unknown")

                    yield RealtimeEvent(
                        type=event_type,
                        data=data,
                        timestamp=time.time()
                    )

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse WebSocket message: {e}")
                    continue

        except Exception as e:
            self._closed = True
            logger.error(f"Error receiving events: {e}")
            raise RealtimeSessionError(f"Error receiving events: {e}") from e

    async def close(self) -> None:
        """Close the session and clean up resources."""
        if self._closed:
            return  # Already closed, make it idempotent

        self._closed = True

        # Close WebSocket connection
        try:
            await self.websocket.close()
        except Exception as e:
            logger.warning(f"Error closing WebSocket: {e}")


class OpenAIRealtimeClient:
    """Client for OpenAI's Realtime API."""

    def __init__(self, config: OpenAIConfig) -> None:
        self.config = config

    async def connect_transcription(
        self,
        model: str = "gpt-4o-transcribe"
    ) -> OpenAIRealtimeTranscriptionSession:
        """Connect to OpenAI's realtime transcription service."""
        try:
            # Build the WebSocket URL for transcription intent
            url = f"{self.config.base_url.replace('https://', 'wss://')}/realtime?intent=transcription"

            # Prepare headers
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "OpenAI-Beta": "realtime=v1"
            }

            if self.config.organization:
                headers["OpenAI-Organization"] = self.config.organization

            # Connect to WebSocket
            websocket = await websockets.connect(
                url,
                additional_headers=headers,
                ping_interval=None,  # Disable ping/pong for OpenAI's API
                ping_timeout=None
            )

            # Create session
            session = OpenAIRealtimeTranscriptionSession(websocket, self.config, model)

            # Configure the session
            await session.configure_transcription(model)

            # Send a short silent audio chunk to "warm up" the stream
            try:
                await websocket.send(json.dumps({
                    "type": "input_audio_buffer.append",
                    "audio": base64.b64encode(b'\x00' * 3200).decode('utf-8')
                }))
            except Exception:
                pass  # Ignore if connection is already closed

            return session

        except Exception as e:
            raise SessionConnectionError(f"Failed to connect to transcription service: {e}") from e

    async def connect_speech_to_speech(
        self,
        model: str = "gpt-4o-realtime-preview-2025-06-03",
        voice: str = "alloy",
        system_prompt: Optional[str] = None
    ) -> RealtimeSpeechToSpeechSession:
        """Connect to OpenAI's realtime speech-to-speech service."""
        try:
            # Build the WebSocket URL with parameters
            url = f"{self.config.base_url.replace('https://', 'wss://')}/realtime"
            url += f"?model={model}&voice={voice}"

            if system_prompt:
                url += f"&system_prompt={system_prompt}"

            # Prepare headers
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "OpenAI-Beta": "realtime=v1"
            }

            if self.config.organization:
                headers["OpenAI-Organization"] = self.config.organization

            # Connect to WebSocket
            websocket = await websockets.connect(
                url,
                additional_headers=headers,
                ping_interval=None,
                ping_timeout=None
            )

            return RealtimeSpeechToSpeechSession(websocket, self.config)

        except Exception as e:
            raise SessionConnectionError(f"Failed to connect to speech-to-speech service: {e}") from e


# Type alias for backward compatibility - removed to avoid assignment issues
# RealtimeTranscriptionSession = OpenAIRealtimeTranscriptionSession
