"""
Email data types and enums.

This module defines the core data structures used throughout the email API.
All email implementations should use these types for consistency.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class EmailPriority(Enum):
    """Email priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class EmailStatus(Enum):
    """Email status indicators."""
    UNREAD = "unread"
    READ = "read"
    REPLIED = "replied"
    FORWARDED = "forwarded"
    DELETED = "deleted"
    DRAFT = "draft"
    SENT = "sent"


class AttachmentType(Enum):
    """Supported attachment types."""
    DOCUMENT = "document"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    ARCHIVE = "archive"
    OTHER = "other"


@dataclass
class EmailAddress:
    """Email address with optional display name."""
    address: str
    name: Optional[str] = None

    def __str__(self) -> str:
        if self.name:
            return f"{self.name} <{self.address}>"
        return self.address


@dataclass
class Attachment:
    """Email attachment representation."""
    filename: str
    content_type: str
    size_bytes: int
    attachment_type: AttachmentType
    content_id: Optional[str] = None  # For inline attachments
    data: Optional[bytes] = None  # Actual content (loaded on demand)

    def __post_init__(self) -> None:
        """Auto-detect attachment type from content type."""
        if self.attachment_type == AttachmentType.OTHER:
            self.attachment_type = self._detect_type_from_content_type()

    def _detect_type_from_content_type(self) -> AttachmentType:
        """Detect attachment type from MIME content type."""
        if self.content_type.startswith("image/"):
            return AttachmentType.IMAGE
        elif self.content_type.startswith("audio/"):
            return AttachmentType.AUDIO
        elif self.content_type.startswith("video/"):
            return AttachmentType.VIDEO
        elif self.content_type in ["application/zip", "application/rar", "application/tar"]:
            return AttachmentType.ARCHIVE
        elif self.content_type in ["application/pdf", "application/msword", "text/plain"]:
            return AttachmentType.DOCUMENT
        return AttachmentType.OTHER


@dataclass
class EmailThread:
    """Email conversation thread."""
    thread_id: str
    subject: str
    participants: List[EmailAddress]
    message_count: int
    last_message_date: datetime
    labels: List[str] = field(default_factory=list)


@dataclass
class Email:
    """Complete email message representation."""
    # Core identifiers
    message_id: str
    thread_id: Optional[str] = None

    # Addressing
    sender: EmailAddress = field(default_factory=lambda: EmailAddress(""))
    recipients: List[EmailAddress] = field(default_factory=list)
    cc_recipients: List[EmailAddress] = field(default_factory=list)
    bcc_recipients: List[EmailAddress] = field(default_factory=list)
    reply_to: Optional[EmailAddress] = None

    # Content
    subject: str = ""
    body_text: Optional[str] = None  # Plain text version
    body_html: Optional[str] = None  # HTML version
    attachments: List[Attachment] = field(default_factory=list)

    # Metadata
    date_sent: Optional[datetime] = None
    date_received: Optional[datetime] = None
    priority: EmailPriority = EmailPriority.NORMAL
    status: EmailStatus = EmailStatus.UNREAD
    labels: List[str] = field(default_factory=list)
    folder: Optional[str] = None

    # Provider-specific data
    provider_data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Generate message ID if not provided."""
        if not self.message_id:
            self.message_id = str(uuid.uuid4())

    @property
    def has_attachments(self) -> bool:
        """Check if email has attachments."""
        return len(self.attachments) > 0

    @property
    def total_attachment_size(self) -> int:
        """Get total size of all attachments in bytes."""
        return sum(att.size_bytes for att in self.attachments)

    @property
    def all_recipients(self) -> List[EmailAddress]:
        """Get all recipients (to, cc, bcc combined)."""
        return self.recipients + self.cc_recipients + self.bcc_recipients


@dataclass
class EmailSearchQuery:
    """Email search parameters."""
    query: Optional[str] = None  # Full-text search
    sender: Optional[str] = None
    recipient: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    has_attachment: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    labels: List[str] = field(default_factory=list)
    folder: Optional[str] = None
    status: Optional[EmailStatus] = None
    limit: int = 50
    offset: int = 0


@dataclass
class EmailSearchResult:
    """Email search results."""
    emails: List[Email]
    total_count: int
    has_more: bool
    next_offset: Optional[int] = None


@dataclass
class EmailFolder:
    """Email folder/mailbox representation."""
    name: str
    display_name: str
    message_count: int
    unread_count: int
    folder_type: str = "custom"  # inbox, sent, drafts, trash, spam, custom
    parent_folder: Optional[str] = None
    subfolders: List[str] = field(default_factory=list)


@dataclass
class EmailStats:
    """Email account statistics."""
    total_messages: int
    unread_messages: int
    total_folders: int
    storage_used_mb: float
    storage_quota_mb: Optional[float] = None
    last_sync: Optional[datetime] = None


@dataclass
class EmailUpdateRequest:
    """Request for updating email properties."""
    message_ids: List[str]
    status: Optional[EmailStatus] = None
    labels: Optional[List[str]] = None
    folder: Optional[str] = None
    mark_important: Optional[bool] = None


# Type aliases for common use cases
EmailList = List[Email]
RecipientList = List[EmailAddress]
AttachmentList = List[Attachment]
