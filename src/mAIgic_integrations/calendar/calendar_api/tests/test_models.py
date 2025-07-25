"""
Tests for calendar data types and models.

This module contains comprehensive tests for all calendar data structures,
including validation, edge cases, and utility methods.
"""

from datetime import datetime

from ..models import (
    Attendee,
    AttendeeStatus,
    AvailabilityQuery,
    AvailableSlot,
    BatchUpdateResult,
    CalendarDateTime,
    CalendarInfo,
    CalendarSearchQuery,
    CalendarSearchResult,
    ConflictInfo,
    ConflictResolution,
    Event,
    EventChanges,
    EventPriority,
    EventStatus,
    InvitationActionType,
    InvitationResponse,
    NotifyOption,
    PermissionInfo,
    Recurrence,
    RecurrenceScope,
    TimeSlot,
    UpdateResult,
)


class TestCalendarDateTime:
    """Test CalendarDateTime wrapper class."""

    def test_current_time_creation(self):
        """Test creating current time."""
        now = CalendarDateTime.now()
        assert isinstance(now.dt, datetime)

    def test_current_time_with_timezone(self):
        """Test creating current time with timezone parameter."""
        dt_with_tz = CalendarDateTime.now(timezone="America/Los_Angeles")
        assert isinstance(dt_with_tz.dt, datetime)

    def test_from_iso_string(self):
        """Test parsing from ISO string."""
        iso_string = "2024-01-15T14:30:00Z"
        dt = CalendarDateTime.from_iso(iso_string)
        assert dt.dt.year == 2024
        assert dt.dt.month == 1
        assert dt.dt.day == 15
        assert dt.dt.hour == 14
        assert dt.dt.minute == 30

    def test_all_day_creation(self):
        """Test creating all-day date."""
        all_day = CalendarDateTime.all_day(2024, 12, 25)
        assert all_day.dt.day == 25
        assert all_day.dt.month == 12
        assert all_day.dt.year == 2024
        assert all_day.dt.hour == 0
        assert all_day.dt.minute == 0

    def test_timezone_conversion(self):
        """Test timezone conversion."""
        utc_dt = CalendarDateTime.now()
        est_dt = utc_dt.to_timezone("America/New_York")
        assert isinstance(est_dt, CalendarDateTime)
        # Should return a new CalendarDateTime instance
        assert utc_dt is not est_dt

    def test_add_hours(self):
        """Test adding hours to datetime."""
        dt = CalendarDateTime.now()
        future_dt = dt.add_hours(2)

        # Should be 2 hours later
        time_diff = future_dt.dt - dt.dt
        assert time_diff.total_seconds() == 2 * 3600

    def test_iso_export(self):
        """Test exporting as ISO string."""
        dt = CalendarDateTime.from_iso("2024-01-15T14:30:00+00:00")
        iso_str = dt.to_iso()
        assert "2024-01-15" in iso_str
        assert "14:30:00" in iso_str


class TestAttendee:
    """Test Attendee data class."""

    def test_minimal_attendee(self):
        """Test attendee with just email."""
        attendee = Attendee(email="test@example.com")
        assert attendee.email == "test@example.com"
        assert attendee.name is None
        assert attendee.status == AttendeeStatus.NEEDS_ACTION
        assert not attendee.is_organizer
        assert not attendee.is_optional  # Default is required (is_optional=False)
        assert attendee.comment is None

    def test_attendee_with_name(self):
        """Test attendee with name and email."""
        attendee = Attendee(
            email="john@example.com",
            name="John Doe",
            status=AttendeeStatus.ACCEPTED,
            is_organizer=True,
            is_optional=True,
            comment="Looking forward to it!"
        )
        assert attendee.email == "john@example.com"
        assert attendee.name == "John Doe"
        assert attendee.status == AttendeeStatus.ACCEPTED
        assert attendee.is_organizer
        assert attendee.is_optional
        assert attendee.comment == "Looking forward to it!"

    def test_attendee_status_enum(self):
        """Test all attendee status options."""
        statuses = [
            AttendeeStatus.NEEDS_ACTION,
            AttendeeStatus.ACCEPTED,
            AttendeeStatus.DECLINED,
            AttendeeStatus.TENTATIVE
        ]
        for status in statuses:
            attendee = Attendee(email="test@example.com", status=status)
            assert attendee.status == status


class TestTimeSlot:
    """Test TimeSlot data class."""

    def test_basic_time_slot(self):
        """Test basic time slot creation."""
        start = CalendarDateTime.now()
        end = start.add_hours(1)
        slot = TimeSlot(start=start, end=end)

        assert slot.start == start
        assert slot.end == end
        assert slot.duration_minutes == 60

    def test_all_day_slot(self):
        """Test all-day time slot."""
        start = CalendarDateTime.all_day(2024, 1, 15)
        end = CalendarDateTime.all_day(2024, 1, 16)
        slot = TimeSlot(start=start, end=end)

        assert slot.duration_minutes == 24 * 60  # 24 hours in minutes

    def test_slot_overlap_detection(self):
        """Test overlap detection between time slots."""
        # Create base slot: 2:00-3:00 PM
        base_start = CalendarDateTime.from_iso("2024-01-15T14:00:00Z")
        base_end = CalendarDateTime.from_iso("2024-01-15T15:00:00Z")
        base_slot = TimeSlot(start=base_start, end=base_end)

        # Overlapping slot: 2:30-3:30 PM
        overlap_start = CalendarDateTime.from_iso("2024-01-15T14:30:00Z")
        overlap_end = CalendarDateTime.from_iso("2024-01-15T15:30:00Z")
        overlap_slot = TimeSlot(start=overlap_start, end=overlap_end)

        # Non-overlapping slot: 4:00-5:00 PM
        no_overlap_start = CalendarDateTime.from_iso("2024-01-15T16:00:00Z")
        no_overlap_end = CalendarDateTime.from_iso("2024-01-15T17:00:00Z")
        no_overlap_slot = TimeSlot(start=no_overlap_start, end=no_overlap_end)

        assert base_slot.overlaps_with(overlap_slot)
        assert overlap_slot.overlaps_with(base_slot)
        assert not base_slot.overlaps_with(no_overlap_slot)

    def test_slot_containment(self):
        """Test datetime containment within time slots."""
        # Outer slot: 2:00-4:00 PM
        outer_start = CalendarDateTime.from_iso("2024-01-15T14:00:00Z")
        outer_end = CalendarDateTime.from_iso("2024-01-15T16:00:00Z")
        outer_slot = TimeSlot(start=outer_start, end=outer_end)

        # Test datetime inside the slot
        inside_dt = CalendarDateTime.from_iso("2024-01-15T15:00:00Z")
        assert outer_slot.contains(inside_dt)

        # Test datetime outside the slot
        outside_dt = CalendarDateTime.from_iso("2024-01-15T17:00:00Z")
        assert not outer_slot.contains(outside_dt)


class TestRecurrence:
    """Test Recurrence pattern class."""

    def test_daily_recurrence(self):
        """Test daily recurrence pattern."""
        recurrence = Recurrence(
            frequency="daily",
            interval=1,
            count=10
        )
        assert recurrence.frequency == "daily"
        assert recurrence.interval == 1
        assert recurrence.count == 10
        assert len(recurrence.days_of_week) == 0

    def test_weekly_recurrence(self):
        """Test weekly recurrence pattern."""
        recurrence = Recurrence(
            frequency="weekly",
            interval=2,
            days_of_week=[0, 2, 4],  # Monday, Wednesday, Friday
            until=CalendarDateTime.from_iso("2024-12-31T23:59:59Z")
        )
        assert recurrence.frequency == "weekly"
        assert recurrence.interval == 2
        assert recurrence.days_of_week == [0, 2, 4]
        assert recurrence.until is not None

    def test_monthly_recurrence(self):
        """Test monthly recurrence pattern."""
        recurrence = Recurrence(
            frequency="monthly",
            day_of_month=15,
            count=12
        )
        assert recurrence.frequency == "monthly"
        assert recurrence.day_of_month == 15
        assert recurrence.count == 12

    def test_complex_recurrence_with_rrule(self):
        """Test complex recurrence with raw RRULE."""
        rrule = "FREQ=WEEKLY;BYDAY=MO,WE,FR;INTERVAL=2;COUNT=20"
        recurrence = Recurrence(
            frequency="weekly",
            rrule=rrule
        )
        assert recurrence.rrule == rrule


class TestEvent:
    """Test Event data class."""

    def test_minimal_event(self):
        """Test event with minimal required fields."""
        start_time = CalendarDateTime.now()
        end_time = start_time.add_hours(1)
        time_slot = TimeSlot(start=start_time, end=end_time)

        event = Event(
            event_id="event-123",
            title="Test Event",
            time_slot=time_slot
        )
        assert event.event_id == "event-123"
        assert event.title == "Test Event"
        assert event.time_slot == time_slot
        assert event.description == ""
        assert event.location == ""
        assert event.status == EventStatus.CONFIRMED
        assert event.priority == EventPriority.NORMAL
        assert len(event.attendees) == 0
        assert event.calendar_id == "primary"

    def test_auto_generate_event_id(self):
        """Test automatic event ID generation."""
        start_time = CalendarDateTime.now()
        end_time = start_time.add_hours(1)
        time_slot = TimeSlot(start=start_time, end=end_time)

        event = Event(
            event_id="",
            title="Test Event",
            time_slot=time_slot
        )
        assert event.event_id != ""
        assert len(event.event_id) > 0

    def test_comprehensive_event(self):
        """Test event with all fields populated."""
        start_time = CalendarDateTime.now()
        end_time = start_time.add_hours(2)
        time_slot = TimeSlot(start=start_time, end=end_time)

        organizer = Attendee(
            email="organizer@example.com",
            name="Event Organizer",
            is_organizer=True,
            status=AttendeeStatus.ACCEPTED
        )

        attendees = [
            Attendee(email="attendee1@example.com", name="Attendee One"),
            Attendee(email="attendee2@example.com", name="Attendee Two", status=AttendeeStatus.ACCEPTED)
        ]

        recurrence = Recurrence(frequency="weekly", interval=1, count=5)

        event = Event(
            event_id="comprehensive-event",
            title="Team Meeting",
            time_slot=time_slot,
            organizer=organizer,
            attendees=attendees,
            description="Weekly team sync meeting",
            location="Conference Room A",
            status=EventStatus.CONFIRMED,
            priority=EventPriority.HIGH,
            recurrence=recurrence,
            calendar_id="cal-123"
        )

        assert event.event_id == "comprehensive-event"
        assert event.calendar_id == "cal-123"
        assert event.title == "Team Meeting"
        assert event.description == "Weekly team sync meeting"
        assert event.location == "Conference Room A"
        assert event.time_slot == time_slot
        assert event.organizer == organizer
        assert len(event.attendees) == 2
        assert event.attendees[0].email == "attendee1@example.com"
        assert event.status == EventStatus.CONFIRMED
        assert event.priority == EventPriority.HIGH
        assert event.recurrence == recurrence
        assert event.is_recurring
        assert event.duration_minutes == 120

    def test_event_properties(self):
        """Test event computed properties."""
        # Create a basic time slot for events
        start_time = CalendarDateTime.now()
        end_time = start_time.add_hours(1)
        time_slot = TimeSlot(start=start_time, end=end_time)

        # Test recurring event
        recurrence = Recurrence(frequency="daily", count=5)
        recurring_event = Event(
            event_id="recurring-123",
            title="Daily Meeting",
            time_slot=time_slot,
            recurrence=recurrence
        )
        assert recurring_event.is_recurring

        # Test non-recurring event
        non_recurring_event = Event(
            event_id="single-123",
            title="Single Meeting",
            time_slot=time_slot
        )
        assert not non_recurring_event.is_recurring

        # Test all-day event (24 hours starting at midnight)
        all_day_start = CalendarDateTime.all_day(2024, 1, 15)
        all_day_end = CalendarDateTime.all_day(2024, 1, 16)
        all_day_slot = TimeSlot(start=all_day_start, end=all_day_end)
        all_day_event = Event(
            event_id="all-day-123",
            title="All Day Event",
            time_slot=all_day_slot
        )
        assert all_day_event.is_all_day
        assert all_day_event.duration_minutes == 1440  # 24 hours


class TestEventChanges:
    """Test EventChanges data class."""

    def test_empty_changes(self):
        """Test empty event changes."""
        changes = EventChanges()
        assert changes.title is None
        assert changes.description is None
        assert changes.location is None
        assert changes.time_slot is None
        assert changes.attendees is None
        assert changes.status is None
        assert changes.priority is None
        assert changes.recurrence is None

    def test_partial_changes(self):
        """Test partial event changes."""
        changes = EventChanges(
            title="Updated Meeting",
            priority=EventPriority.HIGH
        )
        assert changes.title == "Updated Meeting"
        assert changes.priority == EventPriority.HIGH
        assert changes.description is None


class TestUpdateResult:
    """Test UpdateResult data class."""

    def test_successful_update(self):
        """Test successful update result."""
        start_time = CalendarDateTime.now()
        end_time = start_time.add_hours(1)
        time_slot = TimeSlot(start=start_time, end=end_time)
        updated_event = Event(
            event_id="updated-123",
            title="Updated Event",
            time_slot=time_slot
        )
        result = UpdateResult(
            success=True,
            updated_event=updated_event
        )
        assert result.success
        assert result.updated_event == updated_event
        assert len(result.conflicts) == 0
        assert len(result.affected_attendees) == 0
        assert result.permissions is None
        assert result.error_message is None

    def test_failed_update(self):
        """Test failed update result."""
        result = UpdateResult(
            success=False,
            error_message="Permission denied"
        )
        assert not result.success
        assert result.updated_event is None
        assert result.error_message == "Permission denied"

    def test_update_with_conflicts(self):
        """Test update result with scheduling conflicts."""
        conflict_info = ConflictInfo(
            conflict_type="time_conflict",
            description="Overlaps with existing meeting",
            conflicting_event_id="conflict-123",
            severity="high",
            suggestion="Move to 3:00 PM"
        )

        result = UpdateResult(
            success=False,
            conflicts=[conflict_info]
        )
        assert not result.success
        assert len(result.conflicts) == 1
        assert result.conflicts[0].conflict_type == "time_conflict"
        assert result.conflicts[0].conflicting_event_id == "conflict-123"


class TestBatchUpdateResult:
    """Test BatchUpdateResult data class."""

    def test_batch_result_properties(self):
        """Test batch result computed properties."""
        successful_result = UpdateResult(success=True)
        failed_results = [("event-1", "Permission denied"), ("event-2", "Not found")]

        batch_result = BatchUpdateResult(
            successful_updates=[successful_result],
            failed_updates=failed_results
        )

        assert batch_result.total_successful == 1
        assert batch_result.total_failed == 2
        assert batch_result.total_processed == 3

    def test_empty_batch_result(self):
        """Test empty batch result."""
        batch_result = BatchUpdateResult(
            successful_updates=[],
            failed_updates=[]
        )
        assert batch_result.total_successful == 0
        assert batch_result.total_failed == 0
        assert batch_result.total_processed == 0


class TestAvailabilityQuery:
    """Test AvailabilityQuery data class."""

    def test_basic_availability_query(self):
        """Test basic availability query."""
        time_range = TimeSlot(
            start=CalendarDateTime.now(),
            end=CalendarDateTime.now().add_hours(8)
        )
        query = AvailabilityQuery(
            time_range=time_range,
            duration_minutes=60
        )
        assert query.time_range == time_range
        assert query.duration_minutes == 60
        assert len(query.attendees) == 0
        assert query.buffer_minutes == 0
        assert query.working_hours_only
        assert query.exclude_weekends

    def test_comprehensive_availability_query(self):
        """Test availability query with all options."""
        time_range = TimeSlot(
            start=CalendarDateTime.now(),
            end=CalendarDateTime.now().add_hours(8)
        )
        attendees = ["alice@example.com", "bob@example.com"]
        preferred_times = [TimeSlot(
            start=CalendarDateTime.now().add_hours(2),
            end=CalendarDateTime.now().add_hours(3)
        )]

        query = AvailabilityQuery(
            time_range=time_range,
            duration_minutes=90,
            attendees=attendees,
            buffer_minutes=15,
            working_hours_only=False,
            exclude_weekends=False,
            preferred_times=preferred_times
        )

        assert query.time_range == time_range
        assert query.duration_minutes == 90
        assert query.attendees == attendees
        assert query.buffer_minutes == 15
        assert not query.working_hours_only
        assert not query.exclude_weekends
        assert query.preferred_times == preferred_times


class TestAvailableSlot:
    """Test AvailableSlot data class."""

    def test_available_slot(self):
        """Test available slot creation."""
        time_slot = TimeSlot(
            start=CalendarDateTime.now(),
            end=CalendarDateTime.now().add_hours(1)
        )
        slot = AvailableSlot(
            time_slot=time_slot,
            confidence=0.85,
            attendee_conflicts=["charlie@example.com"]
        )
        assert slot.time_slot == time_slot
        assert slot.confidence == 0.85
        assert slot.attendee_conflicts == ["charlie@example.com"]


class TestInvitationResponse:
    """Test InvitationResponse data class."""

    def test_simple_response(self):
        """Test simple invitation response."""
        response = InvitationResponse(status=AttendeeStatus.ACCEPTED)
        assert response.status == AttendeeStatus.ACCEPTED
        assert response.comment is None

    def test_response_with_comment(self):
        """Test invitation response with comment."""
        response = InvitationResponse(
            status=AttendeeStatus.DECLINED,
            comment="Sorry, I have a conflict"
        )
        assert response.status == AttendeeStatus.DECLINED
        assert response.comment == "Sorry, I have a conflict"


class TestPermissionInfo:
    """Test PermissionInfo data class."""

    def test_default_permissions(self):
        """Test default permission settings."""
        permissions = PermissionInfo()
        assert permissions.can_read
        assert not permissions.can_edit
        assert not permissions.can_delete
        assert not permissions.can_invite_others
        assert not permissions.can_modify_attendees
        assert permissions.can_see_attendees
        assert not permissions.is_organizer
        assert permissions.role == "reader"
        assert permissions.reason is None

    def test_full_permissions(self):
        """Test full permission settings."""
        permissions = PermissionInfo(
            can_read=True,
            can_edit=True,
            can_delete=True,
            can_invite_others=True,
            can_modify_attendees=True,
            can_see_attendees=True,
            is_organizer=True,
            role="owner",
            reason="Event organizer"
        )
        assert permissions.can_read
        assert permissions.can_edit
        assert permissions.can_delete
        assert permissions.can_invite_others
        assert permissions.can_modify_attendees
        assert permissions.can_see_attendees
        assert permissions.is_organizer
        assert permissions.role == "owner"
        assert permissions.reason == "Event organizer"


class TestCalendarInfo:
    """Test CalendarInfo data class."""

    def test_basic_calendar_info(self):
        """Test basic calendar information."""
        cal_info = CalendarInfo(
            calendar_id="cal-123",
            name="Work Calendar"
        )
        assert cal_info.calendar_id == "cal-123"
        assert cal_info.name == "Work Calendar"
        assert cal_info.description == ""
        assert not cal_info.is_primary
        assert cal_info.permissions is None
        assert cal_info.timezone == "UTC"
        assert cal_info.color is None
        assert cal_info.provider_type == "unknown"

    def test_comprehensive_calendar_info(self):
        """Test comprehensive calendar information."""
        permissions = PermissionInfo(
            can_read=True,
            can_edit=True,
            can_delete=True,
            role="owner"
        )
        cal_info = CalendarInfo(
            calendar_id="primary",
            name="Personal Calendar",
            description="My main personal calendar",
            timezone="America/New_York",
            is_primary=True,
            permissions=permissions,
            color="#FF5722",
            provider_type="google"
        )
        assert cal_info.calendar_id == "primary"
        assert cal_info.name == "Personal Calendar"
        assert cal_info.description == "My main personal calendar"
        assert cal_info.is_primary
        assert cal_info.permissions == permissions
        assert cal_info.timezone == "America/New_York"
        assert cal_info.color == "#FF5722"
        assert cal_info.provider_type == "google"


class TestCalendarSearchQuery:
    """Test CalendarSearchQuery data class."""

    def test_text_search_query(self):
        """Test text-based search query."""
        query = CalendarSearchQuery(query="team meeting")
        assert query.query == "team meeting"
        assert query.time_range is None
        assert query.attendee_email is None
        assert query.organizer_email is None
        assert len(query.calendar_ids) == 0
        assert query.event_status is None
        assert not query.include_declined
        assert query.max_results == 100

    def test_comprehensive_search_query(self):
        """Test comprehensive search query."""
        time_range = TimeSlot(
            start=CalendarDateTime.now(),
            end=CalendarDateTime.now().add_hours(24)
        )

        query = CalendarSearchQuery(
            query="project review",
            time_range=time_range,
            attendee_email="alice@example.com",
            organizer_email="bob@example.com",
            calendar_ids=["cal-1", "cal-2"],
            event_status=EventStatus.CONFIRMED,
            include_declined=True,
            max_results=25
        )
        assert query.query == "project review"
        assert query.time_range == time_range
        assert query.attendee_email == "alice@example.com"
        assert query.organizer_email == "bob@example.com"
        assert query.calendar_ids == ["cal-1", "cal-2"]
        assert query.event_status == EventStatus.CONFIRMED
        assert query.include_declined
        assert query.max_results == 25


class TestCalendarSearchResult:
    """Test CalendarSearchResult data class."""

    def test_search_result(self):
        """Test search result creation."""
        start_time = CalendarDateTime.now()
        end_time = start_time.add_hours(1)
        time_slot = TimeSlot(start=start_time, end=end_time)

        events = [
            Event(event_id="event-1", title="Meeting 1", time_slot=time_slot),
            Event(event_id="event-2", title="Meeting 2", time_slot=time_slot)
        ]

        result = CalendarSearchResult(
            events=events,
            total_count=25,
            has_more=True,
            next_page_token="page-token-123"
        )
        assert len(result.events) == 2
        assert result.total_count == 25
        assert result.has_more
        assert result.next_page_token == "page-token-123"

    def test_search_result_no_more(self):
        """Test search result with no more results."""
        result = CalendarSearchResult(
            events=[],
            total_count=0,
            has_more=False
        )
        assert len(result.events) == 0
        assert result.total_count == 0
        assert not result.has_more
        assert result.next_page_token is None


class TestEnums:
    """Test all calendar enums."""

    def test_event_status_enum(self):
        """Test EventStatus enum values."""
        assert EventStatus.CONFIRMED.value == "confirmed"
        assert EventStatus.TENTATIVE.value == "tentative"
        assert EventStatus.CANCELLED.value == "cancelled"

    def test_attendee_status_enum(self):
        """Test AttendeeStatus enum values."""
        assert AttendeeStatus.NEEDS_ACTION.value == "needsAction"
        assert AttendeeStatus.DECLINED.value == "declined"
        assert AttendeeStatus.TENTATIVE.value == "tentative"
        assert AttendeeStatus.ACCEPTED.value == "accepted"

    def test_event_priority_enum(self):
        """Test EventPriority enum values."""
        assert EventPriority.LOW.value == "low"
        assert EventPriority.NORMAL.value == "normal"
        assert EventPriority.HIGH.value == "high"

    def test_recurrence_scope_enum(self):
        """Test RecurrenceScope enum values."""
        assert RecurrenceScope.THIS_INSTANCE.value == "this"
        assert RecurrenceScope.THIS_AND_FOLLOWING.value == "following"
        assert RecurrenceScope.ALL_INSTANCES.value == "all"

    def test_notify_option_enum(self):
        """Test NotifyOption enum values."""
        assert NotifyOption.NONE.value == "none"
        assert NotifyOption.DEFAULT.value == "default"
        assert NotifyOption.ALL.value == "all"

    def test_conflict_resolution_enum(self):
        """Test ConflictResolution enum values."""
        assert ConflictResolution.FAIL.value == "fail"
        assert ConflictResolution.WARN.value == "warn"
        assert ConflictResolution.FORCE.value == "force"

    def test_invitation_action_type_enum(self):
        """Test InvitationActionType enum values."""
        assert InvitationActionType.SEND.value == "send"
        assert InvitationActionType.RESPOND.value == "respond"
        assert InvitationActionType.PROPOSE_TIME.value == "propose"
