"""
Audio source implementations for speech input.

Provides concrete implementations of AudioSource interface for different input methods.
"""

import queue
import threading
from typing import Any, Optional

import pyaudio

from mAIgic_speech.speech_api import AudioSource, AudioSourceError, StreamingAudioSource


class PyAudioMicrophoneSource(StreamingAudioSource):
    """PyAudio-based microphone audio source.

    Provides real-time audio capture from system microphone using PyAudio.
    Suitable for desktop applications and development.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
        device_index: Optional[int] = None,
        format: int = pyaudio.paInt16
    ):
        """Initialize microphone source.

        Args:
            sample_rate: Audio sample rate in Hz
            channels: Number of audio channels (1 for mono, 2 for stereo)
            chunk_size: Size of audio chunks to capture
            device_index: Specific audio device to use (None for default)
            format: PyAudio format constant
        """
        self._sample_rate = sample_rate
        self._channels = channels
        self._chunk_size = chunk_size
        self._device_index = device_index
        self._format = format

        self._audio: Optional[pyaudio.PyAudio] = None
        self._stream: Optional[pyaudio.Stream] = None
        self._audio_queue: queue.Queue[bytes] = queue.Queue()
        self._is_active = False
        self._lock = threading.Lock()
        self._callback_count = 0

    async def start(self) -> None:
        """Start microphone capture."""
        with self._lock:
            if self._is_active:
                return
            try:
                self._audio = pyaudio.PyAudio()
                self._stream = self._audio.open(
                    format=self._format,
                    channels=self._channels,
                    rate=self._sample_rate,
                    input=True,
                    input_device_index=self._device_index,
                    frames_per_buffer=self._chunk_size,
                    stream_callback=self._audio_callback
                )
                self._is_active = True
                self._stream.start_stream()
            except Exception as e:
                # Clean up inline to avoid lock reentrance issues
                self._is_active = False
                if self._stream:
                    try:
                        self._stream.stop_stream()
                        self._stream.close()
                    except Exception:
                        pass
                    self._stream = None
                if self._audio:
                    try:
                        self._audio.terminate()
                    except Exception:
                        pass
                    self._audio = None
                raise AudioSourceError(f"Failed to start microphone: {e}") from e

    async def stop(self) -> None:
        """Stop microphone capture and clean up resources."""
        with self._lock:
            self._is_active = False

            if self._stream:
                try:
                    self._stream.stop_stream()
                    self._stream.close()
                except Exception:
                    pass
                self._stream = None

            if self._audio:
                try:
                    self._audio.terminate()
                except Exception:
                    pass
                self._audio = None

            # Clear any remaining audio chunks
            while not self._audio_queue.empty():
                try:
                    self._audio_queue.get_nowait()
                except queue.Empty:
                    break

    async def read_chunk(self) -> Optional[bytes]:
        if not self._is_active:
            return None
        try:
            chunk = self._audio_queue.get_nowait()
            return chunk
        except queue.Empty:
            return None

    def _audio_callback(self, in_data: bytes, frame_count: int, time_info: dict[str, Any], status: int) -> tuple[None, int]:
        """PyAudio callback for handling captured audio."""
        self._callback_count += 1
        if self._is_active and status == 0:  # No errors
            self._audio_queue.put(in_data)
        return (None, pyaudio.paContinue)

    @property
    def sample_rate(self) -> int:
        """Get the audio sample rate in Hz."""
        return self._sample_rate

    @property
    def channels(self) -> int:
        """Get the number of audio channels."""
        return self._channels

    @property
    def is_active(self) -> bool:
        return self._is_active


class FileAudioSource(AudioSource):
    """File-based audio source for testing and development.

    Reads audio from a file and provides it as streaming chunks.
    Useful for testing without microphone hardware.
    """

    def __init__(
        self,
        file_path: str,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
        loop: bool = False
    ):
        """Initialize file audio source.

        Args:
            file_path: Path to the audio file
            sample_rate: Audio sample rate in Hz
            channels: Number of audio channels
            chunk_size: Size of chunks to read
            loop: Whether to loop the file when it ends
        """
        self._file_path = file_path
        self._sample_rate = sample_rate
        self._channels = channels
        self._chunk_size = chunk_size
        self._loop = loop

        self._file_handle: Optional[Any] = None
        self._is_active = False
        self._current_position = 0

    async def start(self) -> None:
        """Start reading from file."""
        if self._is_active:
            return

        try:
            self._file_handle = open(self._file_path, 'rb')
            self._is_active = True
            self._current_position = 0
        except Exception as e:
            raise AudioSourceError(f"Failed to open audio file {self._file_path}: {e}") from e

    async def stop(self) -> None:
        """Stop reading from file and clean up."""
        self._is_active = False

        if self._file_handle:
            try:
                self._file_handle.close()
            except Exception:
                pass  # Ignore cleanup errors
            self._file_handle = None

    async def read_chunk(self) -> Optional[bytes]:
        """Read the next chunk from file.

        Returns:
            Optional[bytes]: Audio data chunk, or None if end of file
        """
        if not self._is_active or not self._file_handle:
            return None

        try:
            chunk = self._file_handle.read(self._chunk_size)

            if not chunk:
                if self._loop:
                    # Reset to beginning of file
                    self._file_handle.seek(0)
                    self._current_position = 0
                    chunk = self._file_handle.read(self._chunk_size)
                else:
                    return b""  # EOF - no more data available

            self._current_position += len(chunk)
            return chunk if isinstance(chunk, bytes) else None

        except Exception as e:
            raise AudioSourceError(f"Error reading from audio file: {e}") from e

    @property
    def sample_rate(self) -> int:
        """Get the audio sample rate in Hz."""
        return self._sample_rate

    @property
    def channels(self) -> int:
        """Get the number of audio channels."""
        return self._channels

    @property
    def is_active(self) -> bool:
        """Check if the audio source is currently active."""
        return self._is_active
