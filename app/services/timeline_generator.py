"""
Timeline generator - creates study schedule from tasks + busy blocks
"""
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from dateutil import parser, tz

from app.models import Task, BusyBlock, ScheduleBlock, UserPreferences


def generate_study_timeline(
    tasks: List[Task],
    busy_blocks: List[BusyBlock],
    preferences: UserPreferences = None
) -> Tuple[List[ScheduleBlock], List[str], float]:
    """
    Generate complete study timeline with specific time blocks

    Args:
        tasks: List of tasks with effort estimates
        busy_blocks: List of busy time blocks from calendar
        preferences: User scheduling preferences

    Returns:
        Tuple of (schedule_blocks, warnings, total_hours_scheduled)
    """
    if preferences is None:
        preferences = UserPreferences()

    warnings = []
    schedule_blocks = []

    # Filter tasks with due dates and effort
    schedulable_tasks = [
        t for t in tasks
        if not t.completed and t.due_date and t.effort_hours and t.effort_hours > 0
    ]

    if not schedulable_tasks:
        warnings.append("No tasks with due dates and effort estimates to schedule")
        return [], warnings, 0.0

    # Sort by priority (due soon = higher priority)
    schedulable_tasks.sort(key=lambda t: (parser.isoparse(t.due_date), -(t.weight or 0)))

    # Build busy intervals
    busy_intervals = []
    for block in busy_blocks:
        try:
            start = parser.isoparse(block.start)
            end = parser.isoparse(block.end)
            busy_intervals.append((start, end))
        except:
            continue

    # Scheduling parameters
    max_hours_per_day = preferences.max_hours_per_day
    min_block_hours = preferences.min_study_block_minutes / 60.0
    break_hours = preferences.break_duration_minutes / 60.0

    # Track remaining effort per task
    remaining_effort = {task.id or task.title: task.effort_hours for task in schedulable_tasks}

    # Start scheduling from today
    current_date = datetime.now(tz=tz.UTC).replace(hour=0, minute=0, second=0, microsecond=0)

    # Schedule each task
    for task in schedulable_tasks:
        task_key = task.id or task.title
        effort_needed = remaining_effort.get(task_key, 0)

        if effort_needed <= 0:
            continue

        # Calculate days until due
        due_date = parser.isoparse(task.due_date)
        days_until_due = (due_date.date() - current_date.date()).days

        if days_until_due < 0:
            warnings.append(f"Task '{task.title}' is overdue!")
            continue

        # Distribute effort over available days (leave 1 day buffer before due)
        days_to_distribute = max(1, days_until_due - 1)

        # Calculate sessions needed
        hours_per_session = min(3.0, effort_needed)  # Max 3h per session
        sessions_needed = int(effort_needed / hours_per_session) + (1 if effort_needed % hours_per_session > 0 else 0)

        # Schedule sessions
        sessions_scheduled = 0
        day_offset = 0

        while sessions_scheduled < sessions_needed and day_offset <= days_until_due:
            schedule_day = current_date + timedelta(days=day_offset)

            # Check daily limit
            day_hours_used = sum(
                b.duration_hours for b in schedule_blocks
                if parser.isoparse(b.start).date() == schedule_day.date()
            )

            if day_hours_used >= max_hours_per_day:
                day_offset += 1
                continue

            # Calculate session duration
            remaining_task_effort = remaining_effort[task_key]
            available_today = max_hours_per_day - day_hours_used
            session_duration = min(hours_per_session, remaining_task_effort, available_today)

            if session_duration < min_block_hours:
                day_offset += 1
                continue

            # Find free slot
            slot_start, slot_end = find_free_slot(
                day=schedule_day,
                duration_hours=session_duration,
                busy_intervals=busy_intervals,
                existing_blocks=schedule_blocks,
                preferences=preferences
            )

            if slot_start and slot_end:
                # Create schedule block
                block = ScheduleBlock(
                    task_id=task.id,
                    task_title=task.title,
                    start=slot_start.isoformat(),
                    end=slot_end.isoformat(),
                    duration_hours=round(session_duration, 2),
                    reason=build_reason(task, days_until_due - day_offset, sessions_scheduled, sessions_needed)
                )
                schedule_blocks.append(block)

                # Update tracking
                remaining_effort[task_key] -= session_duration
                sessions_scheduled += 1

                # Add break after this block
                busy_intervals.append((slot_start, slot_end + timedelta(hours=break_hours)))

            day_offset += 1

        # Check if fully scheduled
        if remaining_effort[task_key] > 0.5:
            warnings.append(f"Could not fully schedule '{task.title}' - need {remaining_effort[task_key]:.1f} more hours")

    total_hours = sum(b.duration_hours for b in schedule_blocks)

    if not schedule_blocks:
        warnings.append("No study blocks could be scheduled - calendar may be too busy")

    return schedule_blocks, warnings, total_hours


def find_free_slot(
    day: datetime,
    duration_hours: float,
    busy_intervals: List[Tuple[datetime, datetime]],
    existing_blocks: List[ScheduleBlock],
    preferences: UserPreferences
) -> Tuple[datetime, datetime]:
    """Find a free time slot on a given day"""

    # Parse preferred times
    start_time = preferences.preferred_start_time.split(":")
    end_time = preferences.preferred_end_time.split(":")

    day_start = day.replace(hour=int(start_time[0]), minute=int(start_time[1]), second=0, microsecond=0)
    day_end = day.replace(hour=int(end_time[0]), minute=int(end_time[1]), second=0, microsecond=0)

    # Collect all busy periods for this day
    all_busy = []

    # Add calendar busy blocks
    for start, end in busy_intervals:
        if start.date() == day.date() or end.date() == day.date():
            all_busy.append((max(start, day_start), min(end, day_end)))

    # Add existing scheduled blocks
    for block in existing_blocks:
        block_start = parser.isoparse(block.start)
        block_end = parser.isoparse(block.end)
        if block_start.date() == day.date():
            all_busy.append((block_start, block_end))

    # Sort by start time
    all_busy.sort(key=lambda x: x[0])

    # Find gaps
    current_time = day_start
    duration_delta = timedelta(hours=duration_hours)

    for busy_start, busy_end in all_busy:
        gap_duration = (busy_start - current_time).total_seconds() / 3600

        if gap_duration >= duration_hours:
            return current_time, current_time + duration_delta

        current_time = max(current_time, busy_end)

    # Check final gap
    final_gap = (day_end - current_time).total_seconds() / 3600
    if final_gap >= duration_hours:
        return current_time, current_time + duration_delta

    return None, None


def build_reason(task: Task, days_until_due: int, session_num: int, total_sessions: int) -> str:
    """Build human-readable reason for scheduling"""
    reasons = []

    if days_until_due <= 1:
        reasons.append("due tomorrow")
    elif days_until_due <= 3:
        reasons.append(f"due in {days_until_due} days")

    if task.weight and task.weight >= 20:
        reasons.append(f"{task.weight}% of grade")

    reasons.append(f"session {session_num + 1}/{total_sessions}")

    return ", ".join(reasons)
