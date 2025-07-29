"""Time helper functions for mAIgic_core.

This module provides utility functions for time parsing, formatting,
and time slot manipulation.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from ..llm.llm_api.types import TimeSlot


def time_slot_from_string(time_str: str, duration_hours: float = 1.0) -> TimeSlot:
    """Create TimeSlot from string representation.
    
    Args:
        time_str: ISO format datetime string
        duration_hours: Duration in hours
        
    Returns:
        TimeSlot object
        
    Raises:
        ValueError: If time_str cannot be parsed
    """
    try:
        start = datetime.fromisoformat(time_str)
        end = start + timedelta(hours=duration_hours)
        return TimeSlot(start=start, end=end)
    except ValueError as e:
        raise ValueError(f"Invalid time string '{time_str}': {e}")


def time_slot_to_string(time_slot: TimeSlot, include_timezone: bool = True) -> str:
    """Convert TimeSlot to string representation.
    
    Args:
        time_slot: TimeSlot to convert
        include_timezone: Whether to include timezone info
        
    Returns:
        String representation of the time slot
    """
    start_str = time_slot.start.isoformat()
    end_str = time_slot.end.isoformat()
    
    if include_timezone and time_slot.timezone != "UTC":
        return f"{start_str} to {end_str} ({time_slot.timezone})"
    else:
        return f"{start_str} to {end_str}"


def parse_natural_time(time_description: str, reference_time: Optional[datetime] = None) -> Optional[TimeSlot]:
    """Parse natural language time descriptions into TimeSlot.
    
    Args:
        time_description: Natural language description (e.g., "tomorrow at 2pm", "next Monday")
        reference_time: Reference time for relative parsing (defaults to now)
        
    Returns:
        TimeSlot if parsing successful, None otherwise
        
    Note:
        This is a simplified implementation. In production, you'd want
        to use a more sophisticated NLP library like dateutil or spacy.
    """
    if reference_time is None:
        reference_time = datetime.now()
    
    time_description = time_description.lower().strip()
    
    # Simple patterns - extend this for production use
    patterns = {
        "tomorrow": timedelta(days=1),
        "today": timedelta(days=0),
        "next week": timedelta(weeks=1),
        "next monday": _days_until_weekday(reference_time, 0),  # Monday = 0
        "next tuesday": _days_until_weekday(reference_time, 1),
        "next wednesday": _days_until_weekday(reference_time, 2),
        "next thursday": _days_until_weekday(reference_time, 3),
        "next friday": _days_until_weekday(reference_time, 4),
    }
    
    for pattern, delta in patterns.items():
        if pattern in time_description:
            target_date = reference_time + delta
            
            # Extract time if mentioned
            if "at" in time_description:
                time_part = time_description.split("at")[-1].strip()
                parsed_time = _parse_time_of_day(time_part)
                if parsed_time:
                    hour, minute = parsed_time
                    target_date = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            else:
                # Default to 9 AM if no time specified
                target_date = target_date.replace(hour=9, minute=0, second=0, microsecond=0)
            
            # Default 1-hour duration
            return TimeSlot(
                start=target_date,
                end=target_date + timedelta(hours=1)
            )
    
    return None


def format_duration(duration: timedelta) -> str:
    """Format duration in human-readable format.
    
    Args:
        duration: Duration to format
        
    Returns:
        Human-readable duration string
    """
    total_seconds = int(duration.total_seconds())
    
    if total_seconds < 60:
        return f"{total_seconds} seconds"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        return f"{minutes} minutes"
    elif total_seconds < 86400:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        if minutes > 0:
            return f"{hours} hours {minutes} minutes"
        else:
            return f"{hours} hours"
    else:
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        if hours > 0:
            return f"{days} days {hours} hours"
        else:
            return f"{days} days"


def is_time_slot_available(
    target_slot: TimeSlot,
    existing_slots: List[TimeSlot],
    buffer_minutes: int = 15
) -> bool:
    """Check if a time slot is available (doesn't conflict with existing slots).
    
    Args:
        target_slot: Time slot to check
        existing_slots: List of existing time slots
        buffer_minutes: Buffer time between slots in minutes
        
    Returns:
        True if the slot is available (no conflicts)
    """
    buffer = timedelta(minutes=buffer_minutes)
    
    # Expand target slot with buffer
    buffered_start = target_slot.start - buffer
    buffered_end = target_slot.end + buffer
    buffered_target = TimeSlot(start=buffered_start, end=buffered_end)
    
    for existing_slot in existing_slots:
        if buffered_target.overlaps_with(existing_slot):
            return False
    
    return True


def find_available_slots(
    duration: timedelta,
    start_time: datetime,
    end_time: datetime,
    existing_slots: List[TimeSlot],
    min_slot_duration: timedelta = timedelta(hours=1),
    buffer_minutes: int = 15
) -> List[TimeSlot]:
    """Find available time slots within a given time range.
    
    Args:
        duration: Required duration for the slot
        start_time: Start of search range
        end_time: End of search range
        existing_slots: List of existing time slots to avoid
        min_slot_duration: Minimum duration for a valid slot
        buffer_minutes: Buffer time between slots
        
    Returns:
        List of available time slots
    """
    available_slots = []
    buffer = timedelta(minutes=buffer_minutes)
    
    # Sort existing slots by start time
    sorted_slots = sorted(existing_slots, key=lambda x: x.start)
    
    current_time = start_time
    
    for slot in sorted_slots:
        # Check if there's a gap before this slot
        gap_end = slot.start - buffer
        if gap_end > current_time:
            gap_duration = gap_end - current_time
            if gap_duration >= duration and gap_duration >= min_slot_duration:
                available_slots.append(TimeSlot(start=current_time, end=gap_end))
        
        # Move current time to after this slot
        current_time = max(current_time, slot.end + buffer)
    
    # Check if there's a gap after the last slot
    if current_time < end_time:
        gap_duration = end_time - current_time
        if gap_duration >= duration and gap_duration >= min_slot_duration:
            available_slots.append(TimeSlot(start=current_time, end=end_time))
    
    return available_slots


# Helper functions
def _days_until_weekday(reference_time: datetime, target_weekday: int) -> timedelta:
    """Calculate days until target weekday.
    
    Args:
        reference_time: Reference datetime
        target_weekday: Target weekday (0=Monday, 6=Sunday)
        
    Returns:
        Timedelta to reach the target weekday
    """
    current_weekday = reference_time.weekday()
    days_ahead = target_weekday - current_weekday
    
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    
    return timedelta(days=days_ahead)


def _parse_time_of_day(time_str: str) -> Optional[tuple[int, int]]:
    """Parse time of day from string.
    
    Args:
        time_str: Time string (e.g., "2pm", "14:30", "9:00")
        
    Returns:
        Tuple of (hour, minute) if successful, None otherwise
    """
    time_str = time_str.strip().lower()
    
    # Handle AM/PM format
    if "pm" in time_str:
        time_str = time_str.replace("pm", "").strip()
        try:
            if ":" in time_str:
                hour, minute = map(int, time_str.split(":"))
            else:
                hour, minute = int(time_str), 0
            
            if hour != 12:
                hour += 12
            return (hour, minute)
        except ValueError:
            return None
    
    elif "am" in time_str:
        time_str = time_str.replace("am", "").strip()
        try:
            if ":" in time_str:
                hour, minute = map(int, time_str.split(":"))
            else:
                hour, minute = int(time_str), 0
            
            if hour == 12:
                hour = 0
            return (hour, minute)
        except ValueError:
            return None
    
    # Handle 24-hour format
    elif ":" in time_str:
        try:
            hour, minute = map(int, time_str.split(":"))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return (hour, minute)
        except ValueError:
            return None
    
    return None 