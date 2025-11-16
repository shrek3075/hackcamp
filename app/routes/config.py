"""
Exam/Test and user configuration routes
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from dateutil import parser, tz

from app.models import ExamConfig, SemesterConfig
from app.clients.supabase import get_supabase_client

router = APIRouter(prefix="/config", tags=["configuration"])


# ===== EXAM/TEST CONFIGURATION (NEW) =====

@router.post("/exam", response_model=ExamConfig)
async def set_exam_config(config: ExamConfig):
    """
    Set configuration for a single exam/test

    Configure:
    - Exam name and date
    - Study depth level (basic/standard/comprehensive)
    - Available study hours per day
    - Task importance weights (% of grade)
    """
    try:
        # Validate exam date
        exam_date = parser.isoparse(config.exam_date)

        if config.start_prep_date:
            start_date = parser.isoparse(config.start_prep_date)
            if start_date >= exam_date:
                raise HTTPException(400, "Start prep date must be before exam date")

        if config.hours_per_day <= 0:
            raise HTTPException(400, "Hours per day must be positive")

        # Save to database (using semester config table for now)
        db = get_supabase_client()
        config_data = config.model_dump(exclude={"id", "created_at"})
        config_data["created_at"] = datetime.now(tz=tz.UTC).isoformat()

        # Store as JSON in semester config for simplicity
        existing = db.get_semester_config(config.user_id)

        if existing:
            db.update_semester_config(config.user_id, config_data)
        else:
            db.insert_semester_config(config_data)

        saved_config = db.get_semester_config(config.user_id)
        return ExamConfig(**saved_config)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to save exam config: {str(e)}")


@router.get("/exam/{user_id}", response_model=ExamConfig)
async def get_exam_config(user_id: str):
    """Get user's exam configuration"""
    try:
        db = get_supabase_client()
        config = db.get_semester_config(user_id)

        if not config:
            raise HTTPException(404, "Exam configuration not found. Please set up your exam first.")

        return ExamConfig(**config)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch exam config: {str(e)}")


@router.delete("/exam/{user_id}")
async def delete_exam_config(user_id: str):
    """Delete user's exam configuration"""
    try:
        db = get_supabase_client()
        db.delete_semester_config(user_id)

        return {"success": True, "message": "Exam configuration deleted"}

    except Exception as e:
        raise HTTPException(500, f"Failed to delete exam config: {str(e)}")


# ===== SEMESTER CONFIGURATION (DEPRECATED - kept for backwards compatibility) =====

@router.post("/semester", response_model=SemesterConfig)
async def set_semester_config(config: SemesterConfig):
    """
    Set or update user's semester configuration

    This defines the time boundaries for study plan generation.
    All timelines will be scheduled within these dates.
    """
    try:
        # Validate dates
        start = parser.isoparse(config.start_date)
        end = parser.isoparse(config.end_date)

        if end <= start:
            raise HTTPException(400, "End date must be after start date")

        if config.exam_period_start and config.exam_period_end:
            exam_start = parser.isoparse(config.exam_period_start)
            exam_end = parser.isoparse(config.exam_period_end)

            if exam_start < start or exam_end > end:
                raise HTTPException(400, "Exam period must be within semester dates")

        # Save to database
        db = get_supabase_client()
        config_data = config.model_dump(exclude={"id", "created_at"})
        config_data["created_at"] = datetime.now(tz=tz.UTC).isoformat()

        # Check if config exists for this user
        existing = db.get_semester_config(config.user_id)

        if existing:
            # Update existing
            db.update_semester_config(config.user_id, config_data)
        else:
            # Insert new
            db.insert_semester_config(config_data)

        # Return the saved config
        saved_config = db.get_semester_config(config.user_id)
        return SemesterConfig(**saved_config)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to save semester config: {str(e)}")


@router.get("/semester/{user_id}", response_model=SemesterConfig)
async def get_semester_config(user_id: str):
    """Get user's semester configuration"""
    try:
        db = get_supabase_client()
        config = db.get_semester_config(user_id)

        if not config:
            raise HTTPException(404, "Semester configuration not found. Please set up your semester first.")

        return SemesterConfig(**config)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch semester config: {str(e)}")


@router.delete("/semester/{user_id}")
async def delete_semester_config(user_id: str):
    """Delete user's semester configuration"""
    try:
        db = get_supabase_client()
        db.delete_semester_config(user_id)

        return {"success": True, "message": "Semester configuration deleted"}

    except Exception as e:
        raise HTTPException(500, f"Failed to delete semester config: {str(e)}")

