"""
Practice questions and AI tutor routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict

from app.services.practice_generator import get_practice_generator
from app.services.tutor import get_ai_tutor

router = APIRouter(prefix="/practice", tags=["practice"])


class PracticeRequest(BaseModel):
    topic: str
    difficulty: str = "medium"  # easy, medium, hard
    num_questions: int = 5
    question_type: str = "mixed"  # multiple_choice, short_answer, mixed


class AnswerCheckRequest(BaseModel):
    question: str
    student_answer: str
    correct_answer: str


class ExplainRequest(BaseModel):
    concept: str
    context: Optional[str] = None
    detail_level: str = "medium"  # simple, medium, detailed


class QuestionRequest(BaseModel):
    question: str
    context: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = None


@router.post("/generate")
async def generate_practice_questions(request: PracticeRequest):
    """
    Generate AI practice questions for a topic

    Args:
        topic: What to practice
        difficulty: easy, medium, or hard
        num_questions: How many questions (1-10)
        question_type: multiple_choice, short_answer, or mixed

    Returns:
        List of practice questions with answers
    """
    try:
        if request.num_questions < 1 or request.num_questions > 10:
            raise HTTPException(400, "num_questions must be between 1 and 10")

        generator = get_practice_generator()

        result = generator.generate_practice_questions(
            topic=request.topic,
            difficulty=request.difficulty,
            num_questions=request.num_questions,
            question_type=request.question_type
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to generate practice questions: {str(e)}")


@router.post("/check-answer")
async def check_answer(request: AnswerCheckRequest):
    """
    Check student's answer with AI feedback

    Returns:
    - is_correct: boolean
    - feedback: encouraging message
    - explanation: why answer is correct/incorrect
    - score: 0-100
    """
    try:
        generator = get_practice_generator()

        result = generator.check_answer(
            question=request.question,
            student_answer=request.student_answer,
            correct_answer=request.correct_answer
        )

        return result

    except Exception as e:
        raise HTTPException(500, f"Failed to check answer: {str(e)}")


@router.post("/explain")
async def explain_concept(request: ExplainRequest):
    """
    AI explains a concept

    Returns:
    - explanation: clear explanation
    - examples: practical examples
    - key_points: main takeaways
    - common_mistakes: what to avoid
    """
    try:
        tutor = get_ai_tutor()

        result = tutor.explain_concept(
            concept=request.concept,
            context=request.context,
            detail_level=request.detail_level
        )

        return result

    except Exception as e:
        raise HTTPException(500, f"Failed to generate explanation: {str(e)}")


@router.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    Ask the AI tutor a question

    Supports conversation history for context.

    Returns:
        Answer to the question
    """
    try:
        tutor = get_ai_tutor()

        answer = tutor.answer_question(
            question=request.question,
            context=request.context,
            conversation_history=request.conversation_history
        )

        return {"answer": answer}

    except Exception as e:
        raise HTTPException(500, f"Failed to answer question: {str(e)}")


@router.get("/resources/{topic}")
async def get_study_resources(topic: str, learning_style: str = "mixed"):
    """
    Get AI-suggested study resources and strategies

    Args:
        topic: What you're studying
        learning_style: visual, auditory, kinesthetic, or mixed

    Returns:
        Study strategies, resources, and practice tips
    """
    try:
        tutor = get_ai_tutor()

        result = tutor.suggest_study_resources(
            topic=topic,
            learning_style=learning_style
        )

        return result

    except Exception as e:
        raise HTTPException(500, f"Failed to get resources: {str(e)}")
