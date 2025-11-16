"""
Progress tracking, streaks, and stats routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, date
from typing import List
from dateutil import tz

from app.services.progress_tracker import (
    calculate_progress_stats,
    generate_progress_report,
    get_progress_badge
)
from app.clients.supabase import get_supabase_client

router = APIRouter(prefix="/progress", tags=["progress"])


class CheckinRequest(BaseModel):
    user_id: str
    completed_block_ids: List[str] = []  # IDs of study blocks completed today


@router.post("/checkin")
async def daily_checkin(request: CheckinRequest):
    """
    Mark daily check-in (Duolingo-style)

    Updates:
    - Daily checkin record
    - Study streak
    - Completed study blocks
    - Total hours studied

    Returns updated streak and stats
    """
    try:
        db = get_supabase_client()

        # Record check-in for today
        today = date.today()
        checkin_data = {
            "user_id": request.user_id,
            "date": today.isoformat(),
            "completed": True,
            "completed_at": datetime.now(tz=tz.UTC).isoformat()
        }

        # Save checkin (upsert to handle multiple checkins per day)
        # Note: Implement upsert in supabase.py or handle duplicates

        # Mark study blocks as completed
        for block_id in request.completed_block_ids:
            # Update study blocks table (implement this in supabase.py)
            pass

        # Get all checkin dates for streak calculation
        # For MVP, simplified implementation
        checkin_dates = [today]  # Would fetch from database in production

        # Calculate stats
        all_tasks = db.get_tasks(request.user_id)
        completed_tasks = [t for t in all_tasks if t.get("completed", False)]

        total_effort = sum(t.get("effort_hours", 0) for t in all_tasks)
        completed_effort = sum(t.get("effort_hours", 0) for t in completed_tasks)

        stats = calculate_progress_stats(
            total_tasks=len(all_tasks),
            completed_tasks=len(completed_tasks),
            total_effort_hours=total_effort,
            completed_hours=completed_effort,
            checkin_dates=checkin_dates
        )

        badges = get_progress_badge(stats["current_streak"], stats["completed_hours"])

        return {
            "success": True,
            "message": f"Great job! {stats['current_streak']}-day streak!",
            "stats": stats,
            "badges": badges
        }

    except Exception as e:
        raise HTTPException(500, f"Checkin failed: {str(e)}")


@router.get("/stats/{user_id}")
async def get_progress_stats_route(user_id: str):
    """
    Get comprehensive progress statistics

    Returns:
    - Task completion percentages
    - Hours studied
    - Current streak
    - Weekly study days
    - Badges and achievements
    """
    try:
        db = get_supabase_client()

        # Get tasks
        all_tasks = db.get_tasks(user_id)
        completed_tasks = [t for t in all_tasks if t.get("completed", False)]

        # Calculate effort
        total_effort = sum(t.get("effort_hours", 0) for t in all_tasks)
        completed_effort = sum(t.get("effort_hours", 0) for t in completed_tasks)

        # For MVP: simplified checkin dates (would fetch from database)
        checkin_dates = []  # Implement proper database query

        stats = calculate_progress_stats(
            total_tasks=len(all_tasks),
            completed_tasks=len(completed_tasks),
            total_effort_hours=total_effort,
            completed_hours=completed_effort,
            checkin_dates=checkin_dates
        )

        badges = get_progress_badge(stats["current_streak"], stats["completed_hours"])

        return {
            "stats": stats,
            "badges": badges
        }

    except Exception as e:
        raise HTTPException(500, f"Failed to get stats: {str(e)}")


@router.get("/report/{user_id}")
async def get_progress_report_route(user_id: str, user_name: str = "Student"):
    """
    Get comprehensive progress report with insights

    Returns:
    - All stats
    - Achievements and badges
    - Personalized insights
    - Upcoming deadline warnings
    """
    try:
        db = get_supabase_client()

        # Get stats (reuse logic from above)
        all_tasks = db.get_tasks(user_id)
        completed_tasks = [t for t in all_tasks if t.get("completed", False)]

        total_effort = sum(t.get("effort_hours", 0) for t in all_tasks)
        completed_effort = sum(t.get("effort_hours", 0) for t in completed_tasks)

        checkin_dates = []  # Simplified for MVP

        stats = calculate_progress_stats(
            total_tasks=len(all_tasks),
            completed_tasks=len(completed_tasks),
            total_effort_hours=total_effort,
            completed_hours=completed_effort,
            checkin_dates=checkin_dates
        )

        # Get upcoming deadlines
        incomplete_tasks = [t for t in all_tasks if not t.get("completed", False)]

        # Sort by due date
        from dateutil import parser as date_parser

        upcoming = []
        for task in incomplete_tasks:
            if task.get("due_date"):
                try:
                    due = date_parser.isoparse(task["due_date"])
                    days_until = (due.date() - date.today()).days
                    upcoming.append({
                        "title": task["title"],
                        "due_date": task["due_date"],
                        "days_until_due": days_until
                    })
                except:
                    pass

        upcoming.sort(key=lambda x: x["days_until_due"])

        # Generate report
        report = generate_progress_report(
            user_name=user_name,
            stats=stats,
            upcoming_deadlines=upcoming[:5]
        )

        return report

    except Exception as e:
        raise HTTPException(500, f"Failed to generate report: {str(e)}")


@router.post("/task/{task_id}/complete")
async def mark_task_complete(task_id: str):
    """Mark a task as completed"""
    try:
        db = get_supabase_client()

        db.update_task(task_id, {"completed": True, "completed_at": datetime.now(tz=tz.UTC).isoformat()})

        return {"success": True, "message": "Task marked complete!"}

    except Exception as e:
        raise HTTPException(500, f"Failed to mark task complete: {str(e)}")
