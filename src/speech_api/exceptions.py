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


class APIError(SpeechAPIError):
    """Errors from the underlying API provider."""
    pass
