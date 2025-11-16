"""
Syllabus upload and extraction routes
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import base64

from app.models import SyllabusIngestResponse, Task
from app.services.syllabus_extractor import extract_tasks_from_syllabus
from app.services.effort_estimator import apply_effort_estimates
from app.clients.supabase import get_supabase_client

router = APIRouter(prefix="/syllabus", tags=["syllabus"])


@router.post("/upload", response_model=SyllabusIngestResponse)
async def upload_syllabus(
    user_id: str = Form(...),
    file: Optional[UploadFile] = File(None),
    syllabus_text: Optional[str] = Form(None),
    course_name: Optional[str] = Form(None)
):
    """
    Upload and extract tasks from syllabus (PDF, image, or text)

    Supports:
    - PDF files (vision-based extraction)
    - Images (JPG, PNG, etc.)
    - Plain text

    Returns extracted tasks with AI-estimated effort hours
    """
    if not file and not syllabus_text:
        raise HTTPException(400, "Must provide either file or syllabus_text")

    try:
        # Process file if provided
        file_content = None
        filename = ""

        if file:
            content_bytes = await file.read()
            file_content = base64.b64encode(content_bytes).decode('utf-8')
            filename = file.filename

        # Extract tasks
        tasks, warnings = extract_tasks_from_syllabus(
            syllabus_text=syllabus_text,
            file_content=file_content,
            filename=filename,
            user_id=user_id
        )

        # Estimate effort for each task
        tasks = apply_effort_estimates(tasks)

        # Save to database
        db = get_supabase_client()
        tasks_data = [task.model_dump(exclude={"id"}) for task in tasks]

        saved_tasks = db.insert_tasks(tasks_data)

        # Convert back to Task objects with IDs
        final_tasks = [Task(**task_dict) for task_dict in saved_tasks]

        return SyllabusIngestResponse(
            success=True,
            tasks_extracted=len(final_tasks),
            tasks=final_tasks,
            warnings=warnings
        )

    except Exception as e:
        raise HTTPException(500, f"Syllabus extraction failed: {str(e)}")


@router.get("/tasks/{user_id}")
async def get_user_tasks(user_id: str, completed: Optional[bool] = None):
    """Get all tasks for a user"""
    try:
        db = get_supabase_client()
        tasks = db.get_tasks(user_id, completed=completed)
        return {"tasks": tasks}
    except Exception as e:
        raise HTTPException(500, f"Failed to fetch tasks: {str(e)}")
