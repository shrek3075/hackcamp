"""
Progress tracking service - streaks, stats, achievements
"""
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional
from dateutil import tz


def calculate_streak(checkin_dates: List[date]) -> int:
    """
    Calculate current study streak

    Args:
        checkin_dates: List of dates when user checked in

    Returns:
        Current streak in days
    """
    if not checkin_dates:
        return 0

    # Sort dates descending
    sorted_dates = sorted(checkin_dates, reverse=True)

    today = datetime.now(tz=tz.UTC).date()
    streak = 0

    # Check if checked in today or yesterday (grace period)
    if sorted_dates[0] not in [today, today - timedelta(days=1)]:
        return 0  # Streak broken

    # Start from most recent
    expected_date = sorted_dates[0]

    for checkin_date in sorted_dates:
        if checkin_date == expected_date or checkin_date == expected_date - timedelta(days=1):
            streak += 1
            expected_date = checkin_date - timedelta(days=1)
        else:
            break

    return streak


def calculate_progress_stats(
    total_tasks: int,
    completed_tasks: int,
    total_effort_hours: float,
    completed_hours: float,
    checkin_dates: List[date]
) -> Dict[str, Any]:
    """
    Calculate comprehensive progress statistics

    Args:
        total_tasks: Total number of tasks
        completed_tasks: Number of completed tasks
        total_effort_hours: Total estimated effort hours
        completed_hours: Hours studied so far
        checkin_dates: List of checkin dates

    Returns:
        Dict with progress statistics
    """
    task_completion_percent = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    hour_completion_percent = (completed_hours / total_effort_hours * 100) if total_effort_hours > 0 else 0

    streak = calculate_streak(checkin_dates)

    # Calculate weekly study hours
    week_ago = datetime.now(tz=tz.UTC).date() - timedelta(days=7)
    weekly_checkins = [d for d in checkin_dates if d >= week_ago]

    return {
        "task_completion_percent": round(task_completion_percent, 1),
        "hour_completion_percent": round(hour_completion_percent, 1),
        "completed_tasks": completed_tasks,
        "total_tasks": total_tasks,
        "completed_hours": round(completed_hours, 1),
        "total_hours": round(total_effort_hours, 1),
        "current_streak": streak,
        "weekly_study_days": len(weekly_checkins),
        "total_study_days": len(checkin_dates)
    }


def get_progress_badge(streak: int, total_hours: float) -> Dict[str, str]:
    """
    Get achievement badge based on progress

    Args:
        streak: Current streak days
        total_hours: Total hours studied

    Returns:
        Dict with badge info
    """
    badges = []

    # Streak badges
    if streak >= 30:
        badges.append({"name": "Study Master", "icon": "🏆", "description": "30-day streak!"})
    elif streak >= 14:
        badges.append({"name": "Dedicated Learner", "icon": "🔥", "description": "2-week streak!"})
    elif streak >= 7:
        badges.append({"name": "Week Warrior", "icon": "⭐", "description": "7-day streak!"})
    elif streak >= 3:
        badges.append({"name": "Getting Started", "icon": "🌟", "description": "3-day streak!"})

    # Hour badges
    if total_hours >= 100:
        badges.append({"name": "Century Club", "icon": "💯", "description": "100+ hours studied!"})
    elif total_hours >= 50:
        badges.append({"name": "Half Century", "icon": "📚", "description": "50+ hours studied!"})
    elif total_hours >= 20:
        badges.append({"name": "Committed Student", "icon": "📖", "description": "20+ hours studied!"})

    return badges if badges else [{"name": "Welcome!", "icon": "👋", "description": "Start your journey!"}]


def generate_progress_report(
    user_name: str,
    stats: Dict[str, Any],
    upcoming_deadlines: List[Dict]
) -> Dict[str, Any]:
    """
    Generate comprehensive progress report

    Args:
        user_name: Student's name
        stats: Progress statistics
        upcoming_deadlines: List of upcoming tasks

    Returns:
        Progress report with insights
    """
    badges = get_progress_badge(stats["current_streak"], stats["completed_hours"])

    # Generate insights
    insights = []

    if stats["current_streak"] > 0:
        insights.append(f"You're on a {stats['current_streak']}-day streak! Keep it up!")

    if stats["task_completion_percent"] >= 80:
        insights.append("You're crushing it! Over 80% of tasks completed!")
    elif stats["task_completion_percent"] < 30:
        insights.append("Let's pick up the pace. Focus on upcoming deadlines.")

    if stats["weekly_study_days"] >= 5:
        insights.append("Excellent consistency this week!")

    # Urgent tasks
    urgent_count = len([t for t in upcoming_deadlines if t.get("days_until_due", 999) <= 3])
    if urgent_count > 0:
        insights.append(f"⚠️ {urgent_count} tasks due within 3 days - prioritize these!")

    return {
        "user_name": user_name,
        "stats": stats,
        "badges": badges,
        "insights": insights,
        "generated_at": datetime.now(tz=tz.UTC).isoformat()
    }
