"""Tests for OpenAI realtime session implementations."""

import asyncio
import json
from typing import Any, List
from unittest.mock import AsyncMock, patch

import pytest

from speech_api import (
    SessionClosedError,
    SessionConnectionError,
)
from speech_openai_impl.config import OpenAIConfig
from speech_openai_impl.sessions import (
    OpenAIRealtimeClient,
    OpenAIRealtimeTranscriptionSession,
    RealtimeSpeechToSpeechSession,
)


class MockAsyncGenerator:
    """A proper async generator mock that handles cleanup correctly."""

    def __init__(self, items: List[str]) -> None:
        self.items = items
        self.index = 0

    def __aiter__(self) -> "MockAsyncGenerator":
        return self

    async def __anext__(self) -> str:
        if self.index >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self.index]
        self.index += 1
        return item

    async def aclose(self) -> None:
        """Properly handle async generator cleanup."""
        pass

    async def athrow(self, exc_type: type, exc_val: Exception | None = None, exc_tb: Any = None) -> None:
        """Handle exceptions thrown into the generator."""
        if exc_val is None:
            exc_val = exc_type()
        raise exc_val


class TestOpenAIRealtimeTranscriptionSession:
    """Test cases for OpenAIRealtimeTranscriptionSession."""

    @pytest.fixture
    def mock_websocket(self) -> AsyncMock:
        """Create a mock WebSocket for testing."""
        websocket = AsyncMock()
        websocket.send = AsyncMock()
        websocket.close = AsyncMock()
        return websocket

    @pytest.fixture
    def config(self) -> OpenAIConfig:
        """Create a test configuration."""
        return OpenAIConfig(api_key="test-key")

    def test_init(self, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test session initialization."""
        session = OpenAIRealtimeTranscriptionSession(mock_websocket, config)

        assert session.websocket == mock_websocket
        assert session.config == config
        assert session.model == "gpt-4o-transcribe"
        assert session._closed is False
        assert session._receiver_task is None

    def test_init_with_custom_model(self, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test session initialization with custom model."""
        session = OpenAIRealtimeTranscriptionSession(
            mock_websocket, config, model="custom-model"
        )

        assert session.model == "custom-model"

    async def test_context_manager_start_and_stop(self, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test async context manager functionality."""
        # Use proper MockAsyncGenerator
        mock_messages = ['{"type": "test"}']
        mock_websocket.__aiter__ = lambda *args: MockAsyncGenerator(mock_messages)

        session = OpenAIRealtimeTranscriptionSession(mock_websocket, config)

        async with session:
            assert session._receiver_task is not None
            assert not session._receiver_task.done()

        # Should be closed after context exit
        assert session._closed is True

    async def test_send_audio_success(self, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test successfully sending audio data."""
        session = OpenAIRealtimeTranscriptionSession(mock_websocket, config)

        audio_data = b"test_audio_data"
        await session.send_audio(audio_data)

        # Verify the correct message was sent
        mock_websocket.send.assert_called_once()
        sent_message = mock_websocket.send.call_args[0][0]
        parsed_message = json.loads(sent_message)

        assert parsed_message["type"] == "input_audio_buffer.append"
        assert "audio" in parsed_message

    async def test_send_audio_when_closed_raises_error(self, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test that sending audio when closed raises SessionClosedError."""
        session = OpenAIRealtimeTranscriptionSession(mock_websocket, config)
        session._closed = True

        with pytest.raises(SessionClosedError, match="Session is closed"):
            await session.send_audio(b"test_data")

    async def test_send_audio_websocket_error_raises_session_closed(self, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test that WebSocket errors during send raise SessionClosedError."""
        session = OpenAIRealtimeTranscriptionSession(mock_websocket, config)
        mock_websocket.send.side_effect = Exception("WebSocket error")

        with pytest.raises(SessionClosedError, match="Failed to send audio"):
            await session.send_audio(b"test_data")

    async def test_receive_transcriptions_completed_event(self, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test receiving completed transcription events."""
        session = OpenAIRealtimeTranscriptionSession(mock_websocket, config)

        # Mock message queue with transcription event
        transcription_event = {
            "type": "conversation.item.input_audio_transcription.completed",
            "transcript": "Hello world"
        }

        await session._message_queue.put(json.dumps(transcription_event))
        await session._message_queue.put(None)  # End signal

        events = []
        async for event in session.receive_transcriptions():
            events.append(event)

        assert len(events) == 1
        assert events[0].text == "Hello world"
        assert events[0].is_final is True

    async def test_receive_transcriptions_failed_event(self, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test receiving failed transcription events."""
        session = OpenAIRealtimeTranscriptionSession(mock_websocket, config)

        # Mock message queue with failed event
        failed_event = {
            "type": "conversation.item.input_audio_transcription.failed"
        }

        await session._message_queue.put(json.dumps(failed_event))
        await session._message_queue.put(None)  # End signal

        events = []
        async for event in session.receive_transcriptions():
            events.append(event)

        assert len(events) == 1
        assert events[0].text == ""
        assert events[0].is_final is True  # Failed events are final

    async def test_receive_transcriptions_ignores_session_events(self, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test that session management events are ignored."""
        session = OpenAIRealtimeTranscriptionSession(mock_websocket, config)

        # Mock message queue with session events
        session_event = {
            "type": "transcription_session.created"
        }

        await session._message_queue.put(json.dumps(session_event))
        await session._message_queue.put(None)  # End signal

        events = []
        async for event in session.receive_transcriptions():
            events.append(event)

        # Should ignore session events
        assert len(events) == 0

    async def test_receive_transcriptions_handles_invalid_json(self, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test that invalid JSON messages are handled gracefully."""
        session = OpenAIRealtimeTranscriptionSession(mock_websocket, config)

        # Mock message queue with invalid JSON
        await session._message_queue.put("invalid json")
        await session._message_queue.put(None)  # End signal

        events = []
        async for event in session.receive_transcriptions():
            events.append(event)

        # Should handle invalid JSON gracefully
        assert len(events) == 0

    async def test_receive_speech_events_started(self, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test receiving speech started events."""
        session = OpenAIRealtimeTranscriptionSession(mock_websocket, config)

        # Mock message queue with speech started event
        speech_event = {
            "type": "input_audio_buffer.speech_started"
        }

        await session._message_queue.put(json.dumps(speech_event))
        await session._message_queue.put(None)  # End signal

        events = []
        async for event in session.receive_speech_events():
            events.append(event)

        assert len(events) == 1
        assert events[0].type == "started"

    async def test_receive_speech_events_stopped(self, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test receiving speech stopped events."""
        session = OpenAIRealtimeTranscriptionSession(mock_websocket, config)

        # Mock message queue with speech stopped event
        speech_event = {
            "type": "input_audio_buffer.speech_stopped"
        }

        await session._message_queue.put(json.dumps(speech_event))
        await session._message_queue.put(None)  # End signal

        events = []
        async for event in session.receive_speech_events():
            events.append(event)

        assert len(events) == 1
        assert events[0].type == "stopped"

    async def test_receive_speech_events_when_closed_raises_error(self, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test that receiving speech events when closed raises error."""
        session = OpenAIRealtimeTranscriptionSession(mock_websocket, config)
        session._closed = True

        with pytest.raises(SessionClosedError, match="Session is closed"):
            async for _ in session.receive_speech_events():
                pass

    async def test_close_idempotent(self, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test that close is idempotent."""
        session = OpenAIRealtimeTranscriptionSession(mock_websocket, config)

        # Close multiple times should be safe
        await session.close()
        await session.close()

        assert session._closed is True

    async def test_close_cancels_receiver_task(self, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test that close cancels the receiver task."""
        # Create a mock async generator that will simulate a long-running operation
        class LongRunningAsyncGenerator:
            def __aiter__(self) -> "LongRunningAsyncGenerator":
                return self

            async def __anext__(self) -> str:
                await asyncio.sleep(10)  # Long-running task
                return ""

            async def aclose(self) -> None:
                pass  # Proper cleanup

        mock_websocket.__aiter__ = lambda *args: LongRunningAsyncGenerator()

        session = OpenAIRealtimeTranscriptionSession(mock_websocket, config)

        # Start the session to create receiver task
        async with session:
            receiver_task = session._receiver_task
            assert receiver_task is not None

        # Task should be cancelled after close
        assert receiver_task.cancelled()

    def test_is_closed_property(self, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test the is_closed property."""
        session = OpenAIRealtimeTranscriptionSession(mock_websocket, config)

        assert session.is_closed is False

        session._closed = True
        assert session.is_closed is True

    @patch('speech_openai_impl.sessions.logger')
    async def test_configure_transcription(self, mock_logger: Any, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test configuring transcription model."""
        session = OpenAIRealtimeTranscriptionSession(mock_websocket, config)

        await session.configure_transcription("new-model")

        # Should send configuration message
        mock_websocket.send.assert_called_once()
        sent_message = mock_websocket.send.call_args[0][0]
        parsed_message = json.loads(sent_message)

        assert parsed_message["type"] == "transcription_session.update"
        assert parsed_message["session"]["input_audio_transcription"]["model"] == "new-model"
        assert "turn_detection" in parsed_message["session"]
        mock_logger.info.assert_called_once_with("Configured transcription with model: new-model")


class TestRealtimeSpeechToSpeechSession:
    """Test cases for RealtimeSpeechToSpeechSession."""

    @pytest.fixture
    def mock_websocket(self) -> AsyncMock:
        """Create a mock WebSocket for testing."""
        websocket = AsyncMock()
        websocket.send = AsyncMock()
        websocket.close = AsyncMock()
        return websocket

    @pytest.fixture
    def config(self) -> OpenAIConfig:
        """Create a test configuration."""
        return OpenAIConfig(api_key="test-key")

    def test_init(self, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test session initialization."""
        session = RealtimeSpeechToSpeechSession(mock_websocket, config)

        assert session.websocket == mock_websocket
        assert session.config == config
        assert session._closed is False

    async def test_context_manager(self, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test async context manager functionality."""
        session = RealtimeSpeechToSpeechSession(mock_websocket, config)

        async with session:
            assert not session._closed

        # Should be closed after context exit
        assert session._closed

    async def test_send_audio_success(self, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test successfully sending audio data."""
        session = RealtimeSpeechToSpeechSession(mock_websocket, config)

        audio_data = b"test_audio_data"
        await session.send_audio(audio_data)

        # Verify the correct message was sent
        mock_websocket.send.assert_called_once()
        sent_message = mock_websocket.send.call_args[0][0]
        parsed_message = json.loads(sent_message)

        assert parsed_message["type"] == "input_audio_buffer.append"
        assert "audio" in parsed_message

    async def test_send_text_success(self, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test successfully sending text."""
        session = RealtimeSpeechToSpeechSession(mock_websocket, config)

        await session.send_text("Hello world")

        # Should send two messages: create conversation item and create response
        assert mock_websocket.send.call_count == 2

        # Check first message (conversation item)
        first_message = json.loads(mock_websocket.send.call_args_list[0][0][0])
        assert first_message["type"] == "conversation.item.create"
        assert first_message["item"]["content"][0]["text"] == "Hello world"

        # Check second message (create response)
        second_message = json.loads(mock_websocket.send.call_args_list[1][0][0])
        assert second_message["type"] == "response.create"

    async def test_receive_events_audio_transcript(self, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test receiving audio transcript events."""
        session = RealtimeSpeechToSpeechSession(mock_websocket, config)

        # Mock websocket messages
        transcript_event = {
            "type": "response.audio_transcript.delta",
            "delta": "Hello"
        }

        # Use the proper MockAsyncGenerator
        mock_messages = [json.dumps(transcript_event)]
        mock_websocket.__aiter__ = lambda *args: MockAsyncGenerator(mock_messages)

        events = []
        async for event in session.receive_events():
            events.append(event)
            break  # Exit after first event

        assert len(events) == 1
        assert events[0].type == "response.audio_transcript.delta"

    async def test_close_websocket(self, mock_websocket: AsyncMock, config: OpenAIConfig) -> None:
        """Test closing the WebSocket connection."""
        session = RealtimeSpeechToSpeechSession(mock_websocket, config)

        await session.close()

        assert session._closed is True
        mock_websocket.close.assert_called_once()


class TestOpenAIRealtimeClient:
    """Test cases for OpenAIRealtimeClient."""

    @pytest.fixture
    def config(self) -> OpenAIConfig:
        """Create a test configuration."""
        return OpenAIConfig(api_key="test-key")

    def test_init(self, config: OpenAIConfig) -> None:
        """Test client initialization."""
        client = OpenAIRealtimeClient(config)

        assert client.config == config

    @patch('websockets.connect')
    async def test_connect_transcription_success(self, mock_connect: Any, config: OpenAIConfig) -> None:
        """Test successful transcription connection."""
        # Mock WebSocket
        mock_websocket = AsyncMock()
        # Make websockets.connect properly awaitable
        async def async_connect(*args: Any, **kwargs: Any) -> AsyncMock:
            return mock_websocket
        mock_connect.side_effect = async_connect

        client = OpenAIRealtimeClient(config)
        session = await client.connect_transcription()

        assert isinstance(session, OpenAIRealtimeTranscriptionSession)
        assert session.websocket == mock_websocket
        assert session.model == "gpt-4o-transcribe"

        # Verify connection parameters
        mock_connect.assert_called_once()
        call_args = mock_connect.call_args

        # Check URL
        assert "wss://api.openai.com/v1/realtime" in call_args[0][0]

        # Check headers
        headers = call_args[1]["additional_headers"]
        assert headers["Authorization"] == "Bearer test-key"
        assert headers["OpenAI-Beta"] == "realtime=v1"

    @patch('websockets.connect')
    async def test_connect_transcription_with_custom_model(self, mock_connect: Any, config: OpenAIConfig) -> None:
        """Test transcription connection with custom model."""
        mock_websocket = AsyncMock()
        async def async_connect(*args: Any, **kwargs: Any) -> AsyncMock:
            return mock_websocket
        mock_connect.side_effect = async_connect

        client = OpenAIRealtimeClient(config)
        session = await client.connect_transcription(model="custom-model")

        assert session.model == "custom-model"

    @patch('websockets.connect')
    async def test_connect_transcription_connection_error(self, mock_connect: Any, config: OpenAIConfig) -> None:
        """Test handling of connection errors in transcription."""
        mock_connect.side_effect = ConnectionError("Mocked connection error")

        client = OpenAIRealtimeClient(config)

        with pytest.raises(SessionConnectionError, match="Failed to connect"):
            await client.connect_transcription()

    @patch('websockets.connect')
    async def test_connect_speech_to_speech_success(self, mock_connect: Any, config: OpenAIConfig) -> None:
        """Test successful speech-to-speech connection."""
        # Mock WebSocket
        mock_websocket = AsyncMock()
        async def async_connect(*args: Any, **kwargs: Any) -> AsyncMock:
            return mock_websocket
        mock_connect.side_effect = async_connect

        client = OpenAIRealtimeClient(config)
        session = await client.connect_speech_to_speech()

        assert isinstance(session, RealtimeSpeechToSpeechSession)
        assert session.websocket == mock_websocket

        # Verify connection parameters
        mock_connect.assert_called_once()
        call_args = mock_connect.call_args

        # Check URL
        assert "wss://api.openai.com/v1/realtime" in call_args[0][0]

    @patch('websockets.connect')
    async def test_connect_speech_to_speech_with_parameters(self, mock_connect: Any, config: OpenAIConfig) -> None:
        """Test speech-to-speech connection with custom parameters."""
        mock_websocket = AsyncMock()
        async def async_connect(*args: Any, **kwargs: Any) -> AsyncMock:
            return mock_websocket
        mock_connect.side_effect = async_connect

        client = OpenAIRealtimeClient(config)
        session = await client.connect_speech_to_speech(
            voice="alloy",
            model="gpt-4o"
        )

        assert isinstance(session, RealtimeSpeechToSpeechSession)

        # Verify connection parameters include custom settings
        mock_connect.assert_called_once()
        call_args = mock_connect.call_args
        url = call_args[0][0]

        assert "voice=alloy" in url
        assert "model=gpt-4o" in url

    @patch('websockets.connect')
    async def test_connect_speech_to_speech_connection_error(self, mock_connect: Any, config: OpenAIConfig) -> None:
        """Test handling of connection errors in speech-to-speech."""
        mock_connect.side_effect = Exception("Connection failed")

        client = OpenAIRealtimeClient(config)

        with pytest.raises(SessionConnectionError, match="Failed to connect"):
            await client.connect_speech_to_speech()
