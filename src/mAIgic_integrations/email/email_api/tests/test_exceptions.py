"""
Tests for email API exceptions.
"""

import pytest

from ..exceptions import (
    HTTP_ERROR_MAP,
    EmailAPIError,
    EmailAttachmentError,
    EmailAuthenticationError,
    EmailAuthorizationError,
    EmailConfigurationError,
    EmailConnectionError,
    EmailFolderError,
    EmailNotFoundError,
    EmailProviderError,
    EmailQuotaExceededError,
    EmailRateLimitError,
    EmailReceiveError,
    EmailSearchError,
    EmailSendError,
    EmailTimeoutError,
    EmailValidationError,
)


class TestEmailAPIError:
    """Test base EmailAPIError exception."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = EmailAPIError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.error_code is None
        assert error.original_error is None

    def test_error_with_code(self):
        """Test error with error code."""
        error = EmailAPIError("Test error", error_code="E001")
        assert error.message == "Test error"
        assert error.error_code == "E001"
        assert error.original_error is None

    def test_error_with_original_error(self):
        """Test error with original exception."""
        original = ValueError("Original error")
        error = EmailAPIError("Wrapped error", original_error=original)
        assert error.message == "Wrapped error"
        assert error.original_error is original

    def test_error_with_all_fields(self):
        """Test error with all fields populated."""
        original = ConnectionError("Connection failed")
        error = EmailAPIError(
            "Email connection error",
            error_code="CONN_001",
            original_error=original
        )
        assert error.message == "Email connection error"
        assert error.error_code == "CONN_001"
        assert error.original_error is original


class TestSpecificExceptions:
    """Test specific email exception types."""

    def test_connection_error(self):
        """Test EmailConnectionError."""
        error = EmailConnectionError("Cannot connect to email server")
        assert isinstance(error, EmailAPIError)
        assert str(error) == "Cannot connect to email server"

    def test_authentication_error(self):
        """Test EmailAuthenticationError."""
        error = EmailAuthenticationError("Invalid credentials")
        assert isinstance(error, EmailAPIError)
        assert str(error) == "Invalid credentials"

    def test_authorization_error(self):
        """Test EmailAuthorizationError."""
        error = EmailAuthorizationError("Access denied")
        assert isinstance(error, EmailAPIError)
        assert str(error) == "Access denied"

    def test_not_found_error(self):
        """Test EmailNotFoundError."""
        error = EmailNotFoundError("Email not found")
        assert isinstance(error, EmailAPIError)
        assert str(error) == "Email not found"

    def test_validation_error(self):
        """Test EmailValidationError."""
        error = EmailValidationError("Invalid email format")
        assert isinstance(error, EmailAPIError)
        assert str(error) == "Invalid email format"

    def test_receive_error(self):
        """Test EmailReceiveError."""
        error = EmailReceiveError("Failed to retrieve emails")
        assert isinstance(error, EmailAPIError)
        assert str(error) == "Failed to retrieve emails"

    def test_search_error(self):
        """Test EmailSearchError."""
        error = EmailSearchError("Search query failed")
        assert isinstance(error, EmailAPIError)
        assert str(error) == "Search query failed"

    def test_attachment_error(self):
        """Test EmailAttachmentError."""
        error = EmailAttachmentError("Cannot download attachment")
        assert isinstance(error, EmailAPIError)
        assert str(error) == "Cannot download attachment"

    def test_folder_error(self):
        """Test EmailFolderError."""
        error = EmailFolderError("Folder operation failed")
        assert isinstance(error, EmailAPIError)
        assert str(error) == "Folder operation failed"

    def test_quota_exceeded_error(self):
        """Test EmailQuotaExceededError."""
        error = EmailQuotaExceededError("Storage quota exceeded")
        assert isinstance(error, EmailAPIError)
        assert str(error) == "Storage quota exceeded"

    def test_provider_error(self):
        """Test EmailProviderError."""
        error = EmailProviderError("Provider service error")
        assert isinstance(error, EmailAPIError)
        assert str(error) == "Provider service error"

    def test_configuration_error(self):
        """Test EmailConfigurationError."""
        error = EmailConfigurationError("Invalid configuration")
        assert isinstance(error, EmailAPIError)
        assert str(error) == "Invalid configuration"

    def test_timeout_error(self):
        """Test EmailTimeoutError."""
        error = EmailTimeoutError("Operation timed out")
        assert isinstance(error, EmailAPIError)
        assert str(error) == "Operation timed out"


class TestEmailSendError:
    """Test EmailSendError with failed recipients."""

    def test_basic_send_error(self):
        """Test basic send error."""
        error = EmailSendError("Failed to send email")
        assert isinstance(error, EmailAPIError)
        assert str(error) == "Failed to send email"
        assert error.failed_recipients == []

    def test_send_error_with_failed_recipients(self):
        """Test send error with failed recipients."""
        failed = ["invalid@example.com", "blocked@example.com"]
        error = EmailSendError("Partial send failure", failed_recipients=failed)
        assert error.failed_recipients == failed
        assert len(error.failed_recipients) == 2

    def test_send_error_with_additional_fields(self):
        """Test send error with error code and original error."""
        original = ConnectionError("SMTP connection failed")
        failed = ["bounce@example.com"]
        error = EmailSendError(
            "SMTP send failed",
            failed_recipients=failed,
            error_code="SMTP_001",
            original_error=original
        )
        assert error.failed_recipients == failed
        assert error.error_code == "SMTP_001"
        assert error.original_error is original


class TestEmailRateLimitError:
    """Test EmailRateLimitError with retry information."""

    def test_basic_rate_limit_error(self):
        """Test basic rate limit error."""
        error = EmailRateLimitError("Rate limit exceeded")
        assert isinstance(error, EmailAPIError)
        assert str(error) == "Rate limit exceeded"
        assert error.retry_after is None

    def test_rate_limit_error_with_retry_after(self):
        """Test rate limit error with retry timing."""
        error = EmailRateLimitError("Rate limit exceeded", retry_after=300)
        assert error.retry_after == 300
        assert str(error) == "Rate limit exceeded"

    def test_rate_limit_error_with_all_fields(self):
        """Test rate limit error with all fields."""
        error = EmailRateLimitError(
            "API rate limit exceeded",
            retry_after=600,
            error_code="RATE_001"
        )
        assert error.retry_after == 600
        assert error.error_code == "RATE_001"


class TestEmailProviderError:
    """Test EmailProviderError with provider response."""

    def test_basic_provider_error(self):
        """Test basic provider error."""
        error = EmailProviderError("Provider service unavailable")
        assert isinstance(error, EmailAPIError)
        assert str(error) == "Provider service unavailable"
        assert error.provider_response is None

    def test_provider_error_with_response(self):
        """Test provider error with provider response."""
        response = '{"error": "internal_server_error", "code": 500}'
        error = EmailProviderError("Server error", provider_response=response)
        assert error.provider_response == response
        assert str(error) == "Server error"

    def test_provider_error_with_all_fields(self):
        """Test provider error with all fields."""
        response = '{"error": "service_unavailable"}'
        error = EmailProviderError(
            "Provider temporarily unavailable",
            provider_response=response,
            error_code="PROV_503"
        )
        assert error.provider_response == response
        assert error.error_code == "PROV_503"


class TestHTTPErrorMapping:
    """Test HTTP status code to exception mapping."""

    def test_http_error_map_contents(self):
        """Test that HTTP error map contains expected mappings."""
        expected_mappings = {
            400: EmailValidationError,
            401: EmailAuthenticationError,
            403: EmailAuthorizationError,
            404: EmailNotFoundError,
            413: EmailQuotaExceededError,
            429: EmailRateLimitError,
            500: EmailProviderError,
            502: EmailConnectionError,
            503: EmailConnectionError,
            504: EmailTimeoutError,
        }

        assert HTTP_ERROR_MAP == expected_mappings

    def test_http_error_map_usage(self):
        """Test using HTTP error map to create exceptions."""
        # Test 401 -> EmailAuthenticationError
        error_class = HTTP_ERROR_MAP[401]
        error = error_class("Authentication failed")
        assert isinstance(error, EmailAuthenticationError)

        # Test 404 -> EmailNotFoundError
        error_class = HTTP_ERROR_MAP[404]
        error = error_class("Resource not found")
        assert isinstance(error, EmailNotFoundError)

        # Test 429 -> EmailRateLimitError
        error_class = HTTP_ERROR_MAP[429]
        error = error_class("Too many requests", retry_after=60)
        assert isinstance(error, EmailRateLimitError)
        assert error.retry_after == 60

    def test_unmapped_status_codes(self):
        """Test that unmapped status codes raise KeyError."""
        with pytest.raises(KeyError):
            _ = HTTP_ERROR_MAP[999]  # Non-existent status code


class TestExceptionInheritance:
    """Test exception inheritance hierarchy."""

    def test_all_exceptions_inherit_from_base(self):
        """Test that all email exceptions inherit from EmailAPIError."""
        exception_classes = [
            EmailConnectionError,
            EmailAuthenticationError,
            EmailAuthorizationError,
            EmailNotFoundError,
            EmailValidationError,
            EmailSendError,
            EmailReceiveError,
            EmailSearchError,
            EmailAttachmentError,
            EmailFolderError,
            EmailQuotaExceededError,
            EmailRateLimitError,
            EmailProviderError,
            EmailConfigurationError,
            EmailTimeoutError,
        ]

        for exc_class in exception_classes:
            assert issubclass(exc_class, EmailAPIError)
            assert issubclass(exc_class, Exception)

    def test_can_catch_with_base_exception(self):
        """Test that specific exceptions can be caught with base exception."""
        try:
            raise EmailConnectionError("Connection failed")
        except EmailAPIError as e:
            assert isinstance(e, EmailConnectionError)
            assert isinstance(e, EmailAPIError)

        try:
            raise EmailSendError("Send failed")
        except EmailAPIError as e:
            assert isinstance(e, EmailSendError)
            assert isinstance(e, EmailAPIError)
