# Speech API Examples

This directory contains comprehensive examples demonstrating the different transcription methods available in the mAIgic-assistant speech API.

## Prerequisites

1. **OpenAI API Key**: Set your OpenAI API key in a `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

2. **Dependencies**: Install required dependencies:
   ```bash
   # Core dependencies (automatically installed with the package)
   pip install -e ..

   # For audio recording functionality (optional)
   pip install pyaudio
   ```

   **Note**: If you don't install `pyaudio`, the examples will still work with existing audio files, but recording functionality won't be available.

3. **Audio Files**: You can either:
   - Use the built-in recording functionality (requires `pyaudio`)
   - Provide your own audio files in WAV, MP3, FLAC, or OGG format

## Examples Overview

### 1. Batch Transcription (`batch_transcription.py`)

Demonstrates complete audio file transcription with full results returned at once.

**Usage:**
```bash
# With existing audio file
python examples/batch_transcription.py path/to/your/audio.wav

# Record new audio
python examples/batch_transcription.py --record
python examples/batch_transcription.py -r

# Interactive mode (prompts for recording if no file provided)
python examples/batch_transcription.py
```

**Features:**
- Complete transcription of entire audio file
- High accuracy with full context
- Support for multiple audio formats
- Built-in audio recording capability
- Automatic cleanup of temporary files

### 2. Streaming Transcription (`streaming_transcription.py`)

Shows progressive transcription with partial results using OpenAI's native streaming API.

**Usage:**
```bash
# With existing audio file
python examples/streaming_transcription.py path/to/your/audio.wav

# Record new audio
python examples/streaming_transcription.py --record
python examples/streaming_transcription.py -r

# Interactive mode
python examples/streaming_transcription.py
```

**Features:**
- Progressive results using OpenAI's streaming API
- Real-time feedback as transcription is processed
- Uses newer `gpt-4o-mini-transcribe` model
- Built-in audio recording capability
- Fallback to batch transcription if streaming fails

### 3. Realtime Transcription (`realtime_transcription.py`)

Demonstrates live audio transcription from microphone input using WebSocket connections.

**Usage:**
```bash
python examples/realtime_transcription.py
```

**Features:**
- Live microphone transcription
- Real-time WebSocket communication
- Immediate partial and final results
- Voice activity detection
- Interactive start/stop control

## Audio Recording

The batch and streaming examples include built-in audio recording functionality:

### Recording Features
- **Configurable Duration**: Specify recording length (default: 10s for batch, 15s for streaming)
- **Quality Settings**: 16kHz sample rate, mono channel, 16-bit depth
- **User-Friendly Interface**: Countdown timer and clear prompts
- **Automatic Cleanup**: Temporary files are automatically removed
- **Cross-Platform**: Works on Windows, macOS, and Linux (with `pyaudio`)

### Recording Process
1. **Countdown**: 3-second countdown before recording starts
2. **Visual Feedback**: Clear indicators showing recording status
3. **Automatic Stop**: Recording stops after specified duration
4. **File Creation**: Audio saved to temporary WAV file
5. **Processing**: File automatically processed for transcription
6. **Cleanup**: Temporary file removed after processing

### Installation for Recording
```bash
# macOS
brew install portaudio
pip install pyaudio

# Ubuntu/Debian
sudo apt-get install portaudio19-dev
pip install pyaudio

# Windows
pip install pyaudio
```

## When to Use Each Method

### Batch Transcription
- **Best for**: Complete audio files, highest accuracy needed
- **Use cases**: Meeting recordings, interviews, voicemails
- **Pros**: Full context, highest accuracy, simple to use
- **Cons**: Waits for complete processing

### Streaming Transcription  
- **Best for**: Getting progressive feedback during transcription
- **Use cases**: Interactive applications, progress monitoring, user feedback
- **Pros**: Progressive results, newer model, immediate feedback
- **Cons**: Still processes complete file, requires network streaming support

### Realtime Transcription
- **Best for**: Live conversations, interactive applications
- **Use cases**: Live captions, voice commands, real-time notes
- **Pros**: Immediate results, interactive, live audio
- **Cons**: Requires continuous audio input, network dependent

## Error Handling

All examples include comprehensive error handling for:
- Missing API keys
- File not found errors
- Network connectivity issues
- Audio format problems
- Recording device issues
- Temporary file cleanup failures

## Customization

You can customize the examples by modifying:
- **Audio formats**: Change `AudioFormat` enum values
- **Chunk sizes**: Adjust streaming chunk sizes for performance
- **Recording parameters**: Modify sample rate, channels, duration
- **Language settings**: Add language specification parameters
- **Output formatting**: Customize result display and logging

## Testing the Examples

To test the batch and streaming examples, you'll need audio files:

1. **Record a test audio file**:
   - Use your computer's built-in recording app
   - Record a short message (10-30 seconds)
   - Save as WAV format for best compatibility

2. **Supported formats**: WAV, MP3, FLAC, OGG

3. **Example command**:
   ```bash
   uv run python examples/batch_transcription.py my_recording.wav
   ```

For realtime transcription, no audio file is needed - it uses your microphone directly.

## Choosing the Right Transcription Method

### Batch Transcription
**Best for**: Complete audio files, high accuracy requirements, non-time-sensitive processing

- Processes entire audio file at once
- Highest accuracy and quality
- Full file must be available before processing
- Most cost-effective for large files
- Returns complete transcription when finished

### Streaming Transcription  
**Best for**: Large audio files, progressive results, memory-constrained environments

- Processes audio in chunks with progressive results
- Memory-efficient for very large files
- Provides intermediate results during processing
- Good balance between responsiveness and accuracy
- Useful for monitoring long-running transcriptions

### Realtime Transcription
**Best for**: Live audio, interactive applications, immediate feedback

- Processes live microphone input
- Lowest latency, immediate results
- Requires continuous audio stream
- Ideal for live conversations, meetings, dictation
- Automatic speech activity detection

## Sample Outputs

### Realtime Transcription Output
```
Listening... Speak now! (Transcription will be printed below.)
--------------------------------------------------
[1] Hello, my name is John.
[2] How are you doing today?
[3] This is a real-time transcription example.
```

### Batch Transcription Output
```
Transcription completed successfully!
==================================================
TRANSCRIPTION RESULT:
==================================================
Hello, this is a test recording for batch transcription. 
The audio quality is good and the transcription should be accurate.
==================================================

Detected language: en
Transcription length: 89 characters
Word count (approximate): 16 words
```

### Streaming Transcription Output
```
Results will be displayed progressively as audio is processed...
==================================================
[Chunk 1] Hello, this is a test
[Chunk 2] recording for streaming transcription.
[Chunk 3] The audio is processed in chunks
[Chunk 4] providing progressive results.
==================================================
Streaming transcription completed!
==================================================
COMPLETE TRANSCRIPTION:
------------------------------
Hello, this is a test recording for streaming transcription. The audio is processed in chunks providing progressive results.
------------------------------

Statistics:
Total chunks processed: 4
Total transcription length: 134 characters
Word count (approximate): 21 words
```

## Running Examples

All examples can be run from the project root directory:

```bash
uv run python examples/realtime_transcription.py
```

## API Documentation

Each example includes detailed inline documentation showing:

- **Step-by-step setup**: How to configure clients and sessions
- **Configuration options**: Available parameters and their effects
- **Event handling**: How to process different types of events
- **Error handling**: Proper exception handling patterns
- **Resource cleanup**: Using async context managers correctly

## Customization

The examples are designed to be easily customizable. Common modifications:

### Audio Source Configuration
```python
# Customize microphone settings
mic_source = PyAudioMicrophoneSource(
    sample_rate=16000,  # Audio quality (8000, 16000, 44100)
    channels=1,         # Mono (1) or stereo (2)
    chunk_size=1024,    # Buffer size
    device_index=None   # Specific microphone device
)
```

### Session Configuration
```python
# Customize transcription behavior
session_config = RealtimeSessionConfig(
    model="gpt-4o-transcribe",      # Model selection
    language="en",                   # Language hint (or None for auto-detect)
    enable_speech_detection=True,    # Automatic speech activity detection
    enable_partial_results=True,     # Real-time partial transcriptions
    prompt="Technical meeting notes" # Context for better accuracy
)
```

## Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY not found"**
   - Ensure your API key is set in environment variables or `.env` file
   - Verify the key is valid and has appropriate permissions

2. **Microphone not detected**
   - Check microphone permissions in your OS settings
   - Verify PyAudio is properly installed: `pip install pyaudio`
   - List available devices: `python -c "import pyaudio; p=pyaudio.PyAudio(); [print(i, p.get_device_info_by_index(i)['name']) for i in range(p.get_device_count())]"`

3. **No transcription events**
   - Speak clearly and loudly enough for detection
   - Check internet connection (transcription happens server-side)
   - Verify your OpenAI API key has access to realtime features

4. **Import errors**
   - Run examples from the project root directory
   - Ensure the package is installed: `pip install -e .`

### Debug Mode

To enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```


## Additional Resources

- [OpenAI Realtime API Documentation](https://platform.openai.com/docs/guides/realtime)
- [mAIgic-assistant API Reference](../README.md)
- [Speech API Interfaces](../src/speech_api/interfaces.py) 