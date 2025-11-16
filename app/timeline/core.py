"""
Core Timeline Generation Engine - Advanced Scheduling Algorithm

This module creates optimal study schedules that:
- Prioritize tasks by due date and importance
- Respect busy blocks from calendar
- Distribute work evenly to avoid cramming
- Use spaced repetition principles
- Adapt to user's study preferences
"""
from datetime import datetime, timedelta, time as dt_time
from typing import List, Dict, Tuple, Optional
from dateutil import parser, tz
import math

from app.models import Task, BusyBlock, ScheduleBlock, UserPreferences


class TimelineEngine:
    """Advanced timeline generation engine"""

    def __init__(self, preferences: UserPreferences):
        self.preferences = preferences
        self.start_hour = int(preferences.preferred_start_time.split(":")[0])
        self.start_minute = int(preferences.preferred_start_time.split(":")[1])
        self.end_hour = int(preferences.preferred_end_time.split(":")[0])
        self.end_minute = int(preferences.preferred_end_time.split(":")[1])

    def generate_timeline(
        self,
        tasks: List[Task],
        busy_blocks: List[BusyBlock]
    ) -> Tuple[List[ScheduleBlock], Dict[str, any]]:
        """
        Generate optimal study timeline

        Returns:
            Tuple of (schedule_blocks, metadata)
        """
        # Filter and prepare tasks
        schedulable_tasks = self._prepare_tasks(tasks)

        if not schedulable_tasks:
            return [], {
                "total_hours": 0,
                "tasks_scheduled": 0,
                "warnings": ["No tasks with due dates to schedule"]
            }

        # Build busy intervals
        busy_intervals = self._build_busy_intervals(busy_blocks)

        # Sort tasks by priority
        prioritized_tasks = self._prioritize_tasks(schedulable_tasks)

        # Generate schedule
        schedule_blocks = []
        metadata = {
            "total_hours": 0,
            "tasks_scheduled": 0,
            "tasks_partial": [],
            "tasks_unscheduled": [],
            "warnings": [],
            "stats": {}
        }

        # Track remaining effort
        remaining_effort = {task.id or task.title: task.effort_hours for task in prioritized_tasks}

        # Schedule each task
        for task in prioritized_tasks:
            task_key = task.id or task.title
            effort_needed = remaining_effort.get(task_key, 0)

            if effort_needed <= 0:
                continue

            # Calculate scheduling window
            due_date = parser.isoparse(task.due_date)
            today = datetime.now(tz=tz.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
            days_until_due = (due_date.date() - today.date()).days

            if days_until_due < 0:
                metadata["warnings"].append(f"Task '{task.title}' is overdue!")
                metadata["tasks_unscheduled"].append(task.title)
                continue

            # Use intelligent scheduling strategy
            task_blocks = self._schedule_task(
                task=task,
                effort_needed=effort_needed,
                days_until_due=days_until_due,
                today=today,
                busy_intervals=busy_intervals,
                existing_blocks=schedule_blocks
            )

            schedule_blocks.extend(task_blocks)

            # Update tracking
            scheduled_hours = sum(b.duration_hours for b in task_blocks)
            remaining_effort[task_key] -= scheduled_hours
            metadata["total_hours"] += scheduled_hours

            if remaining_effort[task_key] > 0.5:
                metadata["tasks_partial"].append({
                    "title": task.title,
                    "remaining_hours": round(remaining_effort[task_key], 1)
                })
            else:
                metadata["tasks_scheduled"] += 1

        # Sort blocks by start time
        schedule_blocks.sort(key=lambda b: parser.isoparse(b.start))

        # Add statistics
        metadata["stats"] = self._calculate_stats(schedule_blocks, prioritized_tasks)

        return schedule_blocks, metadata

    def _prepare_tasks(self, tasks: List[Task]) -> List[Task]:
        """Filter and validate tasks for scheduling"""
        return [
            t for t in tasks
            if not t.completed
            and t.due_date
            and t.effort_hours
            and t.effort_hours > 0
        ]

    def _prioritize_tasks(self, tasks: List[Task]) -> List[Task]:
        """
        Sort tasks by intelligent priority scoring

        Priority factors:
        1. Due date urgency (60%)
        2. Weight/importance (30%)
        3. Effort required (10%)
        """
        def priority_score(task: Task) -> float:
            # Days until due (lower is higher priority)
            try:
                due = parser.isoparse(task.due_date)
                today = datetime.now(tz=tz.UTC)
                days_until = max((due - today).days, 0)

                # Urgency score (exponential decay)
                urgency = 100 / (days_until + 1)  # +1 to avoid division by zero

                # Weight score
                weight_score = (task.weight or 10) * 3  # Scale weight

                # Effort score (prefer getting big tasks done early)
                effort_score = (task.effort_hours or 3) * 0.5

                # Combined score
                return urgency * 0.6 + weight_score * 0.3 + effort_score * 0.1

            except:
                return 0

        return sorted(tasks, key=priority_score, reverse=True)

    def _build_busy_intervals(self, busy_blocks: List[BusyBlock]) -> List[Tuple[datetime, datetime]]:
        """Convert busy blocks to datetime intervals"""
        intervals = []
        for block in busy_blocks:
            try:
                start = parser.isoparse(block.start)
                end = parser.isoparse(block.end)
                intervals.append((start, end))
            except:
                continue
        return intervals

    def _schedule_task(
        self,
        task: Task,
        effort_needed: float,
        days_until_due: int,
        today: datetime,
        busy_intervals: List[Tuple[datetime, datetime]],
        existing_blocks: List[ScheduleBlock]
    ) -> List[ScheduleBlock]:
        """
        Schedule a single task using intelligent distribution

        Strategy:
        - Distribute study sessions over available days
        - Use spaced repetition (don't cram)
        - Keep sessions between 1-3 hours
        - Leave buffer days before deadline
        """
        blocks = []

        # Calculate optimal session length
        optimal_session = min(3.0, max(1.0, effort_needed / 3))

        # Number of sessions needed
        num_sessions = math.ceil(effort_needed / optimal_session)

        # Days to distribute over (leave 1-2 buffer days)
        buffer_days = min(2, max(1, days_until_due // 4))
        distribution_days = max(1, days_until_due - buffer_days)

        # Calculate spacing between sessions
        if num_sessions > 1:
            session_spacing = max(1, distribution_days // num_sessions)
        else:
            session_spacing = 1

        # Schedule sessions
        sessions_scheduled = 0
        remaining = effort_needed
        current_day_offset = 0

        while sessions_scheduled < num_sessions and remaining > 0.5 and current_day_offset <= days_until_due:
            schedule_date = today + timedelta(days=current_day_offset)

            # Calculate this session's duration
            session_duration = min(optimal_session, remaining)

            # Check daily limit
            day_hours_used = self._get_day_hours_used(schedule_date, existing_blocks, blocks)
            available_today = self.preferences.max_hours_per_day - day_hours_used

            if available_today < 0.5:
                current_day_offset += 1
                continue

            # Adjust session to fit in available time
            session_duration = min(session_duration, available_today)

            # Find free slot
            slot_start, slot_end = self._find_free_slot(
                day=schedule_date,
                duration_hours=session_duration,
                busy_intervals=busy_intervals,
                existing_blocks=existing_blocks + blocks
            )

            if slot_start and slot_end:
                # Create schedule block
                block = ScheduleBlock(
                    task_id=task.id,
                    task_title=task.title,
                    start=slot_start.isoformat(),
                    end=slot_end.isoformat(),
                    duration_hours=round(session_duration, 2),
                    reason=self._build_reason(task, sessions_scheduled + 1, num_sessions, days_until_due - current_day_offset)
                )
                blocks.append(block)

                remaining -= session_duration
                sessions_scheduled += 1

                # Move to next scheduled day (spaced repetition)
                current_day_offset += session_spacing
            else:
                # No slot found, try next day
                current_day_offset += 1

        return blocks

    def _get_day_hours_used(
        self,
        date: datetime,
        *block_lists: List[ScheduleBlock]
    ) -> float:
        """Calculate total hours already scheduled on a given day"""
        total = 0.0
        for block_list in block_lists:
            for block in block_list:
                try:
                    block_date = parser.isoparse(block.start).date()
                    if block_date == date.date():
                        total += block.duration_hours
                except:
                    continue
        return total

    def _find_free_slot(
        self,
        day: datetime,
        duration_hours: float,
        busy_intervals: List[Tuple[datetime, datetime]],
        existing_blocks: List[ScheduleBlock]
    ) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Find a free time slot on a given day"""
        # Define day boundaries
        day_start = day.replace(hour=self.start_hour, minute=self.start_minute, second=0, microsecond=0)
        day_end = day.replace(hour=self.end_hour, minute=self.end_minute, second=0, microsecond=0)

        duration_delta = timedelta(hours=duration_hours)
        min_duration = timedelta(minutes=self.preferences.min_study_block_minutes)

        if duration_delta < min_duration:
            return None, None

        # Collect all busy periods for this day
        all_busy = []

        # Add calendar busy blocks
        for start, end in busy_intervals:
            if start.date() == day.date() or end.date() == day.date():
                all_busy.append((max(start, day_start), min(end, day_end)))

        # Add existing scheduled blocks
        for block in existing_blocks:
            try:
                block_start = parser.isoparse(block.start)
                block_end = parser.isoparse(block.end)
                if block_start.date() == day.date():
                    # Add break time after this block
                    break_end = block_end + timedelta(minutes=self.preferences.break_duration_minutes)
                    all_busy.append((block_start, break_end))
            except:
                continue

        # Sort busy periods
        all_busy.sort(key=lambda x: x[0])

        # Find gaps
        current_time = day_start

        for busy_start, busy_end in all_busy:
            gap_duration = busy_start - current_time

            if gap_duration >= duration_delta:
                return current_time, current_time + duration_delta

            current_time = max(current_time, busy_end)

        # Check final gap
        if (day_end - current_time) >= duration_delta:
            return current_time, current_time + duration_delta

        return None, None

    def _build_reason(self, task: Task, session_num: int, total_sessions: int, days_until: int) -> str:
        """Build human-readable scheduling reason"""
        reasons = []

        if days_until <= 1:
            reasons.append("⚠️ DUE TOMORROW")
        elif days_until <= 3:
            reasons.append(f"Due in {days_until} days")

        if task.weight and task.weight >= 20:
            reasons.append(f"{task.weight}% of grade")

        reasons.append(f"Session {session_num}/{total_sessions}")

        if session_num == 1:
            reasons.append("First session")
        elif session_num == total_sessions:
            reasons.append("Final review")

        return " • ".join(reasons)

    def _calculate_stats(self, blocks: List[ScheduleBlock], tasks: List[Task]) -> Dict:
        """Calculate schedule statistics"""
        if not blocks:
            return {}

        # Group by day
        days = {}
        for block in blocks:
            try:
                date = parser.isoparse(block.start).date()
                if date not in days:
                    days[date] = []
                days[date].append(block)
            except:
                continue

        # Calculate stats
        daily_hours = {date: sum(b.duration_hours for b in blocks) for date, blocks in days.items()}

        return {
            "total_days_scheduled": len(days),
            "avg_hours_per_day": round(sum(daily_hours.values()) / len(daily_hours), 1) if daily_hours else 0,
            "busiest_day": max(daily_hours.items(), key=lambda x: x[1])[0].isoformat() if daily_hours else None,
            "busiest_day_hours": max(daily_hours.values()) if daily_hours else 0,
        }
