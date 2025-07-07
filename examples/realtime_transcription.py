#!/usr/bin/env python3
"""
Realtime Audio Transcription Example
====================================

This example demonstrates how to use the OpenAI implementation of the mAIgic-assistant
speech API for real-time speech-to-text transcription.

The OpenAI implementation (speech-openai-impl) provides:
- Integration with OpenAI's Realtime API
- Real-time microphone audio capture
- Continuous transcription as you speak
- Automatic speech detection and segmentation

Requirements:
- OpenAI API key (set in OPENAI_API_KEY environment variable or .env file)
- Microphone access
- Python packages: speech-openai-impl, python-dotenv

Usage:
    python examples/realtime_transcription.py

The transcription will start immediately. Speak naturally and your speech will
be transcribed in real-time using OpenAI's speech recognition models.
Press Ctrl+C to stop.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add src to path for importing our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv

from speech_api import RealtimeSessionConfig
from speech_openai_impl import OpenAIConfig, OpenAISpeechToTextClient
from speech_openai_impl.audio_sources import PyAudioMicrophoneSource

# Configure logging to show only important messages
logging.basicConfig(level=logging.INFO)
# Suppress debug messages from the speech implementation modules
logging.getLogger("speech_openai_impl.sessions").setLevel(logging.WARNING)
logging.getLogger("speech_openai_impl.clients").setLevel(logging.WARNING)

# Load environment variables from .env file
load_dotenv()


async def realtime_transcription_example():
    """
    Demonstrates real-time speech transcription using microphone input.

    This function shows the complete workflow for setting up and running
    real-time transcription:

    1. Configure the OpenAI client
    2. Set up microphone audio source
    3. Configure transcription session
    4. Start real-time transcription
    5. Handle transcription events
    """
    print("Realtime Speech Transcription Example")
    print("=" * 50)
    print("This example demonstrates real-time speech-to-text transcription")
    print("using the OpenAI implementation of the mAIgic-assistant speech API.")
    print("\nFeatures:")
    print("- Real-time audio capture from your microphone")
    print("- Continuous transcription as you speak")
    print("- Automatic speech detection and segmentation")
    print("- High-quality transcription with punctuation")
    print("\nPress Ctrl+C to stop.\n")

    # Step 1: Load and validate configuration
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not found.")
        print("Please set your OpenAI API key in a .env file or environment variable.")
        return

    # Step 2: Create OpenAI configuration
    # The OpenAIConfig class handles authentication and API settings
    config = OpenAIConfig(api_key=api_key)

    # Step 3: Create the speech-to-text client
    # This client provides unified access to batch, streaming, and realtime transcription
    client = OpenAISpeechToTextClient(config)

    # Step 4: Set up microphone audio source
    # PyAudioMicrophoneSource captures audio from your default microphone
    # You can customize sample rate, channels, and other audio parameters
    mic_source = PyAudioMicrophoneSource(
        sample_rate=16000,  # 16kHz is optimal for speech recognition
        channels=1,         # Mono audio (single channel)
        chunk_size=1024     # Size of audio chunks to capture
    )

    # Step 5: Configure the realtime transcription session
    # RealtimeSessionConfig allows you to customize the transcription behavior
    session_config = RealtimeSessionConfig(
        model="gpt-4o-transcribe",           # OpenAI's transcription model
        enable_speech_detection=True,        # Automatic speech activity detection
        enable_partial_results=True,         # Get partial transcriptions while speaking
        language=None,                       # Auto-detect language (or specify like "en")
        prompt=None                          # Optional context/instruction prompt
    )

    print("Starting realtime transcription...")
    print("(Press Ctrl+C to stop)\n")

    try:
        # Step 6: Start transcription session
        # Use async context manager to ensure proper cleanup
        async with client:
            print("Listening... Speak now! (Transcription will be printed below.)")
            print("-" * 50)

            # Step 7: Process transcription events
            # The transcribe_realtime method returns an async generator that yields
            # TranscriptionEvent objects as speech is detected and transcribed
            final_transcription_count = 0

            async for event in client.transcribe_realtime(mic_source, session_config):
                # Each event contains:
                # - event.text: The transcribed text
                # - event.is_final: True if this is a complete utterance, False for partial
                # - event.timestamp: When the event was generated
                # - event.confidence: Confidence score (if available)

                if event.is_final:
                    # Final transcriptions are complete, punctuated utterances
                    final_transcription_count += 1
                    print(f"[{final_transcription_count}] {event.text}")
                # else:
                #     # Partial transcriptions show real-time progress while speaking
                #     print(f"[partial] {event.text}")

    except KeyboardInterrupt:
        print("\n\nTranscription stopped by user")
    except Exception as e:
        print(f"\nError occurred: {e}")
        # Uncomment the next lines for detailed error information during debugging
        # import traceback
        # traceback.print_exc()
    finally:
        print("\nTranscription session ended")
        print("\nThank you for using the realtime transcription example.")


def main():
    """
    Main entry point for the example.
    """
    # Check if running in an environment that supports asyncio
    try:
        asyncio.run(realtime_transcription_example())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Failed to run example: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


