#!/usr/bin/env python3
"""
Streaming Audio Transcription Example
====================================

This example demonstrates how to use the OpenAI implementation of the mAIgic-assistant
speech API for streaming transcription results from audio files.

The OpenAI implementation (speech-openai-impl) provides:
- Integration with OpenAI's Whisper API with streaming responses
- Progressive transcription results as the audio is processed
- Memory-efficient processing with chunked results
- Real-time feedback during processing

Note: This example demonstrates streaming *results* from a complete audio file,
not streaming *input* from a live audio source. For live audio streaming,
see the realtime_transcription.py example.

Requirements:
- OpenAI API key (set in OPENAI_API_KEY environment variable or .env file)
- Audio files to transcribe
- Python packages: speech-openai-impl, python-dotenv

Usage:
    python examples/streaming_transcription.py [audio_file]

The transcription will process the complete audio file but return results
progressively, providing feedback as processing occurs.
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


async def streaming_transcription_example(audio_file_path: str = None, record_new: bool = False):
    """
    Demonstrates streaming transcription of audio files.

    This example shows how to transcribe audio files in chunks and receive
    partial results as they become available, useful for progressive feedback.

    Args:
        audio_file_path: Path to the audio file to transcribe
        record_new: Whether to record a new audio file before transcribing
    """
    print("Streaming Audio Transcription Example")
    print("=" * 50)

    # Handle audio source
    temp_file_to_cleanup = None

    if record_new:
        try:
            duration = int(input("How many seconds to record? (default: 15): ") or "15")
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
                    duration = int(input("How many seconds to record? (default: 15): ") or "15")
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

        print(f"Streaming transcription of: {os.path.basename(audio_file_path)}")
        print("Processing... (you'll see partial results as they arrive)")
        print()

        # Read the complete audio file
        with open(audio_file_path, 'rb') as audio_file:
            audio_data = audio_file.read()

        # Create AudioChunk for the complete audio
        audio_chunk = AudioChunk(
            data=audio_data,
            format=AudioFormat.WAV,
            sample_rate=16000,
            channels=1
        )

        print("📡 Starting streaming transcription...")
        print("🎧 Processing complete audio file with streaming results...")
        print("-" * 50)

        # Use async context manager to ensure proper cleanup
        async with client:
            # Use streaming transcription to get progressive results
            complete_transcription = ""
            chunk_count = 0

            try:
                async for partial_result in client.transcribe_stream(audio_chunk):
                    chunk_count += 1
                    if partial_result.strip():
                        print(f"📝 [Chunk {chunk_count}]: {partial_result}")
                        complete_transcription += partial_result

            except Exception as e:
                print(f"⚠️  Error during streaming transcription: {e}")
                # Fall back to regular transcription if streaming fails
                print("🔄 Falling back to batch transcription...")
                try:
                    complete_transcription = await client.transcribe(audio_chunk)
                    print(f"📝 [Fallback]: {complete_transcription}")
                except Exception as fallback_error:
                    print(f"❌ Fallback transcription also failed: {fallback_error}")
                    raise

        # Display final results
        print("\n" + "=" * 50)
        print("FINAL STREAMING TRANSCRIPTION RESULT")
        print("=" * 50)
        print(f"Streaming chunks received: {chunk_count}")
        print(f"Complete transcription: {complete_transcription.strip()}")
        print(f"Total length: {len(complete_transcription.strip())} characters")

    except Exception as e:
        print(f"Streaming transcription failed: {e}")

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
    Main entry point for the streaming transcription example.

    Usage:
        python examples/streaming_transcription.py [audio_file_path]
        python examples/streaming_transcription.py --record
        python examples/streaming_transcription.py -r

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
            print("  python examples/streaming_transcription.py [audio_file_path]")
            print("  python examples/streaming_transcription.py --record")
            print("  python examples/streaming_transcription.py -r")
            print()
            print("Options:")
            print("  --record, -r    Record new audio for transcription")
            print("  audio_file_path Path to existing audio file")
            sys.exit(1)
        else:
            audio_file_path = arg

    # Run the example
    asyncio.run(streaming_transcription_example(audio_file_path, record_new))
