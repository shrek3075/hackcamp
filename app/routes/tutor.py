"""
Study Tutor/Coach routes - Teaching-focused AI chat
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.clients.ai_client import get_ai_client

router = APIRouter(prefix="/tutor", tags=["tutor"])


# New models for simpler chat interface
class ChatMessage(BaseModel):
    role: str
    content: str


class NoteData(BaseModel):
    id: str
    subject: str
    title: str
    content: str


class SimpleTutorRequest(BaseModel):
    messages: List[ChatMessage]
    notes: Optional[List[NoteData]] = []
    planData: Optional[Dict[str, Any]] = None


class SimpleTutorResponse(BaseModel):
    response: str

# In-memory storage for study materials (temporary - should use database)
_user_materials = {}


# OLD ENDPOINT - COMMENTED OUT (uses undefined models)
# @router.post("/chat", response_model=TutorChatResponse)
# async def chat_with_tutor(request: TutorChatRequest):
#     """
#     Chat with AI tutor that knows all your study materials
#
#     Like NotebookLM - the AI has full context of all uploaded documents
#     and can teach concepts, answer questions, and provide explanations.
#
#     Features:
#     - Understands all uploaded study materials
#     - Teaching-focused explanations
#     - References specific topics and terms
#     - Suggests follow-up questions
#     - Maintains conversation context
#     """
#     try:
#         from app.clients.supabase import get_supabase_client
#
#         # Get user's study materials from DATABASE
#         db = get_supabase_client()
#         materials_data = db.get_study_materials(request.user_id)
#
#         # Convert to StudyMaterial objects
#         materials = [StudyMaterial(**m) if isinstance(m, dict) else m for m in materials_data]
#
#         if not materials:
#             return TutorChatResponse(
#                 message="I don't have any study materials loaded for you yet. Upload your notes, slides, or textbook chapters, and I'll help you master the content!",
#                 referenced_topics=[],
#                 suggested_followups=["How do I upload materials?"]
#             )
#
#         # Convert StudyMaterial objects to dict format for AI
#         materials_dict = []
#         for mat in materials:
#             if isinstance(mat, StudyMaterial):
#                 materials_dict.append(mat.model_dump())
#             else:
#                 materials_dict.append(mat)
#
#         # Get AI tutor response
#         ai_client = get_ai_client()
#
#         # Convert conversation history to dict format
#         history = [msg.model_dump() if hasattr(msg, 'model_dump') else msg
#                    for msg in request.conversation_history]
#
#         result = ai_client.teach_with_context(
#             user_question=request.message,
#             study_materials=materials_dict,
#             conversation_history=history
#         )
#
#         return TutorChatResponse(
#             message=result["message"],
#             referenced_topics=result["referenced_topics"],
#             suggested_followups=result["suggested_followups"]
#         )
#
#     except Exception as e:
#         raise HTTPException(500, f"Tutor chat failed: {str(e)}")


# OLD ENDPOINTS - COMMENTED OUT (use undefined models)
# @router.post("/load-materials")
# async def load_study_materials(user_id: str, materials: List[StudyMaterial]):
#     """
#     Load study materials for a user (temporary in-memory storage)
#
#     In production, materials would be stored in database after upload
#     and fetched automatically during chat.
#     """
#     try:
#         _user_materials[user_id] = materials
#         return {
#             "success": True,
#             "materials_loaded": len(materials),
#             "message": f"Loaded {len(materials)} study materials. Ready to help you learn!"
#         }
#     except Exception as e:
#         raise HTTPException(500, f"Failed to load materials: {str(e)}")
#
#
# @router.get("/materials/{user_id}")
# async def get_user_materials(user_id: str):
#     """Get loaded study materials for a user"""
#     materials = _user_materials.get(user_id, [])
#     return {
#         "user_id": user_id,
#         "materials_count": len(materials),
#         "materials": materials
#     }


@router.post("/simple-chat", response_model=SimpleTutorResponse)
async def simple_chat(request: SimpleTutorRequest):
    """
    Simple chat endpoint for frontend integration
    Accepts messages, notes, and plan data for context
    """
    try:
        client = get_ai_client()

        # Build context from selected notes
        notes_context = ""
        if request.notes and len(request.notes) > 0:
            notes_context = "\n\nYou have access to the following study notes. Use these notes as reference to answer questions:\n\n"
            for idx, note in enumerate(request.notes):
                notes_context += f"--- Note {idx + 1}: {note.title} ({note.subject}) ---\n{note.content}\n\n"
            notes_context += "\nIMPORTANT: Use the information from these notes to help the student. If the question relates to topics in the notes, reference them in your answer."

        # Build context from study plan if provided
        plan_context = ""
        if request.planData:
            plan_context = "\n\nThe student is currently working on the following study plan:\n\n"
            plan_context += f"Subject: {request.planData.get('subject', 'Not specified')}\n"
            plan_context += f"Topic: {request.planData.get('topic', 'Not specified')}\n"
            plan_context += f"Test Date: {request.planData.get('test_date', 'Not specified')}\n"

            plan_data = request.planData.get('plan_data')
            if plan_data and isinstance(plan_data, dict):
                daily_plans = plan_data.get('dailyPlans', [])
                if daily_plans:
                    plan_context += "\nStudy Timeline:\n"
                    # Show first 5 days
                    for day in daily_plans[:5]:
                        sessions = day.get('sessions', [])
                        topics = [s.get('topic', '') for s in sessions]
                        plan_context += f"- Day {day.get('day', '?')} ({day.get('date', '?')}): {', '.join(topics) if topics else 'No sessions'}\n"

            plan_context += "\nUse this study plan context when helping the student with their learning."

        # Create system message for the tutor
        system_message = {
            "role": "system",
            "content": f"""You are a helpful and patient AI study tutor. Your role is to:
- Help students understand concepts clearly based on their study materials
- Break down complex topics into simple explanations
- Provide step-by-step guidance for problem-solving
- Encourage critical thinking rather than just giving answers
- Be supportive and encouraging
- Use examples and analogies to make concepts relatable
- Check for understanding and adjust your explanations accordingly
- When notes or study plans are provided, use them as context for your answers

{notes_context}{plan_context}

Always be patient, clear, and encouraging. If a student is struggling, break things down further.{' Use the provided study materials and plan to give contextual, relevant help.' if (request.notes and len(request.notes) > 0) or request.planData else ''}"""
        }

        # Convert messages to OpenAI format
        messages = [system_message] + [{"role": msg.role, "content": msg.content} for msg in request.messages]

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        ai_response = response.choices[0].message.content

        return SimpleTutorResponse(response=ai_response)

    except Exception as e:
        print(f"Error in simple chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get AI response: {str(e)}")
