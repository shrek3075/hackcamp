"""
Timeline generation and management routes
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from dateutil import tz
import uuid

from app.models import PlanGenerateRequest, PlanGenerateResponse, Task, BusyBlock, UserPreferences
from app.services.timeline_generator import generate_study_timeline
from app.clients.supabase import get_supabase_client

router = APIRouter(prefix="/timeline", tags=["timeline"])


@router.post("/generate", response_model=PlanGenerateResponse)
async def generate_timeline(request: PlanGenerateRequest):
    """
    Generate complete study timeline with specific time blocks

    Takes all tasks and busy blocks, creates optimized study schedule
    that works around calendar commitments.

    Returns schedule blocks with specific start/end times.
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

        # Generate timeline
        schedule_blocks, warnings, total_hours = generate_study_timeline(
            tasks=tasks,
            busy_blocks=busy_blocks,
            preferences=request.preferences or UserPreferences()
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

        return PlanGenerateResponse(
            plan_id=plan_id,
            user_id=request.user_id,
            generated_at=datetime.now(tz=tz.UTC),
            blocks=schedule_blocks,
            total_hours=total_hours,
            warnings=warnings
        )

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
    """Get user's most recent timeline"""
    try:
        db = get_supabase_client()
        plan = db.get_latest_plan(user_id)

        if not plan:
            raise HTTPException(404, "No timeline found. Generate one first.")

        return plan

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch timeline: {str(e)}")
