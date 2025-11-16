"""
AI-powered calendar parsing service (NO keyword matching)
"""
from typing import List, Tuple
from datetime import datetime, timedelta
from icalendar import Calendar
from dateutil import tz

from app.models import BusyBlock
from app.clients.ai_client import get_ai_client


def parse_ics_calendar(ics_content: str, user_id: str, days_ahead: int = 30) -> Tuple[List[BusyBlock], List[str]]:
    """
    Parse .ics calendar file and extract busy blocks using AI categorization

    Args:
        ics_content: Raw .ics file content
        user_id: User ID to associate blocks with
        days_ahead: How many days ahead to extract events

    Returns:
        Tuple of (list of BusyBlock objects, list of warnings)
    """
    warnings = []
    busy_blocks = []

    try:
        cal = Calendar.from_ical(ics_content)
    except Exception as e:
        raise ValueError(f"Invalid .ics file format: {str(e)}")

    # Calculate cutoff date
    now = datetime.now(tz=tz.UTC)
    cutoff = now + timedelta(days=days_ahead)

    ai_client = get_ai_client()

    for component in cal.walk():
        if component.name == "VEVENT":
            try:
                # Extract event details
                summary = str(component.get('summary', 'Untitled Event'))
                description = str(component.get('description', ''))
                dtstart = component.get('dtstart')
                dtend = component.get('dtend')

                if not dtstart or not dtend:
                    warnings.append(f"Event '{summary}' missing start/end time, skipped")
                    continue

                # Handle datetime vs date-only
                start_dt = dtstart.dt
                end_dt = dtend.dt

                # Convert to datetime if date-only
                if not isinstance(start_dt, datetime):
                    start_dt = datetime.combine(start_dt, datetime.min.time())
                if not isinstance(end_dt, datetime):
                    end_dt = datetime.combine(end_dt, datetime.min.time())

                # Ensure timezone awareness
                if start_dt.tzinfo is None:
                    start_dt = start_dt.replace(tzinfo=tz.UTC)
                if end_dt.tzinfo is None:
                    end_dt = end_dt.replace(tzinfo=tz.UTC)

                # Skip past events
                if end_dt < now:
                    continue

                # Skip events too far in future
                if start_dt > cutoff:
                    continue

                # Use AI to categorize event (NO keywords!)
                categorization = ai_client.analyze_calendar_event(summary, description)
                block_type = categorization.get("category", "other")

                # Create BusyBlock
                block = BusyBlock(
                    user_id=user_id,
                    title=summary,
                    start=start_dt.isoformat(),
                    end=end_dt.isoformat(),
                    block_type=block_type
                )
                busy_blocks.append(block)

            except Exception as e:
                warnings.append(f"Failed to parse event: {str(e)}")
                continue

    if not busy_blocks:
        warnings.append("No future events found in calendar")

    return busy_blocks, warnings
