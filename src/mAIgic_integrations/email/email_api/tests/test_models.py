"""
Tests for email data types and structures.
"""

from datetime import datetime

from ..models import (
    Attachment,
    AttachmentType,
    Email,
    EmailAddress,
    EmailFolder,
    EmailPriority,
    EmailSearchQuery,
    EmailSearchResult,
    EmailStats,
    EmailStatus,
    EmailThread,
)


class TestEmailAddress:
    """Test EmailAddress data class."""

    def test_address_only(self):
        """Test email address without display name."""
        addr = EmailAddress("test@example.com")
        assert addr.address == "test@example.com"
        assert addr.name is None
        assert str(addr) == "test@example.com"

    def test_address_with_name(self):
        """Test email address with display name."""
        addr = EmailAddress("test@example.com", "Test User")
        assert addr.address == "test@example.com"
        assert addr.name == "Test User"
        assert str(addr) == "Test User <test@example.com>"


class TestAttachment:
    """Test Attachment data class."""

    def test_basic_attachment(self):
        """Test basic attachment creation."""
        att = Attachment(
            filename="test.pdf",
            content_type="application/pdf",
            size_bytes=1024,
            attachment_type=AttachmentType.DOCUMENT
        )
        assert att.filename == "test.pdf"
        assert att.content_type == "application/pdf"
        assert att.size_bytes == 1024
        assert att.attachment_type == AttachmentType.DOCUMENT

    def test_auto_detect_image_type(self):
        """Test auto-detection of image attachment type."""
        att = Attachment(
            filename="image.jpg",
            content_type="image/jpeg",
            size_bytes=2048,
            attachment_type=AttachmentType.OTHER  # Will be auto-detected
        )
        assert att.attachment_type == AttachmentType.IMAGE

    def test_auto_detect_audio_type(self):
        """Test auto-detection of audio attachment type."""
        att = Attachment(
            filename="audio.mp3",
            content_type="audio/mpeg",
            size_bytes=4096,
            attachment_type=AttachmentType.OTHER
        )
        assert att.attachment_type == AttachmentType.AUDIO

    def test_auto_detect_video_type(self):
        """Test auto-detection of video attachment type."""
        att = Attachment(
            filename="video.mp4",
            content_type="video/mp4",
            size_bytes=8192,
            attachment_type=AttachmentType.OTHER
        )
        assert att.attachment_type == AttachmentType.VIDEO

    def test_auto_detect_archive_type(self):
        """Test auto-detection of archive attachment type."""
        att = Attachment(
            filename="archive.zip",
            content_type="application/zip",
            size_bytes=1536,
            attachment_type=AttachmentType.OTHER
        )
        assert att.attachment_type == AttachmentType.ARCHIVE

    def test_auto_detect_document_type(self):
        """Test auto-detection of document attachment type."""
        att = Attachment(
            filename="doc.pdf",
            content_type="application/pdf",
            size_bytes=3072,
            attachment_type=AttachmentType.OTHER
        )
        assert att.attachment_type == AttachmentType.DOCUMENT

    def test_unknown_type_remains_other(self):
        """Test that unknown content types remain as OTHER."""
        att = Attachment(
            filename="unknown.xyz",
            content_type="application/x-unknown",
            size_bytes=512,
            attachment_type=AttachmentType.OTHER
        )
        assert att.attachment_type == AttachmentType.OTHER


class TestEmailThread:
    """Test EmailThread data class."""

    def test_basic_thread(self):
        """Test basic email thread creation."""
        participants = [
            EmailAddress("user1@example.com", "User One"),
            EmailAddress("user2@example.com", "User Two")
        ]
        thread = EmailThread(
            thread_id="thread-123",
            subject="Test Subject",
            participants=participants,
            message_count=3,
            last_message_date=datetime.now()
        )
        assert thread.thread_id == "thread-123"
        assert thread.subject == "Test Subject"
        assert len(thread.participants) == 2
        assert thread.message_count == 3
        assert len(thread.labels) == 0  # Default empty list


class TestEmail:
    """Test Email data class."""

    def test_minimal_email(self):
        """Test email with minimal required fields."""
        email = Email(message_id="msg-123")
        assert email.message_id == "msg-123"
        assert email.subject == ""
        assert len(email.recipients) == 0
        assert email.priority == EmailPriority.NORMAL
        assert email.status == EmailStatus.UNREAD

    def test_auto_generate_message_id(self):
        """Test automatic message ID generation."""
        email = Email(message_id="")
        assert email.message_id != ""
        assert len(email.message_id) > 0

        # Test with no message_id provided (should be generated in __post_init__)
        email2 = Email(message_id="")
        email2.__post_init__()
        assert email2.message_id != ""

    def test_complete_email(self):
        """Test email with all fields populated."""
        sender = EmailAddress("sender@example.com", "Sender Name")
        recipients = [EmailAddress("recipient@example.com", "Recipient Name")]
        cc_recipients = [EmailAddress("cc@example.com", "CC Name")]
        attachments = [
            Attachment("file.pdf", "application/pdf", 1024, AttachmentType.DOCUMENT)
        ]

        email = Email(
            message_id="msg-456",
            sender=sender,
            recipients=recipients,
            cc_recipients=cc_recipients,
            subject="Test Subject",
            body_text="Test body",
            body_html="<p>Test body</p>",
            attachments=attachments,
            priority=EmailPriority.HIGH,
            status=EmailStatus.READ
        )

        assert email.message_id == "msg-456"
        assert email.sender.address == "sender@example.com"
        assert len(email.recipients) == 1
        assert len(email.cc_recipients) == 1
        assert email.subject == "Test Subject"
        assert email.body_text == "Test body"
        assert email.body_html == "<p>Test body</p>"
        assert len(email.attachments) == 1
        assert email.priority == EmailPriority.HIGH
        assert email.status == EmailStatus.READ

    def test_has_attachments_property(self):
        """Test has_attachments property."""
        email = Email(message_id="msg-789")
        assert not email.has_attachments

        email.attachments.append(
            Attachment("file.txt", "text/plain", 100, AttachmentType.DOCUMENT)
        )
        assert email.has_attachments

    def test_total_attachment_size_property(self):
        """Test total_attachment_size property."""
        email = Email(message_id="msg-101")
        assert email.total_attachment_size == 0

        email.attachments.extend([
            Attachment("file1.txt", "text/plain", 100, AttachmentType.DOCUMENT),
            Attachment("file2.txt", "text/plain", 200, AttachmentType.DOCUMENT)
        ])
        assert email.total_attachment_size == 300

    def test_all_recipients_property(self):
        """Test all_recipients property."""
        email = Email(
            message_id="msg-102",
            recipients=[EmailAddress("to@example.com")],
            cc_recipients=[EmailAddress("cc@example.com")],
            bcc_recipients=[EmailAddress("bcc@example.com")]
        )
        all_recipients = email.all_recipients
        assert len(all_recipients) == 3
        assert any(addr.address == "to@example.com" for addr in all_recipients)
        assert any(addr.address == "cc@example.com" for addr in all_recipients)
        assert any(addr.address == "bcc@example.com" for addr in all_recipients)


class TestEmailSearchQuery:
    """Test EmailSearchQuery data class."""

    def test_default_search_query(self):
        """Test default search query values."""
        query = EmailSearchQuery()
        assert query.query is None
        assert query.sender is None
        assert query.limit == 50
        assert query.offset == 0
        assert len(query.labels) == 0

    def test_custom_search_query(self):
        """Test custom search query."""
        query = EmailSearchQuery(
            query="test search",
            sender="sender@example.com",
            has_attachment=True,
            limit=25,
            offset=10,
            labels=["important", "work"]
        )
        assert query.query == "test search"
        assert query.sender == "sender@example.com"
        assert query.has_attachment is True
        assert query.limit == 25
        assert query.offset == 10
        assert query.labels == ["important", "work"]


class TestEmailSearchResult:
    """Test EmailSearchResult data class."""

    def test_search_result(self):
        """Test email search result."""
        emails = [
            Email(message_id="msg-1"),
            Email(message_id="msg-2")
        ]
        result = EmailSearchResult(
            emails=emails,
            total_count=100,
            has_more=True,
            next_offset=50
        )
        assert len(result.emails) == 2
        assert result.total_count == 100
        assert result.has_more is True
        assert result.next_offset == 50


class TestEmailFolder:
    """Test EmailFolder data class."""

    def test_basic_folder(self):
        """Test basic email folder."""
        folder = EmailFolder(
            name="INBOX",
            display_name="Inbox",
            message_count=100,
            unread_count=5
        )
        assert folder.name == "INBOX"
        assert folder.display_name == "Inbox"
        assert folder.message_count == 100
        assert folder.unread_count == 5
        assert folder.folder_type == "custom"  # Default value
        assert len(folder.subfolders) == 0

    def test_folder_with_hierarchy(self):
        """Test folder with parent and subfolders."""
        folder = EmailFolder(
            name="Work/Projects",
            display_name="Projects",
            message_count=25,
            unread_count=2,
            folder_type="custom",
            parent_folder="Work",
            subfolders=["Work/Projects/Alpha", "Work/Projects/Beta"]
        )
        assert folder.parent_folder == "Work"
        assert len(folder.subfolders) == 2


class TestEmailStats:
    """Test EmailStats data class."""

    def test_basic_stats(self):
        """Test basic email statistics."""
        stats = EmailStats(
            total_messages=1000,
            unread_messages=50,
            total_folders=10,
            storage_used_mb=250.5
        )
        assert stats.total_messages == 1000
        assert stats.unread_messages == 50
        assert stats.total_folders == 10
        assert stats.storage_used_mb == 250.5
        assert stats.storage_quota_mb is None
        assert stats.last_sync is None

    def test_stats_with_quota(self):
        """Test statistics with quota information."""
        last_sync = datetime.now()
        stats = EmailStats(
            total_messages=500,
            unread_messages=25,
            total_folders=5,
            storage_used_mb=125.0,
            storage_quota_mb=1000.0,
            last_sync=last_sync
        )
        assert stats.storage_quota_mb == 1000.0
        assert stats.last_sync == last_sync


class TestEnums:
    """Test email enumeration types."""

    def test_email_priority_values(self):
        """Test EmailPriority enum values."""
        assert EmailPriority.LOW.value == "low"
        assert EmailPriority.NORMAL.value == "normal"
        assert EmailPriority.HIGH.value == "high"
        assert EmailPriority.URGENT.value == "urgent"

    def test_email_status_values(self):
        """Test EmailStatus enum values."""
        assert EmailStatus.UNREAD.value == "unread"
        assert EmailStatus.READ.value == "read"
        assert EmailStatus.REPLIED.value == "replied"
        assert EmailStatus.FORWARDED.value == "forwarded"
        assert EmailStatus.DELETED.value == "deleted"
        assert EmailStatus.DRAFT.value == "draft"
        assert EmailStatus.SENT.value == "sent"

    def test_attachment_type_values(self):
        """Test AttachmentType enum values."""
        assert AttachmentType.DOCUMENT.value == "document"
        assert AttachmentType.IMAGE.value == "image"
        assert AttachmentType.AUDIO.value == "audio"
        assert AttachmentType.VIDEO.value == "video"
        assert AttachmentType.ARCHIVE.value == "archive"
        assert AttachmentType.OTHER.value == "other"
