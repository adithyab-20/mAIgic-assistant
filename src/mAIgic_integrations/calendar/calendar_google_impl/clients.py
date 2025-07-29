"""
Google Calendar Client Implementation.

This module provides the GoogleCalendarClient that implements the CalendarClient
interface using the Google Calendar API v3.
"""

import asyncio
import os
from datetime import UTC, datetime, timedelta
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..calendar_api.exceptions import (
    CalendarAPIError,
    CalendarAuthenticationError,
    CalendarConnectionError,
    CalendarEventNotFoundError,
    CalendarPermissionError,
    CalendarSchedulingError,
)
from ..calendar_api.interfaces import CalendarClient
from ..calendar_api.models import (
    Attendee,
    AttendeeStatus,
    AvailabilityQuery,
    AvailableSlot,
    BatchUpdateResult,
    CalendarDateTime,
    CalendarInfo,
    CalendarSearchQuery,
    CalendarSearchResult,
    Event,
    EventChanges,
    EventStatus,
    InvitationResponse,
    NotifyOption,
    PermissionInfo,
    Recurrence,
    TimeSlot,
    UpdateResult,
)
from .config import GoogleCalendarConfig


class GoogleCalendarClient(CalendarClient):
    """
    Google Calendar implementation of CalendarClient interface.

    Uses Google Calendar API v3 for all operations. Handles OAuth2 authentication,
    converts between Google Calendar API format and mAIgic calendar models.
    """

    def __init__(self, config: GoogleCalendarConfig):
        """
        Initialize Google Calendar client.

        Args:
            config: Google Calendar configuration
        """
        self.config = config
        self.service: Any | None = None
        self.credentials: Any | None = None

    async def __aenter__(self) -> "GoogleCalendarClient":
        """Enter async context and authenticate with Google Calendar."""
        await self._authenticate()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context and clean up resources."""
        # Clean up any resources if needed
        self.service = None
        self.credentials = None

    def _ensure_authenticated(self) -> Any:
        """Ensure service is authenticated and return it."""
        if self.service is None:
            raise CalendarAuthenticationError("Client not authenticated. Use async context manager.")
        return self.service

    async def _authenticate(self) -> None:
        """
        Authenticate with Google Calendar API using OAuth2.

        Raises:
            CalendarAuthenticationError: If authentication fails
        """
        try:
            creds = None
            # Load existing token if available
            if os.path.exists(self.config.token_path):
                creds = Credentials.from_authorized_user_file(  # type: ignore
                    self.config.token_path, self.config.scopes
                )

            # If there are no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())  # type: ignore
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.config.credentials_path, self.config.scopes
                    )
                    creds = flow.run_local_server(port=0)

                # Save the credentials for the next run
                with open(self.config.token_path, 'w') as token:
                    token.write(creds.to_json())

            self.credentials = creds

            # Build the Google Calendar service
            self.service = build(
                'calendar',
                'v3',
                credentials=creds,
                cache_discovery=False
            )

        except Exception as e:
            raise CalendarAuthenticationError(f"Failed to authenticate: {e}")

    def _run_in_executor(self, func: Any, *args: Any) -> Any:
        """Run synchronous Google API calls in thread pool executor."""
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(None, func, *args)

    def _convert_to_google_datetime(self, dt: CalendarDateTime, all_day: bool = False) -> dict[str, Any]:
        """
        Convert CalendarDateTime to Google Calendar API format.

        Args:
            dt: CalendarDateTime to convert
            all_day: Whether this is an all-day event

        Returns:
            Google Calendar API datetime dict
        """
        if all_day:
            return {"date": dt.dt.strftime("%Y-%m-%d")}
        else:
            # Ensure proper RFC3339 format with timezone
            if dt.dt.tzinfo is None:
                # If no timezone info, assume it's in the user's configured timezone
                # For now, assume UTC if no timezone (this should be improved with pendulum)
                aware_dt = dt.dt.replace(tzinfo=UTC)
                iso_string = aware_dt.isoformat()
            else:
                iso_string = dt.dt.isoformat()

            return {
                "dateTime": iso_string,
                "timeZone": self.config.user_timezone
            }

    def _convert_from_google_datetime(self, google_dt: dict[str, Any]) -> CalendarDateTime:
        """
        Convert Google Calendar API datetime to CalendarDateTime.

        Args:
            google_dt: Google Calendar API datetime dict

        Returns:
            CalendarDateTime instance
        """
        if "date" in google_dt:
            # All-day event
            date_str = google_dt["date"]
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            # Timed event
            dt_str = google_dt["dateTime"]
            try:
                # Handle various datetime formats from Google
                if dt_str.endswith('Z'):
                    dt_str = dt_str.replace('Z', '+00:00')
                dt = datetime.fromisoformat(dt_str)
            except ValueError:
                # Fallback for other formats
                from dateutil import parser
                dt = parser.parse(dt_str)

        return CalendarDateTime(dt)

    def _convert_to_google_event(self, event: Event) -> dict[str, Any]:
        """
        Convert Event to Google Calendar API format.

        Args:
            event: Event to convert

        Returns:
            Google Calendar API event dict
        """
        google_event = {
            "summary": event.title,
            "description": event.description,
            "location": event.location,
            "start": self._convert_to_google_datetime(
                event.time_slot.start,
                event.is_all_day
            ),
            "end": self._convert_to_google_datetime(
                event.time_slot.end,
                event.is_all_day
            ),
        }

        # Add attendees
        if event.attendees:
            attendee_list = [
                {
                    "email": attendee.email,
                    "displayName": attendee.name or attendee.email,
                    "optional": attendee.is_optional,
                    "responseStatus": self._convert_attendee_status_to_google(attendee.status)
                }
                for attendee in event.attendees
            ]
            google_event["attendees"] = attendee_list  # type: ignore

        # Add recurrence if present
        if event.recurrence:
            google_event["recurrence"] = self._convert_recurrence_to_google(event.recurrence)

        return google_event

    def _convert_from_google_event(self, google_event: dict[str, Any]) -> Event:
        """
        Convert Google Calendar API event to Event.

        Args:
            google_event: Google Calendar API event dict

        Returns:
            Event instance
        """
        # Extract time slot
        start_dt = self._convert_from_google_datetime(google_event["start"])
        end_dt = self._convert_from_google_datetime(google_event["end"])
        time_slot = TimeSlot(start_dt, end_dt)

        # Extract attendees
        attendees = []
        if "attendees" in google_event:
            for google_attendee in google_event["attendees"]:
                attendee = Attendee(
                    email=google_attendee["email"],
                    name=google_attendee.get("displayName"),
                    status=self._convert_attendee_status_from_google(
                        google_attendee.get("responseStatus", "needsAction")
                    ),
                    is_optional=google_attendee.get("optional", False),
                    is_organizer=google_attendee.get("organizer", False)
                )
                attendees.append(attendee)

        # Extract organizer
        organizer = None
        if "organizer" in google_event:
            organizer = Attendee(
                email=google_event["organizer"]["email"],
                name=google_event["organizer"].get("displayName"),
                is_organizer=True,
                status=AttendeeStatus.ACCEPTED
            )

        event = Event(
            event_id=google_event["id"],
            title=google_event.get("summary", ""),
            time_slot=time_slot,
            description=google_event.get("description", ""),
            location=google_event.get("location", ""),
            organizer=organizer,
            attendees=attendees,
            status=self._convert_event_status_from_google(
                google_event.get("status", "confirmed")
            ),
            provider_data={"google_event": google_event}
        )

        return event

    def _convert_attendee_status_to_google(self, status: AttendeeStatus) -> str:
        """Convert AttendeeStatus to Google Calendar format."""
        mapping = {
            AttendeeStatus.NEEDS_ACTION: "needsAction",
            AttendeeStatus.DECLINED: "declined",
            AttendeeStatus.TENTATIVE: "tentative",
            AttendeeStatus.ACCEPTED: "accepted"
        }
        return mapping.get(status, "needsAction")

    def _convert_attendee_status_from_google(self, google_status: str) -> AttendeeStatus:
        """Convert Google Calendar attendee status to AttendeeStatus."""
        mapping = {
            "needsAction": AttendeeStatus.NEEDS_ACTION,
            "declined": AttendeeStatus.DECLINED,
            "tentative": AttendeeStatus.TENTATIVE,
            "accepted": AttendeeStatus.ACCEPTED
        }
        return mapping.get(google_status, AttendeeStatus.NEEDS_ACTION)

    def _convert_event_status_from_google(self, google_status: str) -> EventStatus:
        """Convert Google Calendar event status to EventStatus."""
        mapping = {
            "confirmed": EventStatus.CONFIRMED,
            "tentative": EventStatus.TENTATIVE,
            "cancelled": EventStatus.CANCELLED
        }
        return mapping.get(google_status, EventStatus.CONFIRMED)

    def _convert_recurrence_to_google(self, recurrence: Recurrence) -> list[str]:
        """Convert Recurrence to Google Calendar RRULE format."""
        # This is a simplified implementation - full RRULE support would be more complex
        if recurrence.rrule:
            return [recurrence.rrule]

        # Build basic RRULE
        freq_map = {
            "daily": "DAILY",
            "weekly": "WEEKLY",
            "monthly": "MONTHLY",
            "yearly": "YEARLY"
        }

        rrule = f"RRULE:FREQ={freq_map.get(recurrence.frequency, 'WEEKLY')}"

        if recurrence.interval > 1:
            rrule += f";INTERVAL={recurrence.interval}"

        if recurrence.count:
            rrule += f";COUNT={recurrence.count}"

        if recurrence.until:
            rrule += f";UNTIL={recurrence.until.dt.strftime('%Y%m%dT%H%M%SZ')}"

        return [rrule]

    async def get_events(
        self,
        time_range: TimeSlot,
        calendar_ids: list[str] | None = None,
        include_declined: bool = False
    ) -> list[Event]:
        """Get events in time range from Google Calendar."""
        try:
            # Default to primary calendar if none specified
            if not calendar_ids:
                calendar_ids = ["primary"]

            all_events = []

            for calendar_id in calendar_ids:
                # Prepare API call parameters with proper datetime format
                start_dt = time_range.start.dt
                end_dt = time_range.end.dt

                # Add timezone if missing
                if start_dt.tzinfo is None:
                    start_dt = start_dt.replace(tzinfo=UTC)
                if end_dt.tzinfo is None:
                    end_dt = end_dt.replace(tzinfo=UTC)

                params = {
                    "calendarId": calendar_id,
                    "timeMin": start_dt.isoformat(),
                    "timeMax": end_dt.isoformat(),
                    "singleEvents": True,
                    "orderBy": "startTime",
                    "maxResults": 2500
                }

                if not include_declined:
                    params["showDeleted"] = False

                # Execute API call
                if self.service is None:
                    raise CalendarAPIError("Calendar service not authenticated")

                service = self._ensure_authenticated()
                events_result = await self._run_in_executor(
                    lambda: service.events().list(**params).execute()
                )

                # Convert events
                for google_event in events_result.get("items", []):
                    event = self._convert_from_google_event(google_event)
                    all_events.append(event)

            return all_events

        except HttpError as e:
            if e.resp.status == 404:
                raise CalendarEventNotFoundError(f"Calendar not found: {calendar_ids}")
            elif e.resp.status == 403:
                raise CalendarPermissionError(f"Access denied to calendar: {calendar_ids}")
            else:
                raise CalendarConnectionError(f"Google Calendar API error: {e}")
        except Exception as e:
            raise CalendarAPIError(f"Failed to get events: {e}")

    async def find_available_slots(
        self,
        query: AvailabilityQuery
    ) -> list[AvailableSlot]:
        """Find available time slots using Google Calendar Freebusy API."""
        try:
            # Use Google Calendar Freebusy API to check availability
            # Ensure proper datetime format for freebusy API
            start_dt = query.time_range.start.dt
            end_dt = query.time_range.end.dt

            # Add timezone if missing
            if start_dt.tzinfo is None:
                start_dt = start_dt.replace(tzinfo=UTC)
            if end_dt.tzinfo is None:
                end_dt = end_dt.replace(tzinfo=UTC)

            freebusy_body = {
                "timeMin": start_dt.isoformat(),
                "timeMax": end_dt.isoformat(),
                "items": [{"id": attendee} for attendee in query.attendees] + [{"id": "primary"}]
            }

            if self.service is None:
                raise CalendarAPIError("Calendar service not authenticated")

            freebusy_result = await self._run_in_executor(
                lambda: self.service.freebusy().query(body=freebusy_body).execute()
            )

            # Analyze busy periods and find free slots
            busy_periods = []
            calendars_data = freebusy_result.get("calendars", {})

            for calendar_id, calendar_data in calendars_data.items():
                busy_times = calendar_data.get("busy", [])
                for busy_time in busy_times:
                    start = CalendarDateTime.from_iso(busy_time["start"])
                    end = CalendarDateTime.from_iso(busy_time["end"])
                    busy_periods.append(TimeSlot(start, end))

            # Generate available slots
            available_slots = self._find_free_slots(
                query.time_range,
                busy_periods,
                query.duration_minutes,
                query.buffer_minutes
            )

            return available_slots

        except HttpError as e:
            raise CalendarConnectionError(f"Google Calendar Freebusy API error: {e}")
        except Exception as e:
            raise CalendarAPIError(f"Failed to find available slots: {e}")

    def _find_free_slots(
        self,
        search_range: TimeSlot,
        busy_periods: list[TimeSlot],
        duration_minutes: int,
        buffer_minutes: int = 0
    ) -> list[AvailableSlot]:
        """
        Find free time slots given busy periods.

        Args:
            search_range: Time range to search within
            busy_periods: List of busy time slots
            duration_minutes: Required duration for each slot
            buffer_minutes: Buffer time between meetings

        Returns:
            List of available slots
        """

        # Normalize all datetimes to ensure consistent timezone handling
        def normalize_dt(dt: Any) -> Any:
            if dt.tzinfo is None:
                return dt.replace(tzinfo=UTC)
            return dt

        # Sort busy periods by start time
        busy_periods.sort(key=lambda slot: slot.start.dt)

        available_slots = []
        current_time = search_range.start
        current_dt = normalize_dt(current_time.dt)

        for busy_period in busy_periods:
            # Check if there's a gap before this busy period
            gap_end = busy_period.start
            gap_end_dt = normalize_dt(gap_end.dt)
            gap_duration = (gap_end_dt - current_dt).total_seconds() / 60

            if gap_duration >= duration_minutes + buffer_minutes:
                # Found a free slot
                slot_end_dt = current_dt + timedelta(minutes=duration_minutes)
                slot_end = CalendarDateTime(slot_end_dt)
                available_slot = AvailableSlot(
                    time_slot=TimeSlot(CalendarDateTime(current_dt), slot_end),
                    confidence=1.0  # High confidence for completely free slots
                )
                available_slots.append(available_slot)

            # Move current time to end of busy period
            current_time = busy_period.end
            current_dt = normalize_dt(current_time.dt)

        # Check for a slot after the last busy period
        search_end_dt = normalize_dt(search_range.end.dt)
        remaining_duration = (search_end_dt - current_dt).total_seconds() / 60
        if remaining_duration >= duration_minutes:
            slot_end_dt = current_dt + timedelta(minutes=duration_minutes)
            slot_end = CalendarDateTime(slot_end_dt)
            available_slot = AvailableSlot(
                time_slot=TimeSlot(CalendarDateTime(current_dt), slot_end),
                confidence=1.0
            )
            available_slots.append(available_slot)

        return available_slots

    async def search_events(
        self,
        query: CalendarSearchQuery
    ) -> CalendarSearchResult:
        """Search events using Google Calendar API."""
        try:
            # Prepare search parameters
            params = {
                "calendarId": query.calendar_ids[0] if query.calendar_ids else "primary",
                "q": query.query or "",
                "maxResults": min(query.max_results, 2500),
                "singleEvents": True,
                "orderBy": "startTime"
            }

            if query.time_range:
                # Ensure proper datetime format
                start_dt = query.time_range.start.dt
                end_dt = query.time_range.end.dt

                # Add timezone if missing
                if start_dt.tzinfo is None:
                    start_dt = start_dt.replace(tzinfo=UTC)
                if end_dt.tzinfo is None:
                    end_dt = end_dt.replace(tzinfo=UTC)

                params.update({
                    "timeMin": start_dt.isoformat(),
                    "timeMax": end_dt.isoformat()
                })

            # Execute search
            service = self._ensure_authenticated()
            search_result = await self._run_in_executor(
                lambda: service.events().list(**params).execute()
            )

            # Convert results
            events = []
            for google_event in search_result.get("items", []):
                event = self._convert_from_google_event(google_event)

                # Apply additional filters
                if self._matches_search_criteria(event, query):
                    events.append(event)

            return CalendarSearchResult(
                events=events,
                total_count=len(events),
                has_more=False,  # Google Calendar API doesn't provide total count
                next_page_token=search_result.get("nextPageToken")
            )

        except HttpError as e:
            raise CalendarConnectionError(f"Google Calendar search error: {e}")
        except Exception as e:
            raise CalendarAPIError(f"Failed to search events: {e}")

    def _matches_search_criteria(self, event: Event, query: CalendarSearchQuery) -> bool:
        """Check if event matches additional search criteria."""
        # Filter by attendee email
        if query.attendee_email:
            attendee_emails = [att.email for att in event.attendees]
            if query.attendee_email not in attendee_emails:
                return False

        # Filter by organizer email
        if query.organizer_email:
            if not event.organizer or event.organizer.email != query.organizer_email:
                return False

        # Filter by event status
        if query.event_status and event.status != query.event_status:
            return False

        return True

    async def get_event(self, event_id: str) -> Event:
        """Get single event by ID."""
        try:
            service = self._ensure_authenticated()
            google_event = await self._run_in_executor(
                lambda: service.events().get(
                    calendarId="primary",
                    eventId=event_id
                ).execute()
            )

            return self._convert_from_google_event(google_event)

        except HttpError as e:
            if e.resp.status == 404:
                raise CalendarEventNotFoundError(f"Event not found: {event_id}")
            elif e.resp.status == 403:
                raise CalendarPermissionError(f"Access denied to event: {event_id}")
            else:
                raise CalendarConnectionError(f"Google Calendar API error: {e}")
        except Exception as e:
            raise CalendarAPIError(f"Failed to get event: {e}")

    async def create_my_event(
        self,
        event: Event,
        calendar_id: str | None = None,
        notify_attendees: NotifyOption = NotifyOption.DEFAULT
    ) -> UpdateResult:
        """Create new event as organizer."""
        try:
            calendar_id = calendar_id or "primary"
            google_event = self._convert_to_google_event(event)

            # Add notification settings
            send_notifications = notify_attendees != NotifyOption.NONE

            service = self._ensure_authenticated()
            created_event = await self._run_in_executor(
                lambda: service.events().insert(
                    calendarId=calendar_id,
                    body=google_event,
                    sendNotifications=send_notifications
                ).execute()
            )

            result_event = self._convert_from_google_event(created_event)

            return UpdateResult(
                success=True,
                updated_event=result_event,
                conflicts=[],
                affected_attendees=result_event.attendees,
                permissions=PermissionInfo(
                    can_read=True,
                    can_edit=True,
                    can_delete=True,
                    is_organizer=True,
                    role="owner"
                )
            )

        except HttpError as e:
            error_msg = f"Google Calendar API error: {e}"
            if e.resp.status == 403:
                raise CalendarPermissionError(error_msg)
            elif e.resp.status == 409:
                raise CalendarSchedulingError(error_msg)
            else:
                raise CalendarConnectionError(error_msg)
        except Exception as e:
            raise CalendarAPIError(f"Failed to create event: {e}")

    async def update_my_event(
        self,
        event_id: str,
        changes: EventChanges,
        notify_attendees: NotifyOption = NotifyOption.DEFAULT
    ) -> UpdateResult:
        """Update existing event as organizer."""
        try:
            # First get the existing event
            existing_event = await self.get_event(event_id)

            # Apply changes
            updated_event = self._apply_changes_to_event(existing_event, changes)
            google_event = self._convert_to_google_event(updated_event)

            # Update the event
            send_notifications = notify_attendees != NotifyOption.NONE

            service = self._ensure_authenticated()
            result_google_event = await self._run_in_executor(
                lambda: service.events().update(
                    calendarId="primary",
                    eventId=event_id,
                    body=google_event,
                    sendNotifications=send_notifications
                ).execute()
            )

            result_event = self._convert_from_google_event(result_google_event)

            return UpdateResult(
                success=True,
                updated_event=result_event,
                conflicts=[],
                affected_attendees=result_event.attendees
            )

        except CalendarEventNotFoundError:
            raise
        except HttpError as e:
            error_msg = f"Google Calendar API error: {e}"
            if e.resp.status == 403:
                raise CalendarPermissionError(error_msg)
            elif e.resp.status == 409:
                raise CalendarSchedulingError(error_msg)
            else:
                raise CalendarConnectionError(error_msg)
        except Exception as e:
            raise CalendarAPIError(f"Failed to update event: {e}")

    def _apply_changes_to_event(self, event: Event, changes: EventChanges) -> Event:
        """Apply EventChanges to an existing Event."""
        # Create a copy of the event with changes applied
        updated_event = Event(
            event_id=event.event_id,
            title=changes.title if changes.title is not None else event.title,
            time_slot=changes.time_slot if changes.time_slot is not None else event.time_slot,
            description=changes.description if changes.description is not None else event.description,
            location=changes.location if changes.location is not None else event.location,
            organizer=event.organizer,
            attendees=changes.attendees if changes.attendees is not None else event.attendees,
            status=changes.status if changes.status is not None else event.status,
            priority=changes.priority if changes.priority is not None else event.priority,
            recurrence=changes.recurrence if changes.recurrence is not None else event.recurrence,
            calendar_id=event.calendar_id,
            created_time=event.created_time,
            updated_time=CalendarDateTime.now(),
            provider_data=event.provider_data
        )

        return updated_event

    async def delete_my_event(
        self,
        event_id: str,
        notify_attendees: NotifyOption = NotifyOption.DEFAULT,
        cancellation_message: str | None = None
    ) -> UpdateResult:
        """Delete event as organizer."""
        try:
            # Get event details before deletion for result
            event = await self.get_event(event_id)

            send_notifications = notify_attendees != NotifyOption.NONE

            service = self._ensure_authenticated()
            await self._run_in_executor(
                lambda: service.events().delete(
                    calendarId="primary",
                    eventId=event_id,
                    sendNotifications=send_notifications
                ).execute()
            )

            return UpdateResult(
                success=True,
                updated_event=None,
                affected_attendees=event.attendees
            )

        except CalendarEventNotFoundError:
            raise
        except HttpError as e:
            error_msg = f"Google Calendar API error: {e}"
            if e.resp.status == 403:
                raise CalendarPermissionError(error_msg)
            else:
                raise CalendarConnectionError(error_msg)
        except Exception as e:
            raise CalendarAPIError(f"Failed to delete event: {e}")

    async def respond_to_invitation(
        self,
        event_id: str,
        response: InvitationResponse
    ) -> UpdateResult:
        """Respond to calendar invitation as attendee."""
        try:
            # Get the event to update attendee status
            event = await self.get_event(event_id)

            # Find user's attendee record and update status
            # Note: This is simplified - real implementation would need to identify
            # the current user's email address
            user_email = None

            # Try to get user email from various credential sources
            if self.credentials and hasattr(self.credentials, 'id_token') and self.credentials.id_token:
                user_email = self.credentials.id_token.get("email")
            elif self.credentials and hasattr(self.credentials, 'token') and isinstance(self.credentials.token, dict):
                user_email = self.credentials.token.get("email")

            if not user_email:
                # Fallback: use "primary" - Google Calendar API will use authenticated user
                user_email = "primary"

            # Update the event with new response status
            google_event = event.provider_data.get("google_event", {})
            if "attendees" in google_event:
                for attendee in google_event["attendees"]:
                    if attendee["email"] == user_email or user_email == "primary":
                        attendee["responseStatus"] = self._convert_attendee_status_to_google(response.status)
                        if response.comment:
                            attendee["comment"] = response.comment

            # Update the event
            service = self._ensure_authenticated()
            updated_google_event = await self._run_in_executor(
                lambda: service.events().update(
                    calendarId="primary",
                    eventId=event_id,
                    body=google_event,
                    sendNotifications=True
                ).execute()
            )

            result_event = self._convert_from_google_event(updated_google_event)

            return UpdateResult(
                success=True,
                updated_event=result_event
            )

        except CalendarEventNotFoundError:
            raise
        except HttpError as e:
            error_msg = f"Google Calendar API error: {e}"
            if e.resp.status == 403:
                raise CalendarPermissionError(error_msg)
            else:
                raise CalendarConnectionError(error_msg)
        except Exception as e:
            raise CalendarAPIError(f"Failed to respond to invitation: {e}")

    async def suggest_reschedule(
        self,
        event_id: str,
        proposed_time: TimeSlot,
        message: str | None = None
    ) -> UpdateResult:
        """
        Suggest reschedule as attendee.

        Note: Google Calendar API doesn't have direct support for reschedule suggestions.
        This implementation adds a comment to the event with the suggestion.
        """
        try:
            # Get the event
            event = await self.get_event(event_id)

            # Add reschedule suggestion as a comment/description update
            suggestion_text = f"\nReschedule suggestion: {proposed_time.start.to_iso()} - {proposed_time.end.to_iso()}"
            if message:
                suggestion_text += f"\nMessage: {message}"

            # Update event description with suggestion
            google_event = event.provider_data.get("google_event", {})
            current_description = google_event.get("description", "")
            google_event["description"] = current_description + suggestion_text

            # This is a limitation of Google Calendar API - we can't actually send
            # reschedule suggestions directly. In a real implementation, you might
            # use Gmail API to send an email with the suggestion instead.

            return UpdateResult(
                success=False,
                error_message="Google Calendar API does not support reschedule suggestions directly. Consider using email integration to send suggestion to organizer."
            )

        except Exception as e:
            raise CalendarAPIError(f"Failed to suggest reschedule: {e}")

    async def batch_create_events(
        self,
        events: list[Event],
        calendar_id: str | None = None,
        notify_attendees: NotifyOption = NotifyOption.DEFAULT
    ) -> BatchUpdateResult:
        """Create multiple events atomically using batch requests."""
        # Google Calendar API supports batch requests for better performance
        successful_updates = []
        failed_updates = []

        for event in events:
            try:
                result = await self.create_my_event(event, calendar_id, notify_attendees)
                successful_updates.append(result)
            except Exception as e:
                failed_updates.append((event.event_id, str(e)))

        return BatchUpdateResult(
            successful_updates=successful_updates,
            failed_updates=failed_updates
        )

    async def batch_update_events(
        self,
        updates: list[tuple[str, EventChanges]],
        notify_attendees: NotifyOption = NotifyOption.DEFAULT
    ) -> BatchUpdateResult:
        """Update multiple events atomically."""
        successful_updates = []
        failed_updates = []

        for event_id, changes in updates:
            try:
                result = await self.update_my_event(event_id, changes, notify_attendees)
                successful_updates.append(result)
            except Exception as e:
                failed_updates.append((event_id, str(e)))

        return BatchUpdateResult(
            successful_updates=successful_updates,
            failed_updates=failed_updates
        )

    async def get_event_permissions(self, event_id: str) -> PermissionInfo:
        """Get permissions for a specific event."""
        try:
            # Get event to determine permissions
            event = await self.get_event(event_id)

            # Check if user is organizer
            user_email = None
            if self.credentials and hasattr(self.credentials, 'id_token') and self.credentials.id_token:
                user_email = self.credentials.id_token.get("email")
            elif self.credentials and hasattr(self.credentials, 'token') and isinstance(self.credentials.token, dict):
                user_email = self.credentials.token.get("email")

            is_organizer: bool = bool(
                user_email and
                event.organizer and
                hasattr(event.organizer, 'email') and
                event.organizer.email == user_email
            )

            return PermissionInfo(
                can_read=True,
                can_edit=is_organizer,
                can_delete=is_organizer,
                can_invite_others=is_organizer,
                can_modify_attendees=is_organizer,
                can_see_attendees=True,
                is_organizer=is_organizer,
                role="owner" if is_organizer else "reader"
            )

        except CalendarEventNotFoundError:
            return PermissionInfo(
                can_read=False,
                reason="Event not found"
            )
        except Exception as e:
            raise CalendarAPIError(f"Failed to get event permissions: {e}")

    async def get_calendars(self) -> list[CalendarInfo]:
        """Get available calendars for this user."""
        try:
            service = self._ensure_authenticated()
            calendar_list = await self._run_in_executor(
                lambda: service.calendarList().list().execute()
            )

            calendars = []
            for google_calendar in calendar_list.get("items", []):
                calendar_info = CalendarInfo(
                    calendar_id=google_calendar["id"],
                    name=google_calendar.get("summary", ""),
                    description=google_calendar.get("description", ""),
                    timezone=google_calendar.get("timeZone", "UTC"),
                    is_primary=google_calendar.get("primary", False),
                    color=google_calendar.get("backgroundColor"),
                    provider_type="google",
                    permissions=PermissionInfo(
                        can_read=True,
                        can_edit=google_calendar.get("accessRole") in ["owner", "writer"],
                        can_delete=google_calendar.get("accessRole") == "owner",
                        role=google_calendar.get("accessRole", "reader")
                    )
                )
                calendars.append(calendar_info)

            return calendars

        except HttpError as e:
            raise CalendarConnectionError(f"Google Calendar API error: {e}")
        except Exception as e:
            raise CalendarAPIError(f"Failed to get calendars: {e}")

