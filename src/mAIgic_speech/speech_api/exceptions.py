"""Custom exceptions for the Speech API."""


class SpeechAPIError(Exception):
    """Base exception for speech API errors."""
    pass


class TranscriptionError(SpeechAPIError):
    """Errors during speech-to-text processing."""
    pass


class SynthesisError(SpeechAPIError):
    """Errors during text-to-speech synthesis."""
    pass


class AudioError(SpeechAPIError):
    """Errors related to audio format or content."""
    pass


class AudioSourceError(AudioError):
    """Errors related to audio input sources."""
    pass


class APIError(SpeechAPIError):
    """Errors from the underlying API provider."""
    pass


class RealtimeSessionError(SpeechAPIError):
    """Errors related to realtime session management."""
    pass


class SessionConnectionError(RealtimeSessionError):
    """Errors when connecting to or maintaining realtime sessions."""
    pass


class SessionClosedError(RealtimeSessionError):
    """Errors when trying to use a closed session."""
    pass


class RealtimeTranscriptionError(TranscriptionError):
    """Errors specific to realtime transcription."""
    pass
