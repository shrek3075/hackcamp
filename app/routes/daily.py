"""
Daily study recommendations (Duolingo-style)
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from app.models import ScheduleBlock
from app.services.study_coach import get_todays_study_plan, generate_motivational_message
from app.clients.supabase import get_supabase_client

router = APIRouter(prefix="/daily", tags=["daily"])


@router.get("/{user_id}")
async def get_daily_plan(user_id: str, user_name: Optional[str] = "Student"):
    """
    Get today's study plan (Duolingo-style)

    Returns:
    - What to study today (specific time blocks)
    - Motivational message
    - Progress stats
    - Study streak
    """
    try:
        db = get_supabase_client()

        # Get latest timeline
        plan = db.get_latest_plan(user_id)

        if not plan:
            raise HTTPException(
                404,
                "No study plan found. Upload syllabus and calendar, then generate timeline."
            )

        # Convert blocks to ScheduleBlock objects
        schedule_blocks = [ScheduleBlock(**b) for b in plan.get("blocks", [])]

        # Get today's plan
        todays_plan = get_todays_study_plan(schedule_blocks, user_name)

        # Get progress stats (simplified for MVP)
        all_tasks = db.get_tasks(user_id)
        completed_tasks = [t for t in all_tasks if t.get("completed", False)]

        progress_percent = (len(completed_tasks) / len(all_tasks) * 100) if all_tasks else 0

        # Get streak (from daily_checkins table)
        # For MVP, assume streak = 0 (implement full tracking later)
        streak = 0

        # Generate motivational message
        todays_task_titles = [b.task_title for b in todays_plan["blocks"]]
        motivation = generate_motivational_message(
            user_name=user_name,
            streak_days=streak,
            todays_tasks=todays_task_titles,
            progress_percent=progress_percent
        )

        return {
            **todays_plan,
            "motivation": motivation,
            "progress_percent": round(progress_percent, 1),
            "streak": streak,
            "total_tasks": len(all_tasks),
            "completed_tasks": len(completed_tasks)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to get daily plan: {str(e)}")
