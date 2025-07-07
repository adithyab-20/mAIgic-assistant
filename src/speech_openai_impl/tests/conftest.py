"""Shared test fixtures and configuration for speech_openai_impl tests."""

import asyncio
from typing import Any, Dict, Generator, List
from unittest.mock import AsyncMock, MagicMock

import pytest

from speech_api.types import AudioChunk, AudioFormat
from speech_openai_impl.config import OpenAIConfig


@pytest.fixture
def sample_config() -> OpenAIConfig:
    """Create a sample OpenAI configuration for testing."""
    return OpenAIConfig(api_key="test-api-key")


@pytest.fixture
def sample_audio_chunk() -> AudioChunk:
    """Create a sample audio chunk for testing."""
    return AudioChunk(
        data=b"sample_audio_data" * 100,  # 1700 bytes
        sample_rate=16000,
        channels=1,
        format=AudioFormat.WAV
    )


@pytest.fixture
def mock_aiohttp_session() -> AsyncMock:
    """Create a mock aiohttp session."""
    session = AsyncMock()
    session.closed = False
    session.close = AsyncMock()
    session.post = AsyncMock()
    return session


@pytest.fixture
def mock_aiohttp_response() -> AsyncMock:
    """Create a mock aiohttp response with proper context manager support."""
    response = AsyncMock()
    response.status = 200
    response.text = AsyncMock(return_value="Mock response")
    response.read = AsyncMock(return_value=b"Mock binary response")
    response.raise_for_status = MagicMock()
    return response


class MockAsyncContextManager:
    """A proper async context manager mock for testing."""

    def __init__(self, response: AsyncMock) -> None:
        self.response = response

    async def __aenter__(self) -> AsyncMock:
        return self.response

    async def __aexit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: Any) -> None:
        return None


def create_mock_http_session_with_response(mock_response: AsyncMock) -> AsyncMock:
    """Helper function to create a properly mocked aiohttp session."""
    mock_session = AsyncMock()

    # Use our custom async context manager
    mock_session.post.return_value = MockAsyncContextManager(mock_response)
    mock_session.closed = False
    mock_session.close = AsyncMock()

    return mock_session


@pytest.fixture
def mock_websocket() -> AsyncMock:
    """Create a mock WebSocket connection."""
    websocket = AsyncMock()
    websocket.send = AsyncMock()
    websocket.close = AsyncMock()
    websocket.recv = AsyncMock()
    return websocket


@pytest.fixture
def mock_successful_http_response() -> AsyncMock:
    """Create a mock successful HTTP response."""
    response = AsyncMock()
    response.status = 200
    response.text = AsyncMock(return_value="Transcription result")
    response.read = AsyncMock(return_value=b"audio_data")
    response.raise_for_status = MagicMock()
    return response


@pytest.fixture
def mock_error_http_response() -> AsyncMock:
    """Create a mock error HTTP response."""
    response = AsyncMock()
    response.status = 401
    response.text = AsyncMock(return_value="Unauthorized")
    return response


@pytest.fixture
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Test utilities for creating mock objects
class MockHelpers:
    """Helper class for creating common mock objects."""

    @staticmethod
    def create_transcription_event(text: str, is_final: bool = True) -> Dict[str, str]:
        """Create a mock transcription event."""
        return {
            "type": "conversation.item.input_audio_transcription.completed" if is_final
                   else "conversation.item.input_audio_transcription.failed",
            "transcript": text if is_final else ""
        }

    @staticmethod
    def create_speech_event(event_type: str) -> Dict[str, str]:
        """Create a mock speech detection event."""
        return {
            "type": f"input_audio_buffer.speech_{event_type}"
        }

    @staticmethod
    def create_streaming_response_chunks(texts: List[str]) -> List[bytes]:
        """Create mock streaming response chunks."""
        chunks: List[bytes] = []
        for text in texts:
            chunks.append(f'data: {{"text": "{text}"}}\n\n'.encode())
        chunks.append(b'data: [DONE]\n\n')
        return chunks


@pytest.fixture
def mock_helpers() -> MockHelpers:
    """Provide access to mock helper utilities."""
    return MockHelpers()
