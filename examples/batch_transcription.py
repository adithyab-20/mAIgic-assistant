#!/usr/bin/env python3
"""
Batch Audio Transcription Example
=================================

This example demonstrates how to use the OpenAI implementation of the mAIgic-assistant
speech API for batch transcription of audio files.

The OpenAI implementation (speech-openai-impl) provides:
- Integration with OpenAI's Whisper API
- Support for multiple audio formats (WAV, MP3, FLAC, etc.)
- High-quality transcription with punctuation
- Language detection and custom language specification
- Custom prompts for improved accuracy

Requirements:
- OpenAI API key (set in OPENAI_API_KEY environment variable or .env file)
- Audio files to transcribe
- Python packages: speech-openai-impl, python-dotenv

Usage:
    python examples/batch_transcription.py [audio_file]

If no audio file is specified, the example will use the default test audio files
in the project directory. The transcription will be completed in one operation
and the full result will be displayed.
"""

import asyncio
import logging
import os
import sys
import tempfile
import time
from pathlib import Path

# Add src to path for importing our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv

from speech_api import AudioChunk, AudioFormat
from speech_openai_impl import OpenAIConfig, OpenAISpeechToTextClient

# Audio recording imports
try:
    import wave

    import pyaudio
    RECORDING_AVAILABLE = True
except ImportError:
    RECORDING_AVAILABLE = False

# Configure logging to show only important messages
logging.basicConfig(level=logging.INFO)
# Suppress debug messages from the speech implementation modules
logging.getLogger("speech_openai_impl.sessions").setLevel(logging.WARNING)
logging.getLogger("speech_openai_impl.clients").setLevel(logging.WARNING)

# Load environment variables from .env file
load_dotenv()


def record_audio(duration_seconds: int = 10, filename: str = None) -> str:
    """
    Record audio from microphone for the specified duration.

    Args:
        duration_seconds: How long to record (default: 10 seconds)
        filename: Output filename (default: temporary file)

    Returns:
        str: Path to the recorded audio file

    Raises:
        RuntimeError: If recording is not available
    """
    if not RECORDING_AVAILABLE:
        raise RuntimeError("Audio recording not available. Install pyaudio: pip install pyaudio")

    if filename is None:
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        filename = temp_file.name
        temp_file.close()

    # Audio recording parameters
    sample_rate = 16000
    channels = 1
    chunk_size = 1024
    audio_format = pyaudio.paInt16

    print(f"Recording audio for {duration_seconds} seconds...")
    print("Speak clearly into your microphone!")
    print("Recording will start in 3 seconds...")

    # Countdown
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    print("🎤 Recording... Speak now!")

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    try:
        # Open recording stream
        stream = audio.open(
            format=audio_format,
            channels=channels,
            rate=sample_rate,
            input=True,
            frames_per_buffer=chunk_size
        )

        frames = []

        # Record audio
        for _ in range(0, int(sample_rate / chunk_size * duration_seconds)):
            data = stream.read(chunk_size)
            frames.append(data)

        print("✅ Recording completed!")

        # Stop and close stream
        stream.stop_stream()
        stream.close()

        # Save to WAV file
        with wave.open(filename, 'wb') as wave_file:
            wave_file.setnchannels(channels)
            wave_file.setsampwidth(audio.get_sample_size(audio_format))
            wave_file.setframerate(sample_rate)
            wave_file.writeframes(b''.join(frames))

        print(f"Audio saved to: {filename}")
        return filename

    finally:
        audio.terminate()


async def batch_transcription_example(audio_file_path: str = None, record_new: bool = False):
    """
    Demonstrates batch transcription of audio files.

    This example shows how to transcribe a complete audio file and get
    the full transcription result at once.

    Args:
        audio_file_path: Path to the audio file to transcribe
        record_new: Whether to record new audio
    """
    print("Batch Audio Transcription Example")
    print("=" * 50)

    # Handle audio source
    temp_file_to_cleanup = None

    if record_new:
        try:
            duration = int(input("How many seconds to record? (default: 10): ") or "10")
            audio_file_path = record_audio(duration)
            temp_file_to_cleanup = audio_file_path
        except KeyboardInterrupt:
            print("\nRecording cancelled.")
            return
        except Exception as e:
            print(f"Recording failed: {e}")
            return
    elif audio_file_path is None:
        # Use default or ask user
        print("No audio file provided.")
        if RECORDING_AVAILABLE:
            choice = input("Would you like to (r)ecord audio or (q)uit? [r/q]: ").lower()
            if choice == 'r':
                try:
                    duration = int(input("How many seconds to record? (default: 10): ") or "10")
                    audio_file_path = record_audio(duration)
                    temp_file_to_cleanup = audio_file_path
                except KeyboardInterrupt:
                    print("\nRecording cancelled.")
                    return
                except Exception as e:
                    print(f"Recording failed: {e}")
                    return
            else:
                print("Please provide an audio file path or use the recording option.")
                return
        else:
            print("Please provide an audio file path.")
            print("To enable recording, install pyaudio: pip install pyaudio")
            return

    if not os.path.exists(audio_file_path):
        print(f"Error: Audio file not found: {audio_file_path}")
        return

    try:
        # Initialize the OpenAI Speech-to-Text client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Error: OPENAI_API_KEY environment variable not found.")
            print("Please set your OpenAI API key in a .env file or environment variable.")
            return

        config = OpenAIConfig(api_key=api_key)
        client = OpenAISpeechToTextClient(config)

        print(f"Transcribing audio file: {audio_file_path}")
        print("Processing... (this may take a moment)")

        # Read the audio file
        with open(audio_file_path, "rb") as f:
            audio_data = f.read()

        # Create audio chunk
        audio_chunk = AudioChunk(
            data=audio_data,
            format=AudioFormat.WAV,
            sample_rate=16000,
            channels=1
        )

        # Use async context manager to ensure proper cleanup
        async with client:
            # Perform batch transcription
            start_time = time.time()
            result = await client.transcribe(audio_chunk)
            end_time = time.time()

        # Display results
        print("\n" + "=" * 50)
        print("TRANSCRIPTION RESULT")
        print("=" * 50)
        print(f"Transcribed text: {result}")
        print(f"Processing time: {end_time - start_time:.2f} seconds")

    except Exception as e:
        print(f"Transcription failed: {e}")

    finally:
        # Clean up temporary file if created
        if temp_file_to_cleanup and os.path.exists(temp_file_to_cleanup):
            try:
                os.unlink(temp_file_to_cleanup)
                print(f"Cleaned up temporary file: {temp_file_to_cleanup}")
            except OSError:
                pass  # Ignore cleanup errors


if __name__ == "__main__":
    """
    Main entry point for the batch transcription example.

    Usage:
        python examples/batch_transcription.py [audio_file_path]
        python examples/batch_transcription.py --record
        python examples/batch_transcription.py -r

    If no arguments are provided and recording is available,
    the user will be prompted to choose.
    """
    import sys

    audio_file_path = None
    record_new = False

    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ['--record', '-r']:
            record_new = True
        elif arg.startswith('-'):
            print("Usage:")
            print("  python examples/batch_transcription.py [audio_file_path]")
            print("  python examples/batch_transcription.py --record")
            print("  python examples/batch_transcription.py -r")
            print()
            print("Options:")
            print("  --record, -r    Record new audio for transcription")
            print("  audio_file_path Path to existing audio file")
            sys.exit(1)
        else:
            audio_file_path = arg

    # Run the example
    asyncio.run(batch_transcription_example(audio_file_path, record_new))
