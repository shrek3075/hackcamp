"""
AI-Powered Study Schedule Generator
Creates intelligent day-by-day study timeline using GPT-4o-mini
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dateutil import parser, tz

from app.models import StudyMaterial
from app.clients.ai_client import get_ai_client


def generate_study_schedule(
    study_materials: List[StudyMaterial],
    exam_date: str,
    current_date: Optional[str] = None,
    hours_per_day: float = 2.0,
    study_start_time: str = "17:00",
    study_end_time: str = "21:00",
    busy_blocks: List[Dict] = None
) -> Tuple[List[Dict], Dict, List[str]]:
    """
    Generate intelligent study schedule using AI

    Args:
        study_materials: List of study materials with topics
        exam_date: ISO format date of the exam (YYYY-MM-DD)
        current_date: Optional current date override (defaults to today)
        hours_per_day: Maximum hours per day to study
        study_start_time: Earliest study time (HH:MM format)
        study_end_time: Latest study time (HH:MM format)
        busy_blocks: Optional calendar busy blocks to avoid

    Returns:
        Tuple of (daily_schedule, metadata, warnings)
    """
    warnings = []

    # Parse dates
    if current_date:
        try:
            today = parser.isoparse(current_date).replace(hour=0, minute=0, second=0, microsecond=0)
        except:
            today = datetime.now(tz=tz.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
            warnings.append(f"Invalid current_date, using today: {today.date()}")
    else:
        today = datetime.now(tz=tz.UTC).replace(hour=0, minute=0, second=0, microsecond=0)

    try:
        exam_dt = parser.isoparse(exam_date).replace(hour=0, minute=0, second=0, microsecond=0)
    except:
        raise ValueError(f"Invalid exam_date format: {exam_date}. Use YYYY-MM-DD")

    # Calculate days until exam
    days_until_exam = (exam_dt.date() - today.date()).days

    if days_until_exam < 0:
        warnings.append("Exam date is in the past!")
        return [], {}, warnings

    if days_until_exam == 0:
        warnings.append("Exam is today!")
        return [], {}, warnings

    # Extract all topics for AI
    all_topics = []
    total_hours_needed = 0.0

    for material in study_materials:
        for topic in material.topics:
            all_topics.append({
                "name": topic.name,
                "source": material.source_file,
                "subtopics": topic.subtopics,
                "estimated_hours": topic.estimated_hours,
                "complexity": topic.complexity,
                "learning_objectives": topic.learning_objectives,
                "key_terms": [{"term": kt.term, "definition": kt.definition} for kt in topic.key_terms]
            })
            total_hours_needed += topic.estimated_hours

    if not all_topics:
        warnings.append("No topics found in study materials")
        return [], {}, warnings

    # Use AI to generate intelligent schedule
    print(f"Generating AI-powered schedule for {len(all_topics)} topics, {days_until_exam} days...")

    ai_client = get_ai_client()

    try:
        ai_result = ai_client.generate_smart_study_schedule(
            topics=all_topics,
            exam_date=exam_date,
            current_date=today.date().isoformat(),
            max_hours_per_day=hours_per_day,
            busy_blocks=busy_blocks
        )

        daily_schedule = ai_result.get("daily_schedule", [])

        # Enhance with session times
        for day in daily_schedule:
            day_date = parser.isoparse(day["date"])
            day["day_name"] = day_date.strftime("%A")
            day["day_number"] = (day_date.date() - today.date()).days + 1

            # Add session times
            start_hour, start_min = map(int, study_start_time.split(":"))
            session_start = day_date.replace(hour=start_hour, minute=start_min)
            session_end = session_start + timedelta(hours=day["total_hours"])

            day["session_start"] = session_start.strftime("%I:%M %p")
            day["session_end"] = session_end.strftime("%I:%M %p")
            day["is_review_day"] = day.get("is_review", False)

            # Add topic details
            for topic_schedule in day.get("topics", []):
                # Find original topic for details
                for orig_topic in all_topics:
                    if orig_topic["name"] == topic_schedule["topic_name"]:
                        topic_schedule["subtopics"] = orig_topic.get("subtopics", [])
                        topic_schedule["complexity"] = orig_topic.get("complexity", "intermediate")
                        topic_schedule["learning_objectives"] = orig_topic.get("learning_objectives", [])[:3]
                        topic_schedule["is_partial"] = False  # AI handles this
                        topic_schedule["source_file"] = orig_topic.get("source", "")
                        break

        # Build metadata
        total_scheduled_hours = sum(day["total_hours"] for day in daily_schedule)
        avg_hours = total_scheduled_hours / len(daily_schedule) if daily_schedule else 0

        metadata = {
            "exam_date": exam_date,
            "current_date": today.date().isoformat(),
            "days_until_exam": days_until_exam,
            "total_study_days": len(daily_schedule),
            "total_hours_needed": round(total_hours_needed, 1),
            "total_hours_scheduled": round(total_scheduled_hours, 1),
            "avg_hours_per_day": round(avg_hours, 1),
            "recommended_hours_per_day": round(total_hours_needed / max(1, days_until_exam - 1), 1),
            "user_specified_hours_per_day": hours_per_day,
            "total_topics": len(all_topics),
            "study_window": f"{study_start_time} - {study_end_time}"
        }

        print(f"AI generated schedule: {len(daily_schedule)} days, {total_scheduled_hours}h total")

        return daily_schedule, metadata, warnings

    except Exception as e:
        print(f"AI schedule generation failed: {e}")
        warnings.append(f"AI scheduling failed: {str(e)}")
        return [], {}, warnings


def format_schedule_summary(daily_schedule: List[Dict], metadata: Dict) -> str:
    """
    Create a human-readable text summary of the schedule

    Args:
        daily_schedule: Output from generate_study_schedule
        metadata: Metadata from generate_study_schedule

    Returns:
        Formatted text summary
    """
    lines = []
    lines.append("=" * 60)
    lines.append("📚 AI-POWERED STUDY SCHEDULE")
    lines.append("=" * 60)
    lines.append(f"Exam Date: {metadata['exam_date']}")
    lines.append(f"Days Until Exam: {metadata['days_until_exam']}")
    lines.append(f"Total Study Days: {metadata['total_study_days']}")
    lines.append(f"Total Hours: {metadata['total_hours_scheduled']}h")
    lines.append(f"Average Hours/Day: {metadata['avg_hours_per_day']}h")
    lines.append(f"Study Window: {metadata['study_window']}")
    lines.append("=" * 60)
    lines.append("")

    for day in daily_schedule:
        if day.get("is_review_day"):
            lines.append(f"📝 DAY {day['day_number']} - {day['day_name']} {day['date']} [REVIEW DAY]")
        else:
            lines.append(f"📅 DAY {day['day_number']} - {day['day_name']} {day['date']}")

        lines.append(f"   Time: {day['session_start']} - {day['session_end']} ({day['total_hours']}h)")
        lines.append("")

        for i, topic in enumerate(day.get("topics", []), 1):
            lines.append(f"   {i}. {topic['topic_name']} - {topic['hours']}h")
            if topic.get("rationale"):
                lines.append(f"      Why: {topic['rationale']}")

        lines.append("")
        lines.append("-" * 60)
        lines.append("")

    return "\n".join(lines)
