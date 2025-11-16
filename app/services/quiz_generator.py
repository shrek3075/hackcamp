"""
Assessment Quiz Generator Service

Generates diagnostic quizzes to assess student's current knowledge level
before creating study plans.
"""
from typing import List
from app.models import StudyMaterial, QuizQuestion, KnowledgeAssessment
from app.clients.ai_client import get_ai_client


def generate_knowledge_assessment(
    study_materials: List[StudyMaterial],
    user_id: str,
    questions_per_topic: int = 3
) -> KnowledgeAssessment:
    """
    Generate diagnostic quiz to assess student's current knowledge

    Args:
        study_materials: List of extracted study materials
        user_id: User ID
        questions_per_topic: Number of questions per topic (default: 3)

    Returns:
        KnowledgeAssessment with quiz questions
    """
    # Collect all topics from all materials
    all_topics = []
    for material in study_materials:
        for topic in material.topics:
            all_topics.append({
                "name": topic.name,
                "subtopics": topic.subtopics,
                "complexity": topic.complexity,
                "learning_objectives": topic.learning_objectives,
                "key_terms": [
                    {"term": kt.term, "definition": kt.definition, "importance": kt.importance}
                    for kt in topic.key_terms
                ]
            })

    if not all_topics:
        # Return empty assessment if no topics
        return KnowledgeAssessment(
            user_id=user_id,
            questions=[],
            results=None,
            overall_score=None
        )

    # Use AI to generate quiz questions
    ai_client = get_ai_client()

    try:
        quiz_data = ai_client.generate_diagnostic_quiz(
            topics=all_topics,
            questions_per_topic=questions_per_topic
        )
    except Exception as e:
        raise Exception(f"Quiz generation failed: {str(e)}")

    # Parse into QuizQuestion objects
    questions = []
    for q_data in quiz_data.get("questions", []):
        question = QuizQuestion(
            topic=q_data.get("topic", "General"),
            question=q_data["question"],
            options=q_data["options"],
            correct_answer=q_data["correct_answer"],
            explanation=q_data.get("explanation")
        )
        questions.append(question)

    # Create assessment
    assessment = KnowledgeAssessment(
        user_id=user_id,
        questions=questions,
        results=None,  # Will be filled when student completes quiz
        overall_score=None
    )

    return assessment


def evaluate_quiz_results(
    assessment: KnowledgeAssessment,
    student_answers: dict  # {question_index: selected_answer}
) -> KnowledgeAssessment:
    """
    Evaluate student's quiz answers and update assessment with results

    Args:
        assessment: Original KnowledgeAssessment
        student_answers: Dict mapping question index to selected answer (e.g., "A", "B", "C", "D")

    Returns:
        Updated KnowledgeAssessment with results and score
    """
    from app.models import AssessmentResult
    from collections import defaultdict

    # Track results by topic
    topic_stats = defaultdict(lambda: {"asked": 0, "correct": 0, "questions": []})

    for idx, question in enumerate(assessment.questions):
        topic_stats[question.topic]["asked"] += 1
        topic_stats[question.topic]["questions"].append(question.question)

        # Check if answer is correct
        student_answer = student_answers.get(idx)
        if student_answer == question.correct_answer:
            topic_stats[question.topic]["correct"] += 1

    # Build AssessmentResult objects
    results = []
    total_correct = 0
    total_asked = 0

    for topic, stats in topic_stats.items():
        correct = stats["correct"]
        asked = stats["asked"]
        total_correct += correct
        total_asked += asked

        percentage = (correct / asked * 100) if asked > 0 else 0

        # Determine strengths and weaknesses
        strengths = []
        weaknesses = []

        if percentage >= 80:
            strengths.append(f"Strong understanding of {topic}")
        elif percentage >= 60:
            strengths.append(f"Moderate understanding of {topic}")
        else:
            weaknesses.append(f"Needs review: {topic}")

        result = AssessmentResult(
            topic=topic,
            questions_asked=asked,
            correct_answers=correct,
            knowledge_percentage=round(percentage, 1),
            strengths=strengths,
            weaknesses=weaknesses
        )
        results.append(result)

    # Calculate overall score
    overall_score = (total_correct / total_asked * 100) if total_asked > 0 else 0

    # Update assessment
    assessment.results = results
    assessment.overall_score = round(overall_score, 1)

    return assessment
