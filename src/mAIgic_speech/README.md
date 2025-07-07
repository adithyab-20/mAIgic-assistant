# mAIgic Speech Component

Complete speech processing capabilities including speech-to-text, text-to-speech, and real-time transcription.

## Overview

This component provides:
- **Speech API** (`speech_api/`) - Abstract interfaces and type definitions
- **OpenAI Implementation** (`speech_openai_impl/`) - Concrete implementation using OpenAI's APIs

## Installation

Install the speech component as part of mAIgic Assistant:

```bash
# Install with speech capabilities
uv sync --extra speech

# Or using pip
pip install "maigic-assistant[speech]"
```

## Quick Start

```python
from mAIgic_speech.speech_api import AudioFormat
from mAIgic_speech.speech_openai_impl import OpenAISpeechToTextClient, OpenAIConfig

# Configure OpenAI
config = OpenAIConfig(api_key="your-api-key")

# Create client
client = OpenAISpeechToTextClient(config)

# Transcribe audio
async with client:
    transcript = await client.transcribe("audio.wav", AudioFormat.WAV)
    print(transcript)
```

## Dependencies

- `aiohttp>=3.8.0` - HTTP client for OpenAI API
- `websockets>=11.0.0` - WebSocket client for real-time transcription  
- `pyaudio>=0.2.14` - Audio input/output

## Components

### Speech API (`speech_api/`)
- **Interfaces** - Abstract base classes for all speech operations
- **Types** - Data structures and enums 
- **Exceptions** - Specific error types for speech operations

### OpenAI Implementation (`speech_openai_impl/`)
- **Clients** - HTTP-based transcription and synthesis
- **Sessions** - Real-time WebSocket transcription
- **Audio Sources** - Microphone and file input
- **Config** - OpenAI-specific configuration

## Examples

See the `examples/` directory for comprehensive usage examples:
- `batch_transcription.py` - Basic file transcription
- `streaming_transcription.py` - Real-time microphone transcription
- `realtime_transcription.py` - WebSocket-based bidirectional sessions 