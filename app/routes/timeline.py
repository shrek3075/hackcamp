"""
Timeline generation and management routes - UPDATED with advanced engine
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from dateutil import tz
import uuid

from app.models import PlanGenerateRequest, Task, BusyBlock, UserPreferences
from app.timeline.core import TimelineEngine
from app.clients.supabase import get_supabase_client

router = APIRouter(prefix="/timeline", tags=["timeline"])


@router.post("/generate")
async def generate_timeline(request: PlanGenerateRequest):
    """
    Generate optimized study timeline with advanced scheduling algorithm

    Features:
    - Intelligent task prioritization (urgency + importance)
    - Spaced repetition (avoids cramming)
    - Respects busy blocks from calendar
    - Distributes work evenly across days
    - Adaptive session lengths (1-3 hours)
    - Buffer days before deadlines

    Returns schedule blocks with detailed metadata
    """
    try:
        db = get_supabase_client()

        # Get user's incomplete tasks
        tasks_data = db.get_tasks(request.user_id, completed=False)
        tasks = [Task(**t) for t in tasks_data]

        if not tasks:
            raise HTTPException(400, "No tasks found. Upload syllabus first.")

        # Get busy blocks
        blocks_data = db.get_busy_blocks(request.user_id)
        busy_blocks = [BusyBlock(**b) for b in blocks_data]

        # Initialize timeline engine
        preferences = request.preferences or UserPreferences()
        engine = TimelineEngine(preferences)

        # Generate timeline
        schedule_blocks, metadata = engine.generate_timeline(tasks, busy_blocks)

        if not schedule_blocks:
            raise HTTPException(
                400,
                f"Could not generate timeline. {'; '.join(metadata.get('warnings', []))}"
            )

        # Save plan to database
        plan_id = str(uuid.uuid4())
        plan_data = {
            "id": plan_id,
            "user_id": request.user_id,
            "generated_at": datetime.now(tz=tz.UTC).isoformat(),
            "blocks": [block.model_dump() for block in schedule_blocks],
            "version": 1
        }

        db.insert_plan(plan_data)

        # Return enhanced response
        return {
            "plan_id": plan_id,
            "user_id": request.user_id,
            "generated_at": datetime.now(tz=tz.UTC).isoformat(),
            "blocks": schedule_blocks,
            "metadata": {
                "total_hours": metadata["total_hours"],
                "tasks_scheduled": metadata["tasks_scheduled"],
                "tasks_partial": metadata.get("tasks_partial", []),
                "warnings": metadata.get("warnings", []),
                "stats": metadata.get("stats", {})
            },
            "visualization": _generate_calendar_view(schedule_blocks)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Timeline generation failed: {str(e)}")


@router.get("/{plan_id}")
async def get_timeline(plan_id: str):
    """Get a specific timeline by ID"""
    try:
        db = get_supabase_client()
        plan = db.get_plan(plan_id)

        if not plan:
            raise HTTPException(404, "Timeline not found")

        return plan

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch timeline: {str(e)}")


@router.get("/latest/{user_id}")
async def get_latest_timeline(user_id: str):
    """Get user's most recent timeline with visualization"""
    try:
        db = get_supabase_client()
        plan = db.get_latest_plan(user_id)

        if not plan:
            raise HTTPException(404, "No timeline found. Generate one first.")

        # Add visualization
        from app.models import ScheduleBlock
        blocks = [ScheduleBlock(**b) for b in plan.get("blocks", [])]
        plan["visualization"] = _generate_calendar_view(blocks)

        return plan

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch timeline: {str(e)}")


def _generate_calendar_view(blocks: list) -> dict:
    """Generate a visual calendar representation of the schedule"""
    if not blocks:
        return {"days": [], "summary": "No study sessions scheduled"}

    from dateutil import parser
    from collections import defaultdict

    # Group by day
    days_data = defaultdict(list)
    for block in blocks:
        try:
            start = parser.isoparse(block.start)
            date_key = start.date().isoformat()
            days_data[date_key].append({
                "task": block.task_title,
                "start_time": start.strftime("%I:%M %p"),
                "end_time": parser.isoparse(block.end).strftime("%I:%M %p"),
                "duration": f"{block.duration_hours}h",
                "reason": block.reason
            })
        except:
            continue

    # Sort and format
    calendar_days = []
    for date, sessions in sorted(days_data.items()):
        total_hours = sum(
            parser.isoparse(b.end).timestamp() - parser.isoparse(b.start).timestamp()
            for b in blocks
            if parser.isoparse(b.start).date().isoformat() == date
        ) / 3600

        calendar_days.append({
            "date": date,
            "day_name": parser.isoparse(date).strftime("%A"),
            "sessions": sessions,
            "total_hours": round(total_hours, 1),
            "session_count": len(sessions)
        })

    return {
        "days": calendar_days,
        "summary": f"{len(calendar_days)} days scheduled, {len(blocks)} total sessions"
    }
