"""
Study coach service - Duolingo-style daily recommendations
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dateutil import parser, tz

from app.models import ScheduleBlock, Task
from app.clients.ai_client import get_ai_client


def get_todays_study_plan(
    schedule_blocks: List[ScheduleBlock],
    user_name: str = "Student"
) -> Dict[str, Any]:
    """
    Get today's study blocks and recommendations

    Args:
        schedule_blocks: All scheduled study blocks
        user_name: Student's name for personalization

    Returns:
        Dict with today's blocks, summary, and motivational message
    """
    today = datetime.now(tz=tz.UTC).date()

    # Filter blocks for today
    todays_blocks = []
    for block in schedule_blocks:
        try:
            block_date = parser.isoparse(block.start).date()
            if block_date == today:
                todays_blocks.append(block)
        except:
            continue

    # Sort by start time
    todays_blocks.sort(key=lambda b: parser.isoparse(b.start))

    # Calculate total hours today
    total_hours_today = sum(b.duration_hours for b in todays_blocks)

    # Generate summary
    if not todays_blocks:
        summary = "No study sessions scheduled for today. Great job staying ahead!"
        recommendation = "Review previous material or get ahead on upcoming tasks."
    else:
        task_count = len(set(b.task_title for b in todays_blocks))
        summary = f"{len(todays_blocks)} study sessions ({total_hours_today:.1f} hours) across {task_count} tasks"
        recommendation = f"Start with {todays_blocks[0].task_title} at {parser.isoparse(todays_blocks[0].start).strftime('%I:%M %p')}"

    return {
        "date": today.isoformat(),
        "blocks": todays_blocks,
        "total_hours": round(total_hours_today, 1),
        "summary": summary,
        "recommendation": recommendation
    }


def generate_motivational_message(
    user_name: str,
    streak_days: int,
    todays_tasks: List[str],
    progress_percent: float
) -> str:
    """
    Generate Duolingo-style motivational coaching message

    Args:
        user_name: Student's name
        streak_days: Current study streak
        todays_tasks: List of tasks for today
        progress_percent: Overall progress percentage

    Returns:
        Motivational message
    """
    ai_client = get_ai_client()

    progress_data = {
        "progress_percent": progress_percent,
        "completed_today": 0  # This would come from database
    }

    upcoming = [{"title": task} for task in todays_tasks[:3]]

    try:
        message = ai_client.generate_study_coach_message(
            student_name=user_name,
            progress_data=progress_data,
            upcoming_tasks=upcoming,
            streak_days=streak_days
        )
        return message
    except Exception as e:
        # Fallback messages
        if streak_days > 7:
            return f"Incredible {user_name}! {streak_days} days strong! You're crushing it! 🔥"
        elif streak_days > 0:
            return f"Nice work {user_name}! {streak_days}-day streak! Keep the momentum going!"
        else:
            return f"Welcome back {user_name}! Let's build that study streak together!"


def get_detailed_task_timeline(task: Task, current_date: str, busy_blocks: List[Dict]) -> Dict[str, Any]:
    """
    Generate detailed timeline for exam/project preparation

    Args:
        task: The task to create timeline for
        current_date: Today's date (ISO format)
        busy_blocks: Student's busy schedule

    Returns:
        Detailed study timeline with milestones
    """
    ai_client = get_ai_client()

    task_dict = {
        "title": task.title,
        "due": task.due_date,
        "type": task.task_type,
        "weight": task.weight,
        "effort_hours": task.effort_hours,
        "notes": task.notes
    }

    try:
        timeline = ai_client.create_study_timeline(
            task=task_dict,
            current_date=current_date,
            busy_blocks=busy_blocks
        )
        return timeline
    except Exception as e:
        # Fallback timeline
        return {
            "timeline": [
                {
                    "phase": "Preparation",
                    "days_before_due": 7,
                    "tasks": ["Review materials", "Practice problems"],
                    "estimated_hours": task.effort_hours or 10
                }
            ],
            "total_prep_hours": task.effort_hours or 10,
            "difficulty": "medium",
            "tips": ["Start early", "Take breaks", "Practice actively"]
        }
