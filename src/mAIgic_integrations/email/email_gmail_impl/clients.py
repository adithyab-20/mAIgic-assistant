"""
Gmail implementation of the EmailClient interface.

This module provides a Gmail-specific implementation focused on AI assistant needs.
"""

import base64
import email
import email.utils
import os
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from googleapiclient.errors import HttpError

from ..email_api.exceptions import (
    EmailAttachmentError,
    EmailAuthenticationError,
    EmailConnectionError,
    EmailNotFoundError,
    EmailReceiveError,
    EmailSearchError,
)

# Import from the email API package
from ..email_api.interfaces import EmailClient
from ..email_api.models import (
    Attachment,
    AttachmentType,
    Email,
    EmailAddress,
    EmailStats,
)
from .config import GmailConfig


class GmailClient(EmailClient):
    """
    Gmail implementation focused on AI assistant context gathering.

    This client provides read-only access to Gmail for AI analysis,
    hiding the complexity of Gmail API behind simple methods.
    """

    def __init__(self, config: GmailConfig):
        """
        Initialize Gmail client.

        Args:
            config: Gmail configuration with credentials
        """
        self.config = config
        self.service: Optional[Resource] = None
        self._connected = False

    async def __aenter__(self) -> "GmailClient":
        """Async context manager entry with connection setup."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit with cleanup."""
        await self.disconnect()

    async def connect(self) -> None:
        """
        Establish connection to Gmail API.

        Raises:
            EmailConnectionError: If connection fails
            EmailAuthenticationError: If authentication fails
        """
        try:
            # Get credentials
            creds = await self._get_credentials()

            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=creds)

            # Test connection
            await self._test_connection()
            self._connected = True

        except EmailAuthenticationError:
            raise
        except Exception as e:
            raise EmailConnectionError(f"Failed to connect to Gmail: {str(e)}") from e

    async def disconnect(self) -> None:
        """Close connection to Gmail API."""
        self.service = None
        self._connected = False

    async def _get_credentials(self) -> Credentials:
        """Get valid Gmail API credentials."""
        creds = None

        # Load existing credentials
        if os.path.exists(self.config.token_path):
            creds = Credentials.from_authorized_user_file(self.config.token_path, self.config.scopes)  # type: ignore[no-untyped-call]

        # If no valid credentials, run OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())  # type: ignore[no-untyped-call]
                except Exception as e:
                    raise EmailAuthenticationError(f"Failed to refresh credentials: {str(e)}") from e
            else:
                if not os.path.exists(self.config.credentials_path):
                    raise EmailAuthenticationError(f"Credentials file not found: {self.config.credentials_path}")

                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.config.credentials_path, self.config.scopes)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    raise EmailAuthenticationError(f"OAuth flow failed: {str(e)}") from e

            # Save credentials for next run
            with open(self.config.token_path, 'w') as token:
                token.write(creds.to_json())

        return creds  # type: ignore[no-any-return]

    async def _test_connection(self) -> None:
        """Test Gmail API connection."""
        try:
            # Simple API call to test connection
            assert self.service is not None
            self.service.users().getProfile(userId='me').execute()
        except HttpError as e:
            if e.resp.status == 401:
                raise EmailAuthenticationError("Invalid Gmail credentials")
            else:
                raise EmailConnectionError(f"Gmail API error: {e}")
        except Exception as e:
            raise EmailConnectionError(f"Connection test failed: {str(e)}") from e

    async def get_emails(
        self,
        folder: str = "INBOX",
        limit: int = 50,
        include_body: bool = True,
        since_days: Optional[int] = None
    ) -> List[Email]:
        """
        Get emails from Gmail for AI context analysis.

        Args:
            folder: Gmail label (INBOX, SENT, etc.)
            limit: Maximum emails to return
            include_body: Whether to include email content
            since_days: Only get emails from last N days
        """
        if not self._connected:
            raise EmailConnectionError("Not connected to Gmail")

        try:
            assert self.service is not None

            # Build query
            query_parts = [f"in:{folder.lower()}"]

            if since_days:
                date_str = (datetime.now() - timedelta(days=since_days)).strftime('%Y/%m/%d')
                query_parts.append(f"after:{date_str}")

            query = " ".join(query_parts)

            # Get message list
            result = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=limit
            ).execute()

            messages = result.get('messages', [])

            # Get full message details
            emails = []
            for msg in messages:
                try:
                    email_obj = await self._get_message_details(msg['id'], include_body)
                    emails.append(email_obj)
                except Exception as e:
                    # Skip individual message errors but continue processing
                    print(f"Warning: Failed to process message {msg['id']}: {e}")
                    continue

            return emails

        except HttpError as e:
            raise EmailReceiveError(f"Gmail API error: {e}") from e
        except Exception as e:
            raise EmailReceiveError(f"Failed to get emails: {str(e)}") from e

    async def search_emails(self, query: str, limit: int = 10) -> List[Email]:
        """
        Search emails using Gmail's search capabilities.

        Args:
            query: Gmail search query (supports Gmail search syntax)
            limit: Maximum results to return
        """
        if not self._connected:
            raise EmailConnectionError("Not connected to Gmail")

        try:
            assert self.service is not None

            # Gmail search
            result = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=limit
            ).execute()

            messages = result.get('messages', [])

            # Get full message details
            emails = []
            for msg in messages:
                try:
                    email_obj = await self._get_message_details(msg['id'], include_body=True)
                    emails.append(email_obj)
                except Exception as e:
                    print(f"Warning: Failed to process search result {msg['id']}: {e}")
                    continue

            return emails

        except HttpError as e:
            raise EmailSearchError(f"Gmail search error: {e}") from e
        except Exception as e:
            raise EmailSearchError(f"Failed to search emails: {str(e)}") from e

    async def get_email(self, message_id: str) -> Email:
        """
        Get single email by ID with full content.

        Args:
            message_id: Gmail message ID
        """
        if not self._connected:
            raise EmailConnectionError("Not connected to Gmail")

        try:
            return await self._get_message_details(message_id, include_body=True)
        except HttpError as e:
            if e.resp.status == 404:
                raise EmailNotFoundError(f"Email {message_id} not found")
            raise EmailReceiveError(f"Gmail API error: {e}") from e
        except Exception as e:
            raise EmailReceiveError(f"Failed to get email {message_id}: {str(e)}") from e

    async def get_recent_emails(self, days: int = 7) -> List[Email]:
        """Get recent emails for AI context."""
        return await self.get_emails(
            folder="INBOX",
            limit=100,
            include_body=True,
            since_days=days
        )

    async def get_account_info(self) -> EmailStats:
        """Get Gmail account statistics for AI context."""
        if not self._connected:
            raise EmailConnectionError("Not connected to Gmail")

        try:
            assert self.service is not None

            # Get profile info
            profile = self.service.users().getProfile(userId='me').execute()

            # Get label info for folder count
            labels = self.service.users().labels().list(userId='me').execute()

            return EmailStats(
                total_messages=profile.get('messagesTotal', 0),
                unread_messages=profile.get('threadsTotal', 0),  # Approximation
                total_folders=len(labels.get('labels', [])),
                storage_used_mb=0.0,  # Gmail doesn't provide this easily
                last_sync=datetime.now()
            )

        except HttpError as e:
            raise EmailReceiveError(f"Gmail API error: {e}") from e
        except Exception as e:
            raise EmailReceiveError(f"Failed to get account info: {str(e)}") from e

    async def download_attachment(self, message_id: str, attachment_id: str) -> bytes:
        """
        Download attachment content for AI analysis.

        Args:
            message_id: Gmail message ID
            attachment_id: Gmail attachment ID
        """
        if not self._connected:
            raise EmailConnectionError("Not connected to Gmail")

        try:
            assert self.service is not None

            attachment = self.service.users().messages().attachments().get(
                userId='me',
                messageId=message_id,
                id=attachment_id
            ).execute()

            data = attachment['data']
            return base64.urlsafe_b64decode(data)

        except HttpError as e:
            if e.resp.status == 404:
                raise EmailNotFoundError(f"Attachment {attachment_id} not found")
            raise EmailAttachmentError(f"Gmail API error: {e}") from e
        except Exception as e:
            raise EmailAttachmentError(f"Failed to download attachment: {str(e)}") from e

    async def _get_message_details(self, message_id: str, include_body: bool = True) -> Email:
        """Get full message details from Gmail API."""
        assert self.service is not None

        # Get message
        message = self.service.users().messages().get(
            userId='me',
            id=message_id,
            format='full' if include_body else 'metadata'
        ).execute()

        # Parse headers
        headers = {h['name'].lower(): h['value'] for h in message['payload'].get('headers', [])}

        # Extract basic info
        subject = headers.get('subject', '')
        sender = self._parse_email_address(headers.get('from', ''))
        recipients = self._parse_email_addresses(headers.get('to', ''))
        cc_recipients = self._parse_email_addresses(headers.get('cc', ''))
        date_str = headers.get('date', '')

        # Parse date
        date_received = None
        if date_str:
            try:
                date_received = email.utils.parsedate_to_datetime(date_str)
            except (ValueError, TypeError):
                pass

        # Extract body and attachments
        body_text = ""
        body_html = ""
        attachments: List[Attachment] = []

        if include_body:
            body_text, body_html, attachments = self._extract_content(message['payload'])

        return Email(
            message_id=message_id,
            sender=sender,
            recipients=recipients,
            cc_recipients=cc_recipients,
            subject=subject,
            body_text=body_text if body_text else None,
            body_html=body_html if body_html else None,
            attachments=attachments,
            date_received=date_received,
            labels=message.get('labelIds', [])
        )

    def _parse_email_address(self, address_str: str) -> EmailAddress:
        """Parse email address from header string."""
        if not address_str:
            return EmailAddress(address="", name=None)

        # Handle both "Name <email@domain.com>" and "email@domain.com" formats
        match = re.match(r'^(.+?)\s*<(.+)>$', address_str.strip())
        if match:
            name = match.group(1).strip('"')
            address = match.group(2).strip()
        else:
            name = None
            address = address_str.strip()

        return EmailAddress(address=address, name=name)

    def _parse_email_addresses(self, addresses_str: str) -> List[EmailAddress]:
        """Parse multiple email addresses from header string."""
        if not addresses_str:
            return []

        # Split by comma and parse each address
        addresses = []
        for addr in addresses_str.split(','):
            addr = addr.strip()
            if addr:
                addresses.append(self._parse_email_address(addr))

        return addresses

    def _extract_content(self, payload: Dict[str, Any]) -> tuple[str, str, List[Attachment]]:
        """Extract text, HTML content and attachments from message payload."""
        body_text = ""
        body_html = ""
        attachments: List[Attachment] = []

        def extract_parts(part: Dict[str, Any]) -> None:
            nonlocal body_text, body_html, attachments

            mime_type = part.get('mimeType', '')

            # Handle text content
            if mime_type == 'text/plain':
                data = part.get('body', {}).get('data')
                if data:
                    body_text += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

            elif mime_type == 'text/html':
                data = part.get('body', {}).get('data')
                if data:
                    body_html += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

            # Handle attachments
            elif part.get('filename'):
                attachment = Attachment(
                    filename=part['filename'],
                    content_type=mime_type,
                    size_bytes=part.get('body', {}).get('size', 0),
                    attachment_type=self._get_attachment_type(mime_type),
                    content_id=part.get('body', {}).get('attachmentId', '')
                )
                attachments.append(attachment)

            # Recursively process multipart
            if 'parts' in part:
                for subpart in part['parts']:
                    extract_parts(subpart)

        extract_parts(payload)
        return body_text.strip(), body_html.strip(), attachments

    def _get_attachment_type(self, content_type: str) -> AttachmentType:
        """Determine attachment type from content type."""
        if not content_type:
            return AttachmentType.OTHER

        content_type = content_type.lower()

        if content_type.startswith('image/'):
            return AttachmentType.IMAGE
        elif content_type.startswith('text/'):
            return AttachmentType.DOCUMENT  # Fixed: TEXT doesn't exist in AttachmentType
        elif 'pdf' in content_type:
            return AttachmentType.DOCUMENT
        elif any(doc_type in content_type for doc_type in ['word', 'document', 'presentation', 'spreadsheet']):
            return AttachmentType.DOCUMENT
        else:
            return AttachmentType.OTHER
