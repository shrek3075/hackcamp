"""
Free time analysis from calendar busy blocks
"""
from typing import List, Dict, Tuple
from datetime import datetime, timedelta, time as dt_time
from dateutil import parser, tz

from app.models import BusyBlock


def analyze_free_time(
    busy_blocks: List[BusyBlock],
    days_ahead: int = 14,
    work_start_hour: int = 9,
    work_end_hour: int = 22,
    min_block_minutes: int = 30,
    preferred_study_start: int = None,
    preferred_study_end: int = None
) -> Dict:
    """
    Analyze calendar to find free time slots available for studying

    Args:
        busy_blocks: List of busy calendar events
        days_ahead: How many days ahead to analyze
        work_start_hour: Start of usable day (e.g., 9am)
        work_end_hour: End of usable day (e.g., 10pm)
        min_block_minutes: Minimum free time to be useful (default 30 min)
        preferred_study_start: Preferred study start hour (e.g., 17 for 5pm)
        preferred_study_end: Preferred study end hour (e.g., 21 for 9pm)

    Returns:
        Dict with free time analysis:
        - total_free_hours: Total free hours available
        - days: List of days with free time breakdown
        - busiest_days: Days with least free time
        - best_study_days: Days with most free time
        - available_study_slots: Clean list of ALL available study times
    """
    # Get date range
    today = datetime.now(tz=tz.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = today + timedelta(days=days_ahead)

    # Group busy blocks by date
    busy_by_date = {}
    for block in busy_blocks:
        try:
            block_start = parser.isoparse(block.start)
            block_end = parser.isoparse(block.end)

            # Get date key
            date_key = block_start.date()

            if date_key not in busy_by_date:
                busy_by_date[date_key] = []

            busy_by_date[date_key].append((block_start, block_end))
        except:
            continue

    # Analyze each day
    days_analysis = []
    total_free_hours = 0.0

    current_date = today
    while current_date < end_date:
        date_key = current_date.date()

        # Define working hours for this day
        day_start = current_date.replace(hour=work_start_hour, minute=0, second=0, microsecond=0)
        day_end = current_date.replace(hour=work_end_hour, minute=0, second=0, microsecond=0)

        # Get busy blocks for this day
        day_busy = busy_by_date.get(date_key, [])

        # Sort by start time
        day_busy.sort(key=lambda x: x[0])

        # Find free time slots
        free_slots = []
        current_time = day_start

        for busy_start, busy_end in day_busy:
            # Clamp busy times to working hours
            busy_start = max(busy_start, day_start)
            busy_end = min(busy_end, day_end)

            # Check gap before this busy block
            if current_time < busy_start:
                gap_minutes = (busy_start - current_time).total_seconds() / 60
                if gap_minutes >= min_block_minutes:
                    free_slots.append({
                        "start": current_time.strftime("%H:%M"),
                        "end": busy_start.strftime("%H:%M"),
                        "duration_hours": round(gap_minutes / 60, 1)
                    })

            # Move current time to end of busy block
            current_time = max(current_time, busy_end)

        # Check final gap until end of day
        if current_time < day_end:
            gap_minutes = (day_end - current_time).total_seconds() / 60
            if gap_minutes >= min_block_minutes:
                free_slots.append({
                    "start": current_time.strftime("%H:%M"),
                    "end": day_end.strftime("%H:%M"),
                    "duration_hours": round(gap_minutes / 60, 1)
                })

        # Calculate stats for this day
        free_hours = sum(slot["duration_hours"] for slot in free_slots)
        busy_hours = sum((end - start).total_seconds() / 3600 for start, end in day_busy)
        total_work_hours = (day_end - day_start).total_seconds() / 3600

        days_analysis.append({
            "date": date_key.isoformat(),
            "day_name": current_date.strftime("%A"),
            "free_hours": round(free_hours, 1),
            "busy_hours": round(busy_hours, 1),
            "total_work_hours": round(total_work_hours, 1),
            "free_percentage": round((free_hours / total_work_hours * 100), 1) if total_work_hours > 0 else 0,
            "free_slots": free_slots,
            "num_busy_blocks": len(day_busy)
        })

        total_free_hours += free_hours
        current_date += timedelta(days=1)

    # Find busiest and best days
    sorted_by_free_time = sorted(days_analysis, key=lambda d: d["free_hours"])
    busiest_days = sorted_by_free_time[:3]  # Least free time
    best_study_days = sorted_by_free_time[-3:]  # Most free time
    best_study_days.reverse()

    # Calculate average
    avg_free_per_day = total_free_hours / len(days_analysis) if days_analysis else 0

    # Build clean list of ALL available study slots (filtered by preferred times)
    available_study_slots = []
    preferred_study_hours = 0.0

    for day in days_analysis:
        for slot in day["free_slots"]:
            # Parse slot times
            slot_start_hour = int(slot["start"].split(":")[0])
            slot_end_hour = int(slot["end"].split(":")[0])
            slot_end_minute = int(slot["end"].split(":")[1])

            # If preferred times are set, filter slots
            if preferred_study_start is not None and preferred_study_end is not None:
                # Check if slot overlaps with preferred study time
                if slot_end_hour <= preferred_study_start or slot_start_hour >= preferred_study_end:
                    continue  # Skip - no overlap with preferred time

                # Clip slot to preferred times
                actual_start = max(slot_start_hour, preferred_study_start)
                actual_end = min(slot_end_hour + (1 if slot_end_minute > 0 else 0), preferred_study_end)

                if actual_end <= actual_start:
                    continue  # Skip - no usable time after clipping

                clipped_duration = actual_end - actual_start

                # Format times
                start_str = f"{actual_start:02d}:00"
                end_str = f"{actual_end:02d}:00"
            else:
                # No preference - use full slot
                clipped_duration = slot["duration_hours"]
                start_str = slot["start"]
                end_str = slot["end"]

            # Only add if duration is meaningful (>= 30 min)
            if clipped_duration >= 0.5:
                available_study_slots.append({
                    "date": day["date"],
                    "day_name": day["day_name"],
                    "start": start_str,
                    "end": end_str,
                    "duration_hours": round(clipped_duration, 1)
                })
                preferred_study_hours += clipped_duration

    return {
        "total_free_hours": round(total_free_hours, 1),
        "avg_free_hours_per_day": round(avg_free_per_day, 1),
        "days_analyzed": len(days_analysis),
        "days": days_analysis,
        "busiest_days": [
            {
                "date": d["date"],
                "day_name": d["day_name"],
                "free_hours": d["free_hours"],
                "busy_blocks": d["num_busy_blocks"]
            }
            for d in busiest_days
        ],
        "best_study_days": [
            {
                "date": d["date"],
                "day_name": d["day_name"],
                "free_hours": d["free_hours"],
                "free_percentage": d["free_percentage"]
            }
            for d in best_study_days
        ],
        "available_study_slots": available_study_slots,
        "total_preferred_hours": round(preferred_study_hours, 1) if preferred_study_start else None
    }


def get_recommended_study_hours(
    busy_blocks: List[BusyBlock],
    days_until_exam: int,
    total_study_hours_needed: float
) -> Dict:
    """
    Get recommended hours per day based on available free time

    Args:
        busy_blocks: Calendar busy blocks
        days_until_exam: Days until the exam
        total_study_hours_needed: Total hours needed to study

    Returns:
        Dict with recommendations
    """
    # Analyze free time
    analysis = analyze_free_time(
        busy_blocks=busy_blocks,
        days_ahead=days_until_exam
    )

    total_free = analysis["total_free_hours"]
    avg_free = analysis["avg_free_hours_per_day"]

    # Calculate recommended hours per day
    if total_free >= total_study_hours_needed:
        # We have enough time, distribute evenly
        recommended_hours_per_day = total_study_hours_needed / days_until_exam
        feasibility = "comfortable"
        message = f"You have {total_free}h free time available. Studying {recommended_hours_per_day:.1f}h/day will be comfortable."
    elif total_free >= total_study_hours_needed * 0.7:
        # Tight but doable
        recommended_hours_per_day = min(avg_free * 0.8, total_study_hours_needed / days_until_exam)
        feasibility = "tight"
        message = f"You have {total_free}h free time. You'll need to use most of your free time to study."
    else:
        # Not enough time
        recommended_hours_per_day = avg_free * 0.9  # Use 90% of free time
        feasibility = "challenging"
        message = f"Warning: Only {total_free}h available but need {total_study_hours_needed}h. Consider starting earlier or reducing scope."

    return {
        "recommended_hours_per_day": round(recommended_hours_per_day, 1),
        "total_free_hours": total_free,
        "total_needed_hours": total_study_hours_needed,
        "feasibility": feasibility,
        "message": message,
        "free_time_analysis": analysis
    }
