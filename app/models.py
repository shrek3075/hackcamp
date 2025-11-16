"""
Pydantic models for SmartPlanner API
"""
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


# ===== TASK MODELS =====

class Task(BaseModel):
    """Represents a single academic task"""
    id: Optional[str] = None
    user_id: Optional[str] = None
    title: str
    due_date: Optional[str] = None  # ISO format or null if ambiguous
    task_type: Literal["assignment", "exam", "project", "quiz", "reading", "other"] = "other"
    weight: Optional[float] = None  # e.g., 15.0 for 15%
    notes: Optional[str] = None
    effort_hours: Optional[float] = None  # Estimated hours needed
    completed: bool = False
    created_at: Optional[datetime] = None


class TaskCreate(BaseModel):
    """Request to create a task"""
    title: str
    due_date: Optional[str] = None
    task_type: str = "other"
    weight: Optional[float] = None
    notes: Optional[str] = None


# ===== SYLLABUS INGESTION =====

class SyllabusIngestRequest(BaseModel):
    """Request to ingest a syllabus"""
    user_id: str
    syllabus_text: Optional[str] = None  # Direct text input
    file_content: Optional[str] = None  # Base64 encoded PDF or text file
    course_name: Optional[str] = None


class SyllabusIngestResponse(BaseModel):
    """Response after syllabus ingestion"""
    success: bool
    tasks_extracted: int
    tasks: List[Task]
    warnings: List[str] = []


# ===== CALENDAR / BUSY BLOCKS =====

class BusyBlock(BaseModel):
    """Represents a time block when user is busy"""
    id: Optional[str] = None
    user_id: Optional[str] = None
    title: str
    start: str  # ISO datetime
    end: str    # ISO datetime
    block_type: Literal["class", "work", "personal", "other"] = "other"
    created_at: Optional[datetime] = None


class CalendarIngestRequest(BaseModel):
    """Request to ingest calendar"""
    user_id: str
    ics_content: Optional[str] = None  # .ics file content
    google_calendar_id: Optional[str] = None  # For OAuth flow (future)


class CalendarIngestResponse(BaseModel):
    """Response after calendar ingestion"""
    success: bool
    blocks_extracted: int
    busy_blocks: List[BusyBlock]


# ===== USER PREFERENCES =====

class UserPreferences(BaseModel):
    """User study preferences"""
    max_hours_per_day: float = 6.0
    preferred_start_time: str = "09:00"  # HH:MM format
    preferred_end_time: str = "22:00"
    break_duration_minutes: int = 15
    min_study_block_minutes: int = 30
    days_to_plan: int = 10  # How many days ahead to plan


# ===== SCHEDULE GENERATION =====

class ScheduleBlock(BaseModel):
    """A single study block in the schedule"""
    task_id: Optional[str] = None
    task_title: str
    start: str  # ISO datetime
    end: str    # ISO datetime
    duration_hours: float
    reason: Optional[str] = None  # Why this was scheduled here


class PlanGenerateRequest(BaseModel):
    """Request to generate a study plan"""
    user_id: str
    preferences: Optional[UserPreferences] = UserPreferences()
    force_regenerate: bool = False


class PlanGenerateResponse(BaseModel):
    """Response with generated plan"""
    plan_id: str
    user_id: str
    generated_at: datetime
    blocks: List[ScheduleBlock]
    total_hours: float
    warnings: List[str] = []


# ===== PLAN FEEDBACK =====

class PlanFeedback(BaseModel):
    """User feedback to adjust plan"""
    action: Literal["block_time", "mark_complete", "adjust_effort", "reschedule"]
    task_id: Optional[str] = None
    blocked_start: Optional[str] = None  # For block_time action
    blocked_end: Optional[str] = None
    new_effort_hours: Optional[float] = None  # For adjust_effort


class PlanFeedbackRequest(BaseModel):
    """Request to update plan based on feedback"""
    user_id: str
    feedback: PlanFeedback


# ===== STORED PLAN =====

class Plan(BaseModel):
    """A complete study plan"""
    id: str
    user_id: str
    generated_at: datetime
    blocks: List[ScheduleBlock]
    version: int = 1


# ===== HEALTH CHECK =====

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    timestamp: datetime
    services: dict = Field(default_factory=dict)
