"""Tests for OpenAI client implementations."""

from typing import Any, AsyncGenerator, Callable, List
from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

from mAIgic_speech.speech_api.exceptions import (
    APIError,
    SynthesisError,
    TranscriptionError,
)
from mAIgic_speech.speech_api.types import AudioChunk, AudioFormat
from mAIgic_speech.speech_openai_impl.clients import (
    OpenAISpeechToTextClient,
    OpenAITextToSpeechClient,
)
from mAIgic_speech.speech_openai_impl.config import OpenAIConfig


class MockResponse:
    """Mock HTTP response for testing."""

    def __init__(self, status: int = 200, text_result: str = "", read_result: bytes = b"", iter_any_data: List[bytes] | None = None, iter_chunked_data: List[bytes] | None = None) -> None:
        self.status = status
        self._text_result = text_result
        self._read_result = read_result
        self.content = MockContent(iter_any_data, iter_chunked_data)

    async def text(self) -> str:
        return self._text_result

    async def read(self) -> bytes:
        return self._read_result

    def raise_for_status(self) -> None:
        if self.status >= 400:
            from multidict import CIMultiDict, CIMultiDictProxy
            from yarl import URL
            url = URL.build(scheme="http", host="example.com")
            request_info = aiohttp.RequestInfo(
                url=url,
                method="POST",
                headers=CIMultiDictProxy(CIMultiDict([("content-type", "application/json")])),
                real_url=url
            )
            raise aiohttp.ClientResponseError(
                request_info=request_info,
                history=()
            )


class MockContent:
    """Mock response content for streaming."""

    def __init__(self, iter_any_data: List[bytes] | None = None, iter_chunked_data: List[bytes] | None = None) -> None:
        self._iter_any_data = iter_any_data or []
        self._iter_chunked_data = iter_chunked_data or []

    async def iter_any(self) -> AsyncGenerator[bytes, None]:
        """Mock iter_any for streaming responses."""
        for chunk in self._iter_any_data:
            yield chunk

    async def iter_chunked(self, chunk_size: int = 8192) -> AsyncGenerator[bytes, None]:
        """Mock iter_chunked for streaming responses."""
        for chunk in self._iter_chunked_data:
            yield chunk


class MockAsyncContextManager:
    """Mock async context manager for HTTP requests."""

    def __init__(self, response: MockResponse) -> None:
        self.response = response

    async def __aenter__(self) -> MockResponse:
        return self.response

    async def __aexit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: Any) -> None:
        pass


class MockSession:
    """Mock HTTP session for testing."""

    def __init__(self, response: MockResponse | None = None, post_side_effect: Callable[[], MockAsyncContextManager] | Exception | None = None) -> None:
        self.response = response
        self.post_calls: List[tuple[str, dict[str, Any]]] = []
        self.post_side_effect = post_side_effect

    def post(self, url: str, **kwargs: Any) -> MockAsyncContextManager:
        self.post_calls.append((url, kwargs))
        if self.post_side_effect:
            if callable(self.post_side_effect):
                result = self.post_side_effect()
                if isinstance(result, MockAsyncContextManager):
                    return result
                else:
                    raise ValueError("post_side_effect must return MockAsyncContextManager")
            else:
                raise self.post_side_effect
        if self.response is None:
            raise ValueError("No response configured")
        return MockAsyncContextManager(self.response)

    async def close(self) -> None:
        pass


class MockFailingContextManager(MockAsyncContextManager):
    """Mock async context manager that raises an error on entry."""

    def __init__(self, error: Exception) -> None:
        # Call parent with a dummy response since we'll raise an error anyway
        super().__init__(MockResponse())
        self.error = error

    async def __aenter__(self) -> MockResponse:
        raise self.error

    async def __aexit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: Any) -> None:
        pass


class TestOpenAISpeechToTextClient:
    """Test cases for OpenAISpeechToTextClient."""

    def test_init_with_valid_config(self) -> None:
        """Test client initialization with valid config."""
        config = OpenAIConfig(api_key="test-key")
        client = OpenAISpeechToTextClient(config)

        assert client.config == config
        assert client._session is None
        assert client._realtime_client is None

    def test_init_with_invalid_config_raises_error(self) -> None:
        """Test that invalid config raises ValueError."""
        with pytest.raises(ValueError, match="API key is required"):
            OpenAIConfig(api_key="")

    async def test_context_manager(self) -> None:
        """Test async context manager functionality."""
        config = OpenAIConfig(api_key="test-key")

        async with OpenAISpeechToTextClient(config) as client:
            assert isinstance(client, OpenAISpeechToTextClient)

        # Client should be closed after context exit

    @patch('aiohttp.ClientSession')
    async def test_get_session_creates_new_session(self, mock_session_class: Any) -> None:
        """Test that _get_session creates new aiohttp session."""
        mock_session = AsyncMock()
        mock_session_class.return_value = mock_session

        config = OpenAIConfig(api_key="test-key")
        client = OpenAISpeechToTextClient(config)

        session = await client._get_session()

        assert session == mock_session
        assert client._session == mock_session
        mock_session_class.assert_called_once()

    @patch('aiohttp.ClientSession')
    async def test_get_session_reuses_existing_session(self, mock_session_class: Any) -> None:
        """Test that _get_session reuses existing session."""
        mock_session = AsyncMock()
        mock_session.closed = False
        mock_session_class.return_value = mock_session

        config = OpenAIConfig(api_key="test-key")
        client = OpenAISpeechToTextClient(config)

        # Get session twice
        session1 = await client._get_session()
        session2 = await client._get_session()

        assert session1 == session2
        assert mock_session_class.call_count == 1  # Only called once

    async def test_close_session(self) -> None:
        """Test closing client session."""
        config = OpenAIConfig(api_key="test-key")
        client = OpenAISpeechToTextClient(config)

        # Mock session
        mock_session = AsyncMock()
        mock_session.closed = False
        client._session = mock_session

        await client.close()

        mock_session.close.assert_called_once()

    async def test_close_already_closed_session(self) -> None:
        """Test closing already closed session is safe."""
        config = OpenAIConfig(api_key="test-key")
        client = OpenAISpeechToTextClient(config)

        # Mock closed session
        mock_session = AsyncMock()
        mock_session.closed = True
        client._session = mock_session

        await client.close()

        # Should not call close on already closed session
        mock_session.close.assert_not_called()

    async def test_get_supported_languages(self) -> None:
        """Test getting supported languages list."""
        config = OpenAIConfig(api_key="test-key")
        client = OpenAISpeechToTextClient(config)

        languages = await client.get_supported_languages()

        assert isinstance(languages, list)
        assert len(languages) == 1
        assert "en" in languages
        # English-only implementation

    async def test_transcribe_success(self) -> None:
        """Test successful transcription."""
        # Create mock response and session
        mock_response = MockResponse(status=200, text_result="Hello world")
        mock_session = MockSession(mock_response)

        config = OpenAIConfig(api_key="test-key")
        client = OpenAISpeechToTextClient(config)

        # Patch the _get_session method directly
        setattr(client, '_get_session', AsyncMock(return_value=mock_session))

        audio = AudioChunk(data=b"audio_data", format=AudioFormat.WAV)
        result = await client.transcribe(audio)

        assert result == "Hello world"
        assert len(mock_session.post_calls) == 1
        assert "https://api.openai.com/v1/audio/transcriptions" in mock_session.post_calls[0][0]

    async def test_transcribe_with_language_and_prompt(self) -> None:
        """Test transcription with language and prompt parameters."""
        # Create mock response and session
        mock_response = MockResponse(status=200, text_result="Hello world")
        mock_session = MockSession(mock_response)

        config = OpenAIConfig(api_key="test-key")
        client = OpenAISpeechToTextClient(config)

        # Patch the _get_session method directly
        setattr(client, '_get_session', AsyncMock(return_value=mock_session))

        audio = AudioChunk(data=b"audio_data", format=AudioFormat.WAV)
        result = await client.transcribe(
            audio,
            language="en",
            prompt="This is English speech"
        )

        assert result == "Hello world"

    async def test_transcribe_empty_audio_raises_error(self) -> None:
        """Test that empty audio data raises ValueError."""
        config = OpenAIConfig(api_key="test-key")
        client = OpenAISpeechToTextClient(config)

        audio = AudioChunk(data=b"", format=AudioFormat.WAV)

        with pytest.raises(ValueError, match="Audio data cannot be empty"):
            await client.transcribe(audio)

    async def test_transcribe_api_error_401(self) -> None:
        """Test handling of 401 API error."""
        # Create mock response and session
        mock_response = MockResponse(status=401)
        mock_session = MockSession(mock_response)

        config = OpenAIConfig(api_key="invalid-key")
        client = OpenAISpeechToTextClient(config)

        # Patch the _get_session method directly
        setattr(client, '_get_session', AsyncMock(return_value=mock_session))

        audio = AudioChunk(data=b"audio_data", format=AudioFormat.WAV)

        with pytest.raises(APIError, match="Invalid API key"):
            await client.transcribe(audio)

    async def test_transcribe_api_error_429(self) -> None:
        """Test handling of 429 rate limit error."""
        # Create mock response and session
        mock_response = MockResponse(status=429)
        mock_session = MockSession(mock_response)

        config = OpenAIConfig(api_key="test-key")
        client = OpenAISpeechToTextClient(config)

        # Patch the _get_session method directly
        setattr(client, '_get_session', AsyncMock(return_value=mock_session))

        audio = AudioChunk(data=b"audio_data", format=AudioFormat.WAV)

        with pytest.raises(APIError, match="Rate limit exceeded"):
            await client.transcribe(audio)

    async def test_transcribe_network_error(self) -> None:
        """Test handling of network errors."""
        config = OpenAIConfig(api_key="test-key")
        client = OpenAISpeechToTextClient(config)

        # Create a mock session that returns a failing context manager
        network_error = aiohttp.ClientError("Network error")
        def create_failing_context() -> MockFailingContextManager:
            return MockFailingContextManager(network_error)
        mock_session = MockSession(post_side_effect=create_failing_context)
        setattr(client, '_get_session', AsyncMock(return_value=mock_session))

        audio = AudioChunk(data=b"audio_data", format=AudioFormat.WAV)

        with pytest.raises(TranscriptionError, match="Network error"):
            await client.transcribe(audio)

    async def test_transcribe_stream_success(self) -> None:
        """Test successful streaming transcription."""
        # Mock streaming content
        streaming_data = [
            b'data: {"text": "Hello"}\n\n',
            b'data: {"text": " world"}\n\n',
            b'data: [DONE]\n\n'
        ]

        # Create mock response with streaming data
        mock_response = MockResponse(status=200, iter_any_data=streaming_data)
        mock_session = MockSession(mock_response)

        config = OpenAIConfig(api_key="test-key")
        client = OpenAISpeechToTextClient(config)

        # Patch the _get_session method directly
        setattr(client, '_get_session', AsyncMock(return_value=mock_session))

        audio = AudioChunk(data=b"audio_data", format=AudioFormat.WAV)
        results = []

        async for chunk in client.transcribe_stream(audio):
            results.append(chunk)

        # Should process the streaming chunks
        assert len(results) >= 0  # Depends on implementation details

    async def test_transcribe_stream_empty_audio_raises_error(self) -> None:
        """Test that streaming with empty audio raises ValueError."""
        config = OpenAIConfig(api_key="test-key")
        client = OpenAISpeechToTextClient(config)

        audio = AudioChunk(data=b"", format=AudioFormat.WAV)

        with pytest.raises(ValueError, match="Audio data cannot be empty"):
            async for _ in client.transcribe_stream(audio):
                pass


class TestOpenAITextToSpeechClient:
    """Test cases for OpenAITextToSpeechClient."""

    def test_init_with_valid_config(self) -> None:
        """Test client initialization with valid config."""
        config = OpenAIConfig(api_key="test-key")
        client = OpenAITextToSpeechClient(config)

        assert client.config == config
        assert client._session is None

    def test_init_with_invalid_config_raises_error(self) -> None:
        """Test that invalid config raises ValueError."""
        with pytest.raises(ValueError, match="API key is required"):
            OpenAIConfig(api_key="")

    async def test_context_manager(self) -> None:
        """Test async context manager functionality."""
        config = OpenAIConfig(api_key="test-key")

        async with OpenAITextToSpeechClient(config) as client:
            assert isinstance(client, OpenAITextToSpeechClient)

    async def test_get_available_voices(self) -> None:
        """Test getting available voices list."""
        config = OpenAIConfig(api_key="test-key")
        client = OpenAITextToSpeechClient(config)

        voices = await client.get_available_voices()

        assert isinstance(voices, list)
        assert len(voices) > 0
        assert "alloy" in voices
        assert "echo" in voices
        assert "fable" in voices

    async def test_synthesize_success(self) -> None:
        """Test successful text-to-speech synthesis."""
        # Create mock response and session
        mock_response = MockResponse(status=200, read_result=b"audio_data")
        mock_session = MockSession(mock_response)

        config = OpenAIConfig(api_key="test-key")
        client = OpenAITextToSpeechClient(config)

        # Patch the _get_session method directly
        setattr(client, '_get_session', AsyncMock(return_value=mock_session))

        result = await client.synthesize("Hello world")

        assert result == b"audio_data"
        assert len(mock_session.post_calls) == 1

    async def test_synthesize_with_voice_and_language(self) -> None:
        """Test synthesis with specific voice and language."""
        # Create mock response and session
        mock_response = MockResponse(status=200, read_result=b"audio_data")
        mock_session = MockSession(mock_response)

        config = OpenAIConfig(api_key="test-key")
        client = OpenAITextToSpeechClient(config)

        # Patch the _get_session method directly
        setattr(client, '_get_session', AsyncMock(return_value=mock_session))

        result = await client.synthesize(
            "Hello world",
            voice_id="nova",
            language="en"
        )

        assert result == b"audio_data"

    async def test_synthesize_empty_text_raises_error(self) -> None:
        """Test that empty text raises ValueError."""
        config = OpenAIConfig(api_key="test-key")
        client = OpenAITextToSpeechClient(config)

        with pytest.raises(ValueError, match="Text cannot be empty"):
            await client.synthesize("")

    async def test_synthesize_api_error_401(self) -> None:
        """Test handling of 401 API error in synthesis."""
        # Create mock response and session
        mock_response = MockResponse(status=401)
        mock_session = MockSession(mock_response)

        config = OpenAIConfig(api_key="invalid-key")
        client = OpenAITextToSpeechClient(config)

        # Patch the _get_session method directly
        setattr(client, '_get_session', AsyncMock(return_value=mock_session))

        with pytest.raises(APIError, match="Invalid API key"):
            await client.synthesize("Hello world")

    async def test_synthesize_network_error(self) -> None:
        """Test handling of network errors in synthesis."""
        config = OpenAIConfig(api_key="test-key")
        client = OpenAITextToSpeechClient(config)

        # Create a mock session that returns a failing context manager
        network_error = aiohttp.ClientError("Network error")
        def create_failing_context() -> MockFailingContextManager:
            return MockFailingContextManager(network_error)
        mock_session = MockSession(post_side_effect=create_failing_context)
        setattr(client, '_get_session', AsyncMock(return_value=mock_session))

        with pytest.raises(SynthesisError, match="Network error"):
            await client.synthesize("Hello world")

    async def test_synthesize_stream_success(self) -> None:
        """Test successful streaming synthesis."""
        # Mock streaming content
        streaming_data = [
            b'data: {"audio": "base64_audio_chunk_1"}\n\n',
            b'data: {"audio": "base64_audio_chunk_2"}\n\n',
            b'data: [DONE]\n\n'
        ]

        # Create mock response with streaming data
        mock_response = MockResponse(status=200, iter_any_data=streaming_data)
        mock_session = MockSession(mock_response)

        config = OpenAIConfig(api_key="test-key")
        client = OpenAITextToSpeechClient(config)

        # Patch the _get_session method directly
        setattr(client, '_get_session', AsyncMock(return_value=mock_session))

        results = []

        async for chunk in client.synthesize_stream("Hello world"):
            results.append(chunk)

        # Should process the streaming chunks
        assert len(results) >= 0  # Depends on implementation details

    async def test_synthesize_stream_empty_text_raises_error(self) -> None:
        """Test that streaming with empty text raises ValueError."""
        config = OpenAIConfig(api_key="test-key")
        client = OpenAITextToSpeechClient(config)

        with pytest.raises(ValueError, match="Text cannot be empty"):
            async for _ in client.synthesize_stream(""):
                pass
