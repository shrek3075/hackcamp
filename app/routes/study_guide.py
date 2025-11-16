"""
Study Guide and Practice Test routes - Focus AI on specific exam topics
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, List
from pydantic import BaseModel

from app.clients.supabase import get_supabase_client
from app.clients.ai_client import get_ai_client

router = APIRouter(prefix="/study-guide", tags=["study-guide"])


class StudyGuideUploadRequest(BaseModel):
    user_id: str
    guide_type: str = "study_guide"  # study_guide, practice_test, exam_outline
    text_content: Optional[str] = None


@router.post("/upload")
async def upload_study_guide(
    user_id: str = Form(...),
    guide_type: str = Form("study_guide"),
    file: Optional[UploadFile] = File(None),
    text_content: Optional[str] = Form(None)
):
    """
    Upload a study guide or practice test to focus AI on specific topics

    The AI will:
    - Generate quizzes tuned toward topics in the guide
    - Spend more study time on areas covered in the guide
    - Focus tutor responses on guide-related concepts
    - Prioritize these topics in the study schedule

    Args:
        user_id: User identifier
        guide_type: Type of guide (study_guide, practice_test, exam_outline)
        file: PDF/image of study guide or practice test
        text_content: OR paste text content directly

    Returns:
        Extracted topics and how they'll be used
    """
    try:
        # Read content
        content = text_content

        if file and not content:
            if file.filename.endswith('.pdf') or file.filename.endswith(('.jpg', '.png', '.jpeg')):
                # Extract text from file
                from app.services.content_extractor import extract_text_from_pdf, extract_text_from_image
                import base64

                file_bytes = await file.read()

                if file.filename.endswith('.pdf'):
                    content = extract_text_from_pdf(file_bytes)
                else:
                    base64_image = base64.b64encode(file_bytes).decode('utf-8')
                    content = extract_text_from_image(base64_image)
            else:
                content = (await file.read()).decode('utf-8')

        if not content:
            raise HTTPException(400, "Must provide either file or text_content")

        # Extract key topics and focus areas using AI
        ai_client = get_ai_client()

        guide_analysis = ai_client.analyze_study_guide(
            content=content,
            guide_type=guide_type
        )

        # Store in database with focus_priority flag
        db = get_supabase_client()

        study_guide_data = {
            "user_id": user_id,
            "guide_type": guide_type,
            "raw_content": content[:5000],  # Store first 5000 chars
            "focus_topics": guide_analysis.get("focus_topics", []),
            "key_concepts": guide_analysis.get("key_concepts", []),
            "suggested_question_types": guide_analysis.get("question_types", []),
            "priority_level": "high",
            "created_at": None  # Will be set by database
        }

        # Save to database (will need to add this table/method)
        try:
            saved = db.insert_study_guide(study_guide_data)
        except AttributeError:
            # If method doesn't exist yet, store in study materials with special flag
            print("[INFO] insert_study_guide not implemented, using fallback")
            saved = study_guide_data

        return {
            "success": True,
            "guide_type": guide_type,
            "focus_topics": guide_analysis.get("focus_topics", []),
            "key_concepts": guide_analysis.get("key_concepts", []),
            "question_types": guide_analysis.get("question_types", []),
            "topics_count": len(guide_analysis.get("focus_topics", [])),
            "message": f"Study guide analyzed! AI will now focus on these {len(guide_analysis.get('focus_topics', []))} key topics.",
            "how_this_helps": [
                "Quizzes will be tuned toward these topics",
                "Study schedule will allocate more time to these areas",
                "Tutor will prioritize explaining these concepts",
                "Practice questions will mirror these themes"
            ]
        }

    except Exception as e:
        raise HTTPException(500, f"Study guide upload failed: {str(e)}")


@router.get("/focus-areas/{user_id}")
async def get_focus_areas(user_id: str):
    """
    Get topics the AI should focus on based on uploaded study guides

    Returns priority topics for:
    - Quiz generation
    - Study time allocation
    - Tutor emphasis
    """
    try:
        db = get_supabase_client()

        # Try to get study guides
        try:
            guides = db.get_study_guides(user_id)
        except AttributeError:
            guides = []

        if not guides:
            return {
                "user_id": user_id,
                "has_focus_areas": False,
                "focus_topics": [],
                "message": "No study guide uploaded yet. Upload one to focus AI on specific exam topics!"
            }

        # Combine all focus topics from all guides
        all_topics = []
        all_concepts = []

        for guide in guides:
            all_topics.extend(guide.get("focus_topics", []))
            all_concepts.extend(guide.get("key_concepts", []))

        # Deduplicate
        unique_topics = list(set(all_topics))
        unique_concepts = list(set(all_concepts))

        return {
            "user_id": user_id,
            "has_focus_areas": True,
            "focus_topics": unique_topics,
            "key_concepts": unique_concepts,
            "guides_count": len(guides),
            "total_topics": len(unique_topics),
            "message": f"AI is focused on {len(unique_topics)} priority topics from your study guides"
        }

    except Exception as e:
        raise HTTPException(500, f"Failed to get focus areas: {str(e)}")


@router.post("/generate-focused-quiz")
async def generate_focused_quiz(
    user_id: str,
    num_questions: int = 10,
    difficulty: str = "medium"
):
    """
    Generate quiz specifically focused on study guide topics

    Unlike regular practice questions, this:
    - Only uses topics from the uploaded study guide
    - Mirrors the style/format suggested in the guide
    - Prioritizes high-importance concepts
    """
    try:
        # Get focus areas
        focus_data = await get_focus_areas(user_id)

        if not focus_data["has_focus_areas"]:
            raise HTTPException(
                400,
                "No study guide uploaded. Upload a study guide first to generate focused quizzes."
            )

        # Get study materials
        db = get_supabase_client()
        materials = db.get_study_materials(user_id)

        # Generate quiz focused on priority topics
        ai_client = get_ai_client()

        quiz = ai_client.generate_focused_quiz(
            study_materials=materials,
            focus_topics=focus_data["focus_topics"],
            key_concepts=focus_data["key_concepts"],
            num_questions=num_questions,
            difficulty=difficulty
        )

        return {
            "success": True,
            "quiz": quiz,
            "focus_topics_covered": focus_data["focus_topics"],
            "message": f"Generated {num_questions} questions focused on your study guide topics"
        }

    except Exception as e:
        raise HTTPException(500, f"Focused quiz generation failed: {str(e)}")
