# speech_openai_impl Test Suite

This directory contains comprehensive unit tests for the `speech_openai_impl` component.

## Overview

The test suite covers all major classes and functionality:

- **`test_config.py`** - Tests for `OpenAIConfig` class validation
- **`test_audio_sources.py`** - Tests for audio source implementations (`FileAudioSource`, `PyAudioMicrophoneSource`)
- **`test_clients.py`** - Tests for client classes (`OpenAISpeechToTextClient`, `OpenAITextToSpeechClient`)
- **`test_sessions.py`** - Tests for session classes (`OpenAIRealtimeTranscriptionSession`, `RealtimeSpeechToSpeechSession`, `OpenAIRealtimeClient`)
- **`conftest.py`** - Shared fixtures and test utilities

## Running Tests

### Quick Test Run (No Coverage)
```bash
# From project root
python test_speech_openai.py
```

### Individual Test Files
```bash
# Config tests (fastest)
python -m pytest src/speech_openai_impl/tests/test_config.py -v

# Audio source tests
python -m pytest src/speech_openai_impl/tests/test_audio_sources.py -v

# Client tests
python -m pytest src/speech_openai_impl/tests/test_clients.py -v

# Session tests
python -m pytest src/speech_openai_impl/tests/test_sessions.py -v
```

### Full Test Suite with Coverage
```bash
python -m pytest src/speech_openai_impl/tests/ -v
```

## Test Structure

### Mocking Strategy

The tests use extensive mocking to isolate units under test:

- **HTTP Requests**: Mock `aiohttp.ClientSession` for API calls
- **WebSocket Connections**: Mock `websockets.connect()` for realtime sessions
- **PyAudio**: Mock `pyaudio` module for microphone tests
- **File I/O**: Use temporary files for file-based audio sources

### Test Coverage

The tests cover:

✅ **Configuration Validation**
- Valid/invalid API keys
- Timeout validation
- Parameter defaults

✅ **Audio Sources**
- File-based audio streaming
- Microphone capture simulation
- Error handling and cleanup
- Context manager behavior

✅ **HTTP Clients**
- Successful API requests
- Error handling (401, 429, network errors)
- Request parameter passing
- Streaming responses

✅ **Realtime Sessions**
- WebSocket connection management
- Message sending/receiving
- Event parsing and handling
- Session lifecycle management

✅ **Context Managers**
- Proper resource cleanup
- Exception handling
- Async context manager protocols

## Test Fixtures

### `conftest.py` provides:

- `sample_config`: Basic OpenAI configuration
- `sample_audio_chunk`: Test audio data
- `mock_aiohttp_session`: Mock HTTP session
- `mock_websocket`: Mock WebSocket connection
- `mock_helpers`: Utilities for creating test events

## Async Testing

All async methods are properly tested using:
- `pytest-asyncio` for async test support
- Proper mocking of async methods with `AsyncMock`
- Event loop management for concurrent operations

## Dependencies

Test dependencies (included in project dev dependencies):
- `pytest`
- `pytest-asyncio`
- `pytest-cov`

## Notes

- Tests use mocking extensively to avoid external dependencies
- File-based tests use temporary files for isolation
- Network mocking prevents actual API calls during testing
- Audio hardware mocking enables testing without microphone access 