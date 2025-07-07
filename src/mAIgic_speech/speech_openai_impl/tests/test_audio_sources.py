"""Tests for audio source implementations."""

import tempfile
from unittest.mock import MagicMock, patch

import pytest

from mAIgic_speech.speech_api.exceptions import AudioSourceError
from mAIgic_speech.speech_openai_impl.audio_sources import (
    FileAudioSource,
    PyAudioMicrophoneSource,
)


class TestFileAudioSource:
    """Test cases for FileAudioSource."""

    def test_init_with_defaults(self) -> None:
        """Test FileAudioSource initialization with default parameters."""
        source = FileAudioSource("/path/to/test.wav")

        assert source._file_path == "/path/to/test.wav"
        assert source._sample_rate == 16000
        assert source._channels == 1
        assert source._chunk_size == 1024
        assert source._loop is False
        assert source._file_handle is None
        assert source._is_active is False

    def test_init_with_custom_parameters(self) -> None:
        """Test FileAudioSource initialization with custom parameters."""
        source = FileAudioSource(
            file_path="/path/to/test.wav",
            sample_rate=44100,
            channels=2,
            chunk_size=2048,
            loop=True
        )

        assert source._file_path == "/path/to/test.wav"
        assert source._sample_rate == 44100
        assert source._channels == 2
        assert source._chunk_size == 2048
        assert source._loop is True

    async def test_start_success(self) -> None:
        """Test successfully starting file audio source."""
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(b"test audio data")
            temp_file.flush()

            source = FileAudioSource(temp_file.name)
            await source.start()

            assert source._is_active is True
            assert source._file_handle is not None

            await source.stop()

    async def test_start_nonexistent_file_raises_error(self) -> None:
        """Test that starting with nonexistent file raises AudioSourceError."""
        source = FileAudioSource("/nonexistent/file.wav")

        with pytest.raises(AudioSourceError, match="Failed to open audio file"):
            await source.start()

    async def test_start_already_active_is_idempotent(self) -> None:
        """Test that calling start when already active is idempotent."""
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(b"test data")
            temp_file.flush()

            source = FileAudioSource(temp_file.name)
            await source.start()
            first_handle = source._file_handle

            await source.start()  # Should not change anything

            assert source._file_handle is first_handle
            await source.stop()

    async def test_stop_success(self) -> None:
        """Test successfully stopping file audio source."""
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(b"test data")
            temp_file.flush()

            source = FileAudioSource(temp_file.name)
            await source.start()
            await source.stop()

            assert source._is_active is False
            assert source._file_handle is None

    async def test_stop_when_inactive_is_idempotent(self) -> None:
        """Test that stopping when already inactive is idempotent."""
        source = FileAudioSource("/path/to/test.wav")
        await source.stop()  # Should not raise error
        assert source._is_active is False

    async def test_read_chunk_success(self) -> None:
        """Test successfully reading audio chunks."""
        test_data = b"0123456789" * 200  # 2000 bytes

        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(test_data)
            temp_file.flush()

            source = FileAudioSource(temp_file.name, chunk_size=100)
            await source.start()

            chunk1 = await source.read_chunk()
            chunk2 = await source.read_chunk()

            assert chunk1 is not None
            assert chunk2 is not None
            assert len(chunk1) == 100
            assert len(chunk2) == 100
            assert chunk1 == test_data[:100]
            assert chunk2 == test_data[100:200]

            await source.stop()

    async def test_read_chunk_end_of_file(self) -> None:
        """Test reading chunk at end of file."""
        test_data = b"short"

        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(test_data)
            temp_file.flush()

            source = FileAudioSource(temp_file.name, chunk_size=100)
            await source.start()

            chunk1 = await source.read_chunk()
            chunk2 = await source.read_chunk()

            assert chunk1 == test_data
            assert chunk2 == b""  # EOF

            await source.stop()

    async def test_read_chunk_with_loop(self) -> None:
        """Test reading chunk with loop enabled."""
        test_data = b"test"

        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(test_data)
            temp_file.flush()

            source = FileAudioSource(temp_file.name, chunk_size=2, loop=True)
            await source.start()

            chunk1 = await source.read_chunk()
            chunk2 = await source.read_chunk()
            chunk3 = await source.read_chunk()  # Should loop back

            assert chunk1 == b"te"
            assert chunk2 == b"st"
            assert chunk3 == b"te"  # Back to beginning

            await source.stop()

    async def test_read_chunk_when_inactive_returns_none(self) -> None:
        """Test that reading chunk when inactive returns None."""
        source = FileAudioSource("/path/to/test.wav")
        result = await source.read_chunk()
        assert result is None

    def test_properties(self) -> None:
        """Test audio source properties."""
        source = FileAudioSource(
            "/path/to/test.wav",
            sample_rate=44100,
            channels=2
        )

        assert source.sample_rate == 44100
        assert source.channels == 2
        assert source.is_active is False


class TestPyAudioMicrophoneSource:
    """Test cases for PyAudioMicrophoneSource."""

    def test_init_with_defaults(self) -> None:
        """Test PyAudioMicrophoneSource initialization with defaults."""
        source = PyAudioMicrophoneSource()

        assert source._sample_rate == 16000
        assert source._channels == 1
        assert source._chunk_size == 1024
        assert source._device_index is None
        assert source._audio is None
        assert source._stream is None
        assert source._is_active is False

    def test_init_with_custom_parameters(self) -> None:
        """Test PyAudioMicrophoneSource initialization with custom parameters."""
        source = PyAudioMicrophoneSource(
            sample_rate=44100,
            channels=2,
            chunk_size=2048,
            device_index=1
        )

        assert source._sample_rate == 44100
        assert source._channels == 2
        assert source._chunk_size == 2048
        assert source._device_index == 1

    @patch('mAIgic_speech.speech_openai_impl.audio_sources.pyaudio')
    async def test_start_success(self, mock_pyaudio_module: MagicMock) -> None:
        """Test successfully starting microphone audio source."""
        # Mock PyAudio objects
        mock_pyaudio = MagicMock()
        mock_stream = MagicMock()
        mock_pyaudio_module.PyAudio.return_value = mock_pyaudio
        mock_pyaudio.open.return_value = mock_stream

        source = PyAudioMicrophoneSource()
        await source.start()

        assert source._is_active is True
        assert source._audio is mock_pyaudio
        assert source._stream is mock_stream

        # Verify PyAudio was called correctly
        mock_pyaudio.open.assert_called_once()
        mock_stream.start_stream.assert_called_once()

        await source.stop()

    @patch('mAIgic_speech.speech_openai_impl.audio_sources.pyaudio')
    async def test_start_pyaudio_error_cleans_up(self, mock_pyaudio_module: MagicMock) -> None:
        """Test that PyAudio error during start cleans up properly."""
        mock_pyaudio = MagicMock()
        mock_pyaudio_module.PyAudio.return_value = mock_pyaudio
        mock_pyaudio.open.side_effect = Exception("PyAudio error")

        source = PyAudioMicrophoneSource()

        with pytest.raises(AudioSourceError, match="Failed to start microphone"):
            await source.start()

        # Should have cleaned up
        assert source._is_active is False
        assert source._audio is None
        assert source._stream is None

    @patch('mAIgic_speech.speech_openai_impl.audio_sources.pyaudio')
    async def test_start_already_active_is_idempotent(self, mock_pyaudio_module: MagicMock) -> None:
        """Test that calling start when already active is idempotent."""
        mock_pyaudio = MagicMock()
        mock_stream = MagicMock()
        mock_pyaudio_module.PyAudio.return_value = mock_pyaudio
        mock_pyaudio.open.return_value = mock_stream

        source = PyAudioMicrophoneSource()
        await source.start()
        first_audio = source._audio

        await source.start()  # Should not change anything

        assert source._audio is first_audio
        assert mock_pyaudio.open.call_count == 1  # Only called once

        await source.stop()

    @patch('mAIgic_speech.speech_openai_impl.audio_sources.pyaudio')
    async def test_stop_success(self, mock_pyaudio_module: MagicMock) -> None:
        """Test successfully stopping microphone audio source."""
        mock_pyaudio = MagicMock()
        mock_stream = MagicMock()
        mock_pyaudio_module.PyAudio.return_value = mock_pyaudio
        mock_pyaudio.open.return_value = mock_stream

        source = PyAudioMicrophoneSource()
        await source.start()
        await source.stop()

        assert source._is_active is False
        assert source._audio is None
        assert source._stream is None

        mock_stream.stop_stream.assert_called_once()
        mock_stream.close.assert_called_once()
        mock_pyaudio.terminate.assert_called_once()

    async def test_stop_when_inactive_is_idempotent(self) -> None:
        """Test that stopping when already inactive is idempotent."""
        source = PyAudioMicrophoneSource()
        await source.stop()  # Should not raise error
        assert source._is_active is False

    @patch('mAIgic_speech.speech_openai_impl.audio_sources.pyaudio')
    async def test_read_chunk_success(self, mock_pyaudio_module: MagicMock) -> None:
        """Test successfully reading audio chunk."""
        mock_pyaudio = MagicMock()
        mock_stream = MagicMock()
        mock_pyaudio_module.PyAudio.return_value = mock_pyaudio
        mock_pyaudio.open.return_value = mock_stream

        source = PyAudioMicrophoneSource()
        await source.start()

        # Simulate audio callback adding data to queue
        test_data = b"audio_chunk_data"
        source._audio_queue.put(test_data)

        chunk = await source.read_chunk()
        assert chunk == test_data

        await source.stop()

    async def test_read_chunk_empty_queue_returns_none(self) -> None:
        """Test that reading from empty queue returns None."""
        source = PyAudioMicrophoneSource()
        source._is_active = True  # Simulate active state

        chunk = await source.read_chunk()
        assert chunk is None

    async def test_read_chunk_when_inactive_returns_none(self) -> None:
        """Test that reading chunk when inactive returns None."""
        source = PyAudioMicrophoneSource()
        result = await source.read_chunk()
        assert result is None

    @patch('mAIgic_speech.speech_openai_impl.audio_sources.pyaudio')
    def test_audio_callback(self, mock_pyaudio_module: MagicMock) -> None:
        """Test audio callback adds data to queue."""
        source = PyAudioMicrophoneSource()
        source._is_active = True

        test_data = b"audio_data"
        time_info = {"input_buffer_adc_time": 0.0, "current_time": 0.0, "output_buffer_dac_time": 0.0}
        result = source._audio_callback(test_data, 1024, time_info, 0)

        # Should add data to queue
        assert not source._audio_queue.empty()
        queued_data = source._audio_queue.get_nowait()
        assert queued_data == test_data

        # Should return continuation signal
        assert result == (None, mock_pyaudio_module.paContinue)

    @patch('mAIgic_speech.speech_openai_impl.audio_sources.pyaudio')
    def test_audio_callback_with_error_status(self, mock_pyaudio_module: MagicMock) -> None:
        """Test audio callback with error status doesn't add data."""
        source = PyAudioMicrophoneSource()
        source._is_active = True

        test_data = b"audio_data"
        time_info = {"input_buffer_adc_time": 0.0, "current_time": 0.0, "output_buffer_dac_time": 0.0}
        result = source._audio_callback(test_data, 1024, time_info, 1)  # Error status

        # Should not add data to queue
        assert source._audio_queue.empty()

        # Should still return continuation signal
        assert result == (None, mock_pyaudio_module.paContinue)

    def test_audio_callback_when_inactive(self) -> None:
        """Test audio callback when source is inactive."""
        source = PyAudioMicrophoneSource()
        source._is_active = False

        test_data = b"audio_data"
        time_info = {"input_buffer_adc_time": 0.0, "current_time": 0.0, "output_buffer_dac_time": 0.0}
        source._audio_callback(test_data, 1024, time_info, 0)

        # Should not add data to queue when inactive
        assert source._audio_queue.empty()

    def test_properties(self) -> None:
        """Test audio source properties."""
        source = PyAudioMicrophoneSource(
            sample_rate=44100,
            channels=2
        )

        assert source.sample_rate == 44100
        assert source.channels == 2
        assert source.is_active is False
