"""
Calendar upload and parsing routes
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from app.models import CalendarIngestResponse, BusyBlock
from app.services.calendar_parser import parse_ics_calendar
from app.clients.supabase import get_supabase_client

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.post("/upload")
async def upload_calendar(
    user_id: str = Form(...),
    file: UploadFile = File(...),
    days_ahead: int = Form(30),
    exam_date: Optional[str] = Form(None),
    preferred_study_start: Optional[int] = Form(None),
    preferred_study_end: Optional[int] = Form(None)
):
    """
    Upload .ics calendar file and extract busy blocks with free time analysis

    AI categorizes events (no keyword matching):
    - class: Lectures, labs, tutorials
    - work: Job, meetings
    - personal: Gym, appointments
    - study: Study sessions
    - other: Everything else

    Returns busy blocks + free time analysis
    """
    try:
        from app.services.free_time_analyzer import analyze_free_time
        from datetime import datetime

        # Calculate actual days to parse
        actual_days_ahead = days_ahead
        if exam_date:
            try:
                exam_dt = datetime.fromisoformat(exam_date)
                today = datetime.now()
                actual_days_ahead = max(1, (exam_dt - today).days)
                print(f"[CALENDAR] Parsing calendar until exam date: {exam_date} ({actual_days_ahead} days)")
            except:
                print(f"[WARN] Invalid exam date format, using default {days_ahead} days")

        # Read .ics file
        ics_content = (await file.read()).decode('utf-8')

        # Parse calendar with AI categorization
        busy_blocks, warnings = parse_ics_calendar(
            ics_content=ics_content,
            user_id=user_id,
            days_ahead=actual_days_ahead
        )

        # Save to database
        db = get_supabase_client()
        blocks_data = [block.model_dump(exclude={"id"}) for block in busy_blocks]

        saved_blocks = db.insert_busy_blocks(blocks_data)

        # Convert back to BusyBlock objects
        final_blocks = [BusyBlock(**block_dict) for block_dict in saved_blocks]

        # Analyze free time automatically
        free_time_analysis = None
        if final_blocks:
            try:
                free_time_analysis = analyze_free_time(
                    busy_blocks=final_blocks,
                    days_ahead=actual_days_ahead,
                    work_start_hour=9,
                    work_end_hour=22,
                    min_block_minutes=30,
                    preferred_study_start=preferred_study_start,
                    preferred_study_end=preferred_study_end
                )

                if preferred_study_start and preferred_study_end:
                    print(f"[OK] Free time analyzed: {free_time_analysis['total_preferred_hours']}h available during preferred times ({preferred_study_start}:00-{preferred_study_end}:00)")
                else:
                    print(f"[OK] Free time analyzed: {free_time_analysis['total_free_hours']}h available")
            except Exception as e:
                print(f"[WARN] Free time analysis failed: {e}")
                warnings.append(f"Free time analysis failed: {str(e)}")

        return {
            "success": True,
            "blocks_extracted": len(final_blocks),
            "busy_blocks": final_blocks,
            "free_time_analysis": free_time_analysis,
            "days_parsed": actual_days_ahead,
            "warnings": warnings
        }

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


@router.get("/free-time/{user_id}")
async def analyze_user_free_time(
    user_id: str,
    days_ahead: int = 14
):
    """
    Analyze available free time from calendar

    Returns:
    - Total free hours available
    - Daily breakdown with free time slots
    - Busiest days (least free time)
    - Best study days (most free time)
    """
    try:
        from app.services.free_time_analyzer import analyze_free_time

        # Get user's busy blocks
        db = get_supabase_client()
        blocks_data = db.get_busy_blocks(user_id)
        busy_blocks = [BusyBlock(**b) for b in blocks_data]

        if not busy_blocks:
            return {
                "message": "No calendar events found. Upload your calendar first.",
                "total_free_hours": 0,
                "days": []
            }

        # Analyze free time
        analysis = analyze_free_time(
            busy_blocks=busy_blocks,
            days_ahead=days_ahead,
            work_start_hour=9,
            work_end_hour=22,
            min_block_minutes=30
        )

        return analysis

    except Exception as e:
        raise HTTPException(500, f"Free time analysis failed: {str(e)}")
