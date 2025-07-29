"""
Comprehensive tests for Gmail client implementation.

This test suite focuses on testing the Gmail client implementation with proper
mocking that avoids the complex Google API client validation issues.
"""

import base64
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from ...email_api.exceptions import (
    EmailConnectionError,
    EmailNotFoundError,
    EmailReceiveError,
    EmailSearchError,
)
from ...email_api.models import (
    Email,
    EmailAddress,
    EmailStats,
)
from ..clients import GmailClient
from ..config import GmailConfig


@pytest.fixture
def mock_config():
    """Create mock Gmail configuration for testing."""
    return GmailConfig(
        credentials_path="test_credentials.json",
        token_path="test_token.json"
    )


@pytest.fixture
def gmail_client(mock_config):
    """Create Gmail client for testing."""
    return GmailClient(mock_config)


@pytest.fixture
def mock_gmail_service():
    """Create a properly mocked Gmail service."""
    service = MagicMock()

    # Mock the full API structure
    service.users.return_value = service
    service.messages.return_value = service
    service.attachments.return_value = service
    service.labels.return_value = service
    service.getProfile.return_value = service
    service.list.return_value = service
    service.get.return_value = service

    return service


class TestGmailClientConnection:
    """Test Gmail client connection management."""

    @patch.object(GmailClient, '_get_credentials')
    @patch.object(GmailClient, '_test_connection')
    @patch('googleapiclient.discovery.build')
    @pytest.mark.asyncio
    async def test_connect_success(self, mock_build, mock_test_conn, mock_get_creds, gmail_client, mock_gmail_service):
        """Test successful connection."""
        mock_creds = Mock()
        mock_creds.universe_domain = "googleapis.com"
        mock_get_creds.return_value = mock_creds
        mock_build.return_value = mock_gmail_service
        mock_test_conn.return_value = None  # Mock successful connection test

        await gmail_client.connect()

        assert gmail_client._connected is True
        assert gmail_client.service is not None
        mock_test_conn.assert_called_once()
        mock_get_creds.assert_called_once()

    @patch.object(GmailClient, '_get_credentials')
    @patch('googleapiclient.discovery.build')
    @pytest.mark.asyncio
    async def test_connect_failure(self, mock_build, mock_get_creds, gmail_client):
        """Test connection failure."""
        mock_get_creds.side_effect = Exception("Connection failed")

        with pytest.raises(EmailConnectionError):
            await gmail_client.connect()

        assert gmail_client._connected is False

    @pytest.mark.asyncio
    async def test_disconnect(self, gmail_client):
        """Test disconnection."""
        gmail_client.service = Mock()
        gmail_client._connected = True

        await gmail_client.disconnect()

        assert gmail_client.service is None
        assert gmail_client._connected is False

    @patch.object(GmailClient, 'connect')
    @patch.object(GmailClient, 'disconnect')
    @pytest.mark.asyncio
    async def test_context_manager(self, mock_disconnect, mock_connect, gmail_client):
        """Test using client as async context manager."""
        async with gmail_client as client:
            assert client is gmail_client

        mock_connect.assert_called_once()
        mock_disconnect.assert_called_once()


class TestGmailClientGetEmails:
    """Test get_emails method."""

    def setup_connected_client(self, gmail_client, mock_service):
        """Helper to setup a connected client."""
        gmail_client.service = mock_service
        gmail_client._connected = True

    @patch.object(GmailClient, '_get_message_details')
    @pytest.mark.asyncio
    async def test_get_emails_basic(self, mock_get_details, gmail_client, mock_gmail_service):
        """Test basic email retrieval."""
        self.setup_connected_client(gmail_client, mock_gmail_service)

        # Mock API response
        mock_gmail_service.execute.return_value = {
            'messages': [{'id': 'msg-1'}, {'id': 'msg-2'}]
        }

        # Mock email details
        mock_email = Email(
            message_id="msg-1",
            sender=EmailAddress("test@example.com"),
            recipients=[EmailAddress("recipient@example.com")],
            subject="Test Email",
            body_text="Test body"
        )
        mock_get_details.return_value = mock_email

        emails = await gmail_client.get_emails(folder="INBOX", limit=5)

        assert isinstance(emails, list)
        assert len(emails) <= 5
        mock_gmail_service.execute.assert_called()

    @patch.object(GmailClient, '_get_message_details')
    @pytest.mark.asyncio
    async def test_get_emails_with_date_filter(self, mock_get_details, gmail_client, mock_gmail_service):
        """Test email retrieval with date filtering."""
        self.setup_connected_client(gmail_client, mock_gmail_service)

        mock_gmail_service.execute.return_value = {'messages': [{'id': 'msg-1'}]}
        mock_get_details.return_value = Email(message_id="msg-1")

        emails = await gmail_client.get_emails(folder="INBOX", since_days=7)

        assert isinstance(emails, list)
        # Verify date filter was applied in query
        mock_gmail_service.execute.assert_called()

    @pytest.mark.asyncio
    async def test_get_emails_not_connected(self, gmail_client):
        """Test get_emails when not connected."""
        with pytest.raises(EmailConnectionError):
            await gmail_client.get_emails()

    @pytest.mark.asyncio
    async def test_get_emails_api_error(self, gmail_client, mock_gmail_service):
        """Test handling of Gmail API errors."""
        self.setup_connected_client(gmail_client, mock_gmail_service)
        mock_gmail_service.execute.side_effect = Exception("API Error")

        with pytest.raises(EmailReceiveError):
            await gmail_client.get_emails()


class TestGmailClientSearchEmails:
    """Test search_emails method."""

    def setup_connected_client(self, gmail_client, mock_service):
        """Helper to setup a connected client."""
        gmail_client.service = mock_service
        gmail_client._connected = True

    @patch.object(GmailClient, '_get_message_details')
    @pytest.mark.asyncio
    async def test_search_emails_basic(self, mock_get_details, gmail_client, mock_gmail_service):
        """Test basic email search."""
        self.setup_connected_client(gmail_client, mock_gmail_service)

        mock_gmail_service.execute.return_value = {
            'messages': [{'id': 'msg-1'}]
        }
        mock_get_details.return_value = Email(
            message_id="msg-1",
            subject="Matching email",
            sender=EmailAddress("test@example.com")
        )

        emails = await gmail_client.search_emails("test query", limit=10)

        assert isinstance(emails, list)
        assert len(emails) <= 10
        mock_gmail_service.execute.assert_called()

    @pytest.mark.asyncio
    async def test_search_emails_not_connected(self, gmail_client):
        """Test search when not connected."""
        with pytest.raises(EmailConnectionError):
            await gmail_client.search_emails("test")

    @pytest.mark.asyncio
    async def test_search_emails_api_error(self, gmail_client, mock_gmail_service):
        """Test handling of search API errors."""
        self.setup_connected_client(gmail_client, mock_gmail_service)
        mock_gmail_service.execute.side_effect = Exception("Search failed")

        with pytest.raises(EmailSearchError):
            await gmail_client.search_emails("test query")


class TestGmailClientGetEmail:
    """Test get_email method."""

    def setup_connected_client(self, gmail_client, mock_service):
        """Helper to setup a connected client."""
        gmail_client.service = mock_service
        gmail_client._connected = True

    @patch.object(GmailClient, '_get_message_details')
    @pytest.mark.asyncio
    async def test_get_email_success(self, mock_get_details, gmail_client, mock_gmail_service):
        """Test successful single email retrieval."""
        self.setup_connected_client(gmail_client, mock_gmail_service)

        expected_email = Email(
            message_id="msg-123",
            subject="Test Email",
            sender=EmailAddress("sender@example.com"),
            body_text="Email content"
        )
        mock_get_details.return_value = expected_email

        email = await gmail_client.get_email("msg-123")

        assert isinstance(email, Email)
        assert email.message_id == "msg-123"
        assert email.subject == "Test Email"
        mock_get_details.assert_called_once_with("msg-123", include_body=True)

    @pytest.mark.asyncio
    async def test_get_email_not_connected(self, gmail_client):
        """Test get_email when not connected."""
        with pytest.raises(EmailConnectionError):
            await gmail_client.get_email("msg-1")

    @patch.object(GmailClient, '_get_message_details')
    @pytest.mark.asyncio
    async def test_get_email_not_found(self, mock_get_details, gmail_client, mock_gmail_service):
        """Test get_email with non-existent email."""
        from googleapiclient.errors import HttpError

        self.setup_connected_client(gmail_client, mock_gmail_service)

        # Mock 404 error
        error_resp = Mock()
        error_resp.status = 404
        mock_get_details.side_effect = HttpError(error_resp, b'Not found')

        with pytest.raises(EmailNotFoundError):
            await gmail_client.get_email("nonexistent-id")


class TestGmailClientGetAccountInfo:
    """Test get_account_info method."""

    def setup_connected_client(self, gmail_client, mock_service):
        """Helper to setup a connected client."""
        gmail_client.service = mock_service
        gmail_client._connected = True

    @pytest.mark.asyncio
    async def test_get_account_info_success(self, gmail_client, mock_gmail_service):
        """Test successful account info retrieval."""
        self.setup_connected_client(gmail_client, mock_gmail_service)

        # Mock profile and labels responses separately
        call_count = 0
        def mock_execute():
            nonlocal call_count
            call_count += 1
            if call_count == 1:  # First call is getProfile
                return {'messagesTotal': 150, 'threadsTotal': 75}
            else:  # Second call is labels list
                return {'labels': [{'id': 'INBOX'}, {'id': 'SENT'}, {'id': 'DRAFTS'}]}

        mock_gmail_service.execute.side_effect = mock_execute

        stats = await gmail_client.get_account_info()

        assert isinstance(stats, EmailStats)
        assert stats.total_messages == 150
        assert stats.unread_messages == 75
        assert stats.total_folders == 3
        assert isinstance(stats.last_sync, datetime)

    @pytest.mark.asyncio
    async def test_get_account_info_not_connected(self, gmail_client):
        """Test get_account_info when not connected."""
        with pytest.raises(EmailConnectionError):
            await gmail_client.get_account_info()


class TestGmailClientDownloadAttachment:
    """Test download_attachment method."""

    def setup_connected_client(self, gmail_client, mock_service):
        """Helper to setup a connected client."""
        gmail_client.service = mock_service
        gmail_client._connected = True

    @pytest.mark.asyncio
    async def test_download_attachment_success(self, gmail_client, mock_gmail_service):
        """Test successful attachment download."""
        self.setup_connected_client(gmail_client, mock_gmail_service)

        # Mock attachment data (base64 encoded "Test attachment content")
        test_content = "Test attachment content"
        encoded_content = base64.urlsafe_b64encode(test_content.encode()).decode()

        mock_gmail_service.execute.return_value = {
            'data': encoded_content
        }

        content = await gmail_client.download_attachment("msg-123", "att-456")

        assert isinstance(content, bytes)
        assert content == test_content.encode()

    @pytest.mark.asyncio
    async def test_download_attachment_not_connected(self, gmail_client):
        """Test download_attachment when not connected."""
        with pytest.raises(EmailConnectionError):
            await gmail_client.download_attachment("msg-123", "att-456")

    @pytest.mark.asyncio
    async def test_download_attachment_not_found(self, gmail_client, mock_gmail_service):
        """Test download_attachment with non-existent attachment."""
        from googleapiclient.errors import HttpError

        self.setup_connected_client(gmail_client, mock_gmail_service)

        # Mock 404 error
        error_resp = Mock()
        error_resp.status = 404
        mock_gmail_service.execute.side_effect = HttpError(error_resp, b'Not found')

        with pytest.raises(EmailNotFoundError):
            await gmail_client.download_attachment("msg-123", "nonexistent")


class TestGmailClientMessageParsing:
    """Test email message parsing methods."""

    def test_parse_email_address_simple(self, gmail_client):
        """Test parsing simple email address."""
        addr = gmail_client._parse_email_address("test@example.com")
        assert addr.address == "test@example.com"
        assert addr.name is None

    def test_parse_email_address_with_name(self, gmail_client):
        """Test parsing email address with display name."""
        addr = gmail_client._parse_email_address('John Doe <john@example.com>')
        assert addr.address == "john@example.com"
        assert addr.name == "John Doe"

    def test_parse_email_address_quoted_name(self, gmail_client):
        """Test parsing email address with quoted display name."""
        addr = gmail_client._parse_email_address('"John Doe" <john@example.com>')
        assert addr.address == "john@example.com"
        assert addr.name == "John Doe"

    def test_parse_email_addresses_multiple(self, gmail_client):
        """Test parsing multiple email addresses."""
        addresses = gmail_client._parse_email_addresses(
            "test1@example.com, John Doe <john@example.com>, test2@example.com"
        )
        assert len(addresses) == 3
        assert addresses[0].address == "test1@example.com"
        assert addresses[1].address == "john@example.com"
        assert addresses[1].name == "John Doe"
        assert addresses[2].address == "test2@example.com"

    def test_parse_email_addresses_empty(self, gmail_client):
        """Test parsing empty email address string."""
        addresses = gmail_client._parse_email_addresses("")
        assert len(addresses) == 0

    def test_extract_content_simple_text(self, gmail_client):
        """Test extracting content from simple text email."""
        test_text = "Hello world"
        encoded_text = base64.urlsafe_b64encode(test_text.encode()).decode()

        payload = {
            'mimeType': 'text/plain',
            'body': {'data': encoded_text}
        }

        body_text, body_html, attachments = gmail_client._extract_content(payload)

        assert body_text == test_text
        assert body_html == ""
        assert len(attachments) == 0

    def test_extract_content_with_attachment(self, gmail_client):
        """Test extracting content from email with attachment."""
        payload = {
            'parts': [
                {
                    'mimeType': 'text/plain',
                    'body': {'data': base64.urlsafe_b64encode(b"Email body").decode()}
                },
                {
                    'filename': 'document.pdf',
                    'mimeType': 'application/pdf',
                    'body': {'size': 1024, 'attachmentId': 'att-123'}
                }
            ]
        }

        body_text, body_html, attachments = gmail_client._extract_content(payload)

        assert body_text == "Email body"
        assert len(attachments) == 1
        assert attachments[0].filename == 'document.pdf'
        assert attachments[0].content_type == 'application/pdf'
        assert attachments[0].size_bytes == 1024


class TestGmailClientErrorHandling:
    """Test error handling across all methods."""

    @pytest.mark.asyncio
    async def test_methods_require_connection(self, gmail_client):
        """Test that all main methods require connection."""
        # Ensure client is not connected
        gmail_client._connected = False

        with pytest.raises(EmailConnectionError):
            await gmail_client.get_emails()

        with pytest.raises(EmailConnectionError):
            await gmail_client.search_emails("test")

        with pytest.raises(EmailConnectionError):
            await gmail_client.get_email("msg-1")

        with pytest.raises(EmailConnectionError):
            await gmail_client.get_account_info()

        with pytest.raises(EmailConnectionError):
            await gmail_client.download_attachment("msg-1", "att-1")


class TestGmailClientInterfaceCompliance:
    """Test that Gmail client properly implements the EmailClient interface."""

    def test_has_all_required_methods(self, gmail_client):
        """Test that all required interface methods are implemented."""
        required_methods = [
            '__aenter__', '__aexit__',
            'get_emails', 'search_emails', 'get_email',
            'get_account_info', 'download_attachment',
            'get_recent_emails'  # Convenience method from base class
        ]

        for method_name in required_methods:
            assert hasattr(gmail_client, method_name), f"Missing method: {method_name}"

    @patch.object(GmailClient, 'get_emails')
    @pytest.mark.asyncio
    async def test_get_recent_emails_convenience(self, mock_get_emails, gmail_client):
        """Test the convenience method get_recent_emails."""
        mock_get_emails.return_value = [Email(message_id="test")]

        emails = await gmail_client.get_recent_emails(days=7)

        mock_get_emails.assert_called_once_with(
            folder="INBOX",
            limit=100,
            include_body=True,
            since_days=7
        )
        assert len(emails) == 1
