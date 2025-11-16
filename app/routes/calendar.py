"""
Calendar upload and parsing routes
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from app.models import CalendarIngestResponse, BusyBlock
from app.services.calendar_parser import parse_ics_calendar
from app.clients.supabase import get_supabase_client

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.post("/upload", response_model=CalendarIngestResponse)
async def upload_calendar(
    user_id: str = Form(...),
    file: UploadFile = File(...),
    days_ahead: int = Form(30)
):
    """
    Upload .ics calendar file and extract busy blocks

    AI categorizes events (no keyword matching):
    - class: Lectures, labs, tutorials
    - work: Job, meetings
    - personal: Gym, appointments
    - study: Study sessions
    - other: Everything else

    Returns busy blocks for schedule generation
    """
    try:
        # Read .ics file
        ics_content = (await file.read()).decode('utf-8')

        # Parse calendar with AI categorization
        busy_blocks, warnings = parse_ics_calendar(
            ics_content=ics_content,
            user_id=user_id,
            days_ahead=days_ahead
        )

        # Save to database
        db = get_supabase_client()
        blocks_data = [block.model_dump(exclude={"id"}) for block in busy_blocks]

        saved_blocks = db.insert_busy_blocks(blocks_data)

        # Convert back to BusyBlock objects
        final_blocks = [BusyBlock(**block_dict) for block_dict in saved_blocks]

        return CalendarIngestResponse(
            success=True,
            blocks_extracted=len(final_blocks),
            busy_blocks=final_blocks
        )

    except Exception as e:
        raise HTTPException(500, f"Calendar parsing failed: {str(e)}")


@router.get("/busy-blocks/{user_id}")
async def get_busy_blocks(user_id: str):
    """Get all busy blocks for a user"""
    try:
        db = get_supabase_client()
        blocks = db.get_busy_blocks(user_id)
        return {"busy_blocks": blocks}
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch busy blocks: {str(e)}")
