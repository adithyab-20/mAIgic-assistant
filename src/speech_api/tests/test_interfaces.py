"""Tests for the Speech API interfaces."""

from typing import AsyncGenerator, List, Optional

import pytest

from speech_api.interfaces import AudioSource, SpeechToTextClient, TextToSpeechClient
from speech_api.types import AudioChunk, RealtimeSessionConfig, TranscriptionEvent


class DummyAudioSource(AudioSource):
    """Dummy audio source for testing."""

    def __init__(self, chunks: List[bytes]):
        self._chunks = chunks
        self._index = 0
        self._active = False

    async def start(self) -> None:
        self._active = True

    async def stop(self) -> None:
        self._active = False

    async def read_chunk(self) -> Optional[bytes]:
        if self._index < len(self._chunks):
            chunk = self._chunks[self._index]
            self._index += 1
            return chunk
        return None

    @property
    def sample_rate(self) -> int:
        return 16000

    @property
    def channels(self) -> int:
        return 1

    @property
    def is_active(self) -> bool:
        return self._active


class DummySpeechToTextClient(SpeechToTextClient):
    """Dummy implementation for testing."""

    def __init__(self, response_text: str = "test transcription") -> None:
        self._response_text = response_text

    async def transcribe(
        self,
        audio: AudioChunk,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> str:
        if len(audio.data) == 0:
            raise ValueError("Empty audio data")
        return self._response_text

    async def transcribe_stream(
        self,
        audio: AudioChunk,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        words = self._response_text.split()
        for i in range(1, len(words) + 1):
            yield " ".join(words[:i])

    async def transcribe_realtime(
        self,
        audio_source: AudioSource,
        config: RealtimeSessionConfig,
    ) -> AsyncGenerator[TranscriptionEvent, None]:
        await audio_source.start()
        try:
            chunk_count = 0
            while audio_source.is_active:
                chunk = await audio_source.read_chunk()
                if chunk is None:
                    break
                chunk_count += 1
                # Create a dummy transcription event
                event = TranscriptionEvent(
                    text=f"chunk_{chunk_count}: {self._response_text}",
                    is_final=True,
                    confidence=0.95,
                    timestamp=chunk_count * 1.0
                )
                yield event
        finally:
            await audio_source.stop()

    async def get_supported_languages(self) -> List[str]:
        return ["en", "es", "fr", "de"]


class DummyTextToSpeechClient(TextToSpeechClient):
    """Dummy implementation for testing."""

    def __init__(self, response_audio: bytes = b"fake_audio_data") -> None:
        self._response_audio = response_audio

    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        language: Optional[str] = None,
    ) -> bytes:
        if not text.strip():
            raise ValueError("Empty text")

        # Simulate different voice settings
        if voice_id:
            prefix = f"voice_{voice_id}_".encode()
            return prefix + self._response_audio
        return self._response_audio

    async def synthesize_stream(
        self,
        text: str,
        voice_id: Optional[str] = None,
        language: Optional[str] = None,
    ) -> AsyncGenerator[bytes, None]:
        if not text.strip():
            raise ValueError("Empty text")

        # Simulate different voice settings
        if voice_id:
            base_audio = f"voice_{voice_id}_".encode() + self._response_audio
        else:
            base_audio = self._response_audio

        # Stream it in reasonable chunks (simulate real audio streaming)
        chunk_size = max(1024, len(base_audio) // 3)  # At least 1KB chunks
        for i in range(0, len(base_audio), chunk_size):
            yield base_audio[i:i + chunk_size]

    async def get_available_voices(self) -> List[str]:
        return ["nova", "alloy", "echo", "fable"]


class TestSpeechToTextClient:
    """Tests for SpeechToTextClient interface."""

    @pytest.fixture
    def stt_client(self) -> SpeechToTextClient:
        return DummySpeechToTextClient("hello world")

    @pytest.fixture
    def audio_chunk(self) -> AudioChunk:
        return AudioChunk(data=b"fake_audio_data")

    @pytest.mark.asyncio
    async def test_transcribe_returns_text(self, stt_client: SpeechToTextClient, audio_chunk: AudioChunk) -> None:
        result = await stt_client.transcribe(audio_chunk)
        assert isinstance(result, str)
        assert result == "hello world"

    @pytest.mark.asyncio
    async def test_transcribe_with_parameters(self, stt_client: SpeechToTextClient, audio_chunk: AudioChunk) -> None:
        result = await stt_client.transcribe(
            audio_chunk,
            language="en",
            prompt="Voice commands"
        )
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_transcribe_stream_yields_partial_results(self, stt_client: SpeechToTextClient, audio_chunk: AudioChunk) -> None:
        results = []
        async for partial in stt_client.transcribe_stream(audio_chunk):
            results.append(partial)

        assert len(results) == 2
        assert results[0] == "hello"
        assert results[1] == "hello world"

    @pytest.mark.asyncio
    async def test_transcribe_realtime_processes_stream(self, stt_client: SpeechToTextClient) -> None:
        # Create dummy audio source with test chunks
        audio_source = DummyAudioSource([b"chunk1", b"chunk2"])

        # Create dummy config
        config = RealtimeSessionConfig(
            model="test-model",
            language="en"
        )

        results = []
        async for event in stt_client.transcribe_realtime(audio_source, config):
            results.append(event)

        assert len(results) == 2
        assert isinstance(results[0], TranscriptionEvent)
        assert isinstance(results[1], TranscriptionEvent)
        assert "chunk_1" in results[0].text
        assert "chunk_2" in results[1].text

    @pytest.mark.asyncio
    async def test_get_supported_languages(self, stt_client: SpeechToTextClient) -> None:
        languages = await stt_client.get_supported_languages()
        assert isinstance(languages, list)
        assert "en" in languages


class TestTextToSpeechClient:
    """Tests for TextToSpeechClient interface."""

    @pytest.fixture
    def tts_client(self) -> TextToSpeechClient:
        return DummyTextToSpeechClient(b"synthesized_audio")

    @pytest.mark.asyncio
    async def test_synthesize_returns_audio(self, tts_client: TextToSpeechClient) -> None:
        result = await tts_client.synthesize("Hello world")
        assert isinstance(result, bytes)
        assert result == b"synthesized_audio"

    @pytest.mark.asyncio
    async def test_synthesize_with_voice_settings(self, tts_client: TextToSpeechClient) -> None:
        result = await tts_client.synthesize("Hello", voice_id="nova", language="en")
        assert isinstance(result, bytes)
        assert result.startswith(b"voice_nova_")

    @pytest.mark.asyncio
    async def test_synthesize_stream_yields_chunks(self, tts_client: TextToSpeechClient) -> None:
        chunks = []
        async for chunk in tts_client.synthesize_stream("Hello world"):
            chunks.append(chunk)

        assert len(chunks) > 0
        assert all(isinstance(chunk, bytes) for chunk in chunks)

    @pytest.mark.asyncio
    async def test_synthesize_stream_with_voice_settings(self, tts_client: TextToSpeechClient) -> None:
        chunks = []
        async for chunk in tts_client.synthesize_stream("Hello world", voice_id="nova", language="en"):
            chunks.append(chunk)

        assert len(chunks) > 0
        assert all(isinstance(chunk, bytes) for chunk in chunks)

    @pytest.mark.asyncio
    async def test_get_available_voices(self, tts_client: TextToSpeechClient) -> None:
        voices = await tts_client.get_available_voices()
        assert isinstance(voices, list)
        assert "nova" in voices


class TestInterfaceCompliance:
    """Tests to ensure implementations comply with interface contracts."""

    def test_stt_interface_methods_exist(self) -> None:
        required_methods = [
            "transcribe",
            "transcribe_stream",
            "transcribe_realtime",
            "get_supported_languages"
        ]

        for method_name in required_methods:
            assert hasattr(SpeechToTextClient, method_name)
            assert callable(getattr(SpeechToTextClient, method_name))

    def test_tts_interface_methods_exist(self) -> None:
        required_methods = [
            "synthesize",
            "synthesize_stream",
            "get_available_voices"
        ]

        for method_name in required_methods:
            assert hasattr(TextToSpeechClient, method_name)
            assert callable(getattr(TextToSpeechClient, method_name))
