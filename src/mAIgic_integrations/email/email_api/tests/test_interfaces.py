"""
Tests for email API interfaces (abstract classes).
"""

import inspect

import pytest

from ..interfaces import EmailClient, EmailProvider
from ..models import Email, EmailStats


class TestEmailClientInterface:
    """Test EmailClient abstract interface."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that EmailClient cannot be instantiated directly."""
        with pytest.raises(TypeError):
            EmailClient()

    def test_has_expected_abstract_methods(self):
        """Test that EmailClient has exactly the expected abstract methods."""
        abstract_methods = [name for name, method in inspect.getmembers(EmailClient)
                          if getattr(method, "__isabstractmethod__", False)]

        expected_methods = [
            "__aenter__", "__aexit__",
            "get_emails", "search_emails", "get_recent_emails", "get_email",
            "get_account_info", "download_attachment"
        ]
        assert sorted(abstract_methods) == sorted(expected_methods)

    def test_complete_implementation_works(self):
        """Test that complete implementation can be instantiated."""

        class MockEmailClient(EmailClient):
            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

            async def get_emails(self, folder="INBOX", limit=50, include_body=True, since_days=None):
                return []

            async def search_emails(self, query: str, limit=10):
                return []

            async def get_recent_emails(self, days=7):
                return []

            async def get_email(self, message_id: str):
                return Email(message_id=message_id)

            async def get_account_info(self):
                return EmailStats(total_messages=0, unread_messages=0, total_folders=0, storage_used_mb=0.0)

            async def download_attachment(self, message_id: str, attachment_id: str):
                return b"content"

        client = MockEmailClient()
        assert isinstance(client, EmailClient)


class TestEmailProviderInterface:
    """Test EmailProvider abstract interface."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that EmailProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            EmailProvider()

    def test_complete_implementation_works(self):
        """Test that complete implementation can be instantiated."""

        class MockEmailProvider(EmailProvider):
            def create_client(self, **config):
                return None

            def validate_config(self, **config):
                return True

            def get_required_config_keys(self):
                return ["api_key"]

            def get_optional_config_keys(self):
                return ["timeout"]

            def get_config_description(self):
                return "Mock email provider configuration"

        provider = MockEmailProvider()
        assert isinstance(provider, EmailProvider)


class TestEmailClientImplementation:
    """Test a working implementation of EmailClient."""

    class WorkingEmailClient(EmailClient):
        def __init__(self):
            self.emails = [
                Email(message_id="1", subject="Test Email 1"),
                Email(message_id="2", subject="Test Email 2"),
            ]

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

        async def get_emails(self, folder="INBOX", limit=50, include_body=True, since_days=None):
            return self.emails[:limit]

        async def search_emails(self, query: str, limit=10):
            results = [email for email in self.emails if query.lower() in email.subject.lower()]
            return results[:limit]

        async def get_recent_emails(self, days=7):
            # For testing purposes, return all emails as "recent"
            return self.emails

        async def get_email(self, message_id: str):
            for email in self.emails:
                if email.message_id == message_id:
                    return email
            raise ValueError(f"Email {message_id} not found")

        async def get_account_info(self):
            return EmailStats(total_messages=len(self.emails), unread_messages=1, total_folders=3, storage_used_mb=5.0)

        async def download_attachment(self, message_id: str, attachment_id: str):
            return b"mock attachment content"

    @pytest.mark.asyncio
    async def test_basic_functionality(self):
        """Test basic email client functionality."""
        client = self.WorkingEmailClient()

        # Test get_emails
        emails = await client.get_emails(limit=1)
        assert len(emails) == 1
        assert emails[0].message_id == "1"

        # Test search_emails
        results = await client.search_emails("Test")
        assert len(results) == 2

        # Test get_recent_emails
        recent = await client.get_recent_emails(days=7)
        assert len(recent) == 2

        # Test get_email
        email = await client.get_email("2")
        assert email.subject == "Test Email 2"

        # Test get_account_info
        stats = await client.get_account_info()
        assert stats.total_messages == 2

        # Test download_attachment
        content = await client.download_attachment("1", "att-1")
        assert content == b"mock attachment content"

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test using the client as a context manager."""
        client = self.WorkingEmailClient()
        async with client as c:
            emails = await c.get_emails()
            assert len(emails) == 2

    @pytest.mark.asyncio
    async def test_get_recent_emails_convenience_method(self):
        """Test the get_recent_emails method."""
        client = self.WorkingEmailClient()
        emails = await client.get_recent_emails(days=7)
        assert len(emails) == 2  # All emails in our mock
