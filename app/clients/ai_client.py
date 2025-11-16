"""
OpenAI GPT-4o-mini client with vision capabilities
"""
import os
import json
import base64
from typing import Dict, Any, List, Optional
from openai import OpenAI


class AIClient:
    """Wrapper for OpenAI API calls with GPT-4o-mini"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"  # Vision-capable, cheap, fast

    def extract_syllabus_tasks(
        self,
        syllabus_text: str = None,
        image_base64: str = None,
        pdf_images: List[str] = None
    ) -> Dict[str, Any]:
        """
        Extract tasks from syllabus using vision or text

        Args:
            syllabus_text: Raw text (if available)
            image_base64: Base64 encoded image
            pdf_images: List of base64 encoded images from PDF pages

        Returns:
            Dict with 'tasks' key containing extracted tasks
        """
        system_prompt = """You are an expert syllabus analyzer. Extract ALL assignments, exams, projects, quizzes, and readings with their details.

Return ONLY valid JSON (no markdown, no explanations):
{
  "tasks": [
    {
      "title": "Assignment 1: Intro to Python",
      "due": "2024-02-15",
      "type": "assignment",
      "weight": 15.0,
      "notes": "Cover chapters 1-3"
    }
  ]
}

Rules:
- Use ISO date format (YYYY-MM-DD)
- If date is unclear, use null
- type must be: assignment, exam, project, quiz, reading, or other
- weight is percentage (15.0 = 15%), use null if not specified
- Extract EVERYTHING - don't miss any tasks"""

        messages = [{"role": "system", "content": system_prompt}]

        # Build user message with vision if available
        if pdf_images and len(pdf_images) > 0:
            # Multi-page PDF
            content = [{"type": "text", "text": "Extract all tasks from this syllabus (multiple pages):"}]
            for img_b64 in pdf_images[:10]:  # Limit to 10 pages to save tokens
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{img_b64}"}
                })
            messages.append({"role": "user", "content": content})

        elif image_base64:
            # Single image
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract all tasks from this syllabus:"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_base64}"}
                    }
                ]
            })

        elif syllabus_text:
            # Text only
            messages.append({
                "role": "user",
                "content": f"Extract all tasks from this syllabus:\n\n{syllabus_text}"
            })

        else:
            raise ValueError("Must provide either text, image, or PDF")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.0,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except json.JSONDecodeError as e:
            raise ValueError(f"AI returned invalid JSON: {e}")
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def estimate_effort(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate effort hours using AI"""
        system_prompt = """You are an academic workload estimator. Estimate realistic study hours needed.

Consider:
- Assignment complexity (based on title/description)
- Course level (intro vs advanced)
- Task type and weight
- Typical student workload

Return ONLY valid JSON:
{"estimates": [{"title": "...", "effort_hours": 4.5}]}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Estimate effort for these tasks:\n{json.dumps(tasks, indent=2)}"}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def analyze_calendar_event(self, event_title: str, event_description: str = "") -> Dict[str, str]:
        """Use AI to categorize calendar events (no keyword matching!)"""
        system_prompt = """Categorize this calendar event intelligently.

Categories:
- class: Lectures, labs, tutorials, office hours
- work: Job shifts, meetings, work commitments
- personal: Gym, meals, appointments, social events
- study: Study groups, library time, homework sessions
- other: Anything else

Return ONLY valid JSON:
{"category": "class", "confidence": "high", "reasoning": "..."}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Title: {event_title}\nDescription: {event_description or 'N/A'}"}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            return {"category": "other", "confidence": "low", "reasoning": "AI categorization failed"}

    def generate_study_coach_message(
        self,
        student_name: str,
        progress_data: Dict[str, Any],
        upcoming_tasks: List[Dict],
        streak_days: int
    ) -> str:
        """Generate Duolingo-style motivational coaching message"""
        system_prompt = f"""You are a supportive, energetic study coach like Duolingo's owl.

Be:
- Encouraging but not cheesy
- Specific about their progress
- Actionable with next steps
- Motivating about streaks
- Brief (2-3 sentences max)

Student: {student_name}
Streak: {streak_days} days
Recent progress: {json.dumps(progress_data)}
Upcoming: {json.dumps(upcoming_tasks[:3])}

Generate a personalized motivational message."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}],
                temperature=0.7,
                max_tokens=150
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Great work, {student_name}! You're on a {streak_days}-day streak. Keep it up!"

    def create_study_timeline(
        self,
        task: Dict[str, Any],
        current_date: str,
        busy_blocks: List[Dict]
    ) -> Dict[str, Any]:
        """AI-powered timeline generator for test/project prep"""
        system_prompt = """You are a study planning expert. Create a detailed prep timeline.

Break down preparation into milestones with best practices (spaced repetition, active recall).

Return valid JSON:
{
  "timeline": [
    {
      "phase": "Review Fundamentals",
      "days_before_due": 7,
      "tasks": ["Review lecture notes", "Summarize key concepts"],
      "estimated_hours": 4
    }
  ],
  "total_prep_hours": 20,
  "difficulty": "medium",
  "tips": ["Start early", "Focus on practice problems"]
}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Create timeline for:\nTask: {json.dumps(task)}\nToday: {current_date}\nBusy blocks: {json.dumps(busy_blocks[:10])}"
                    }
                ],
                temperature=0.4,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            raise Exception(f"Timeline generation failed: {str(e)}")


# Global singleton
_ai_client: Optional[AIClient] = None


def get_ai_client() -> AIClient:
    """Get or create AI client singleton"""
    global _ai_client
    if _ai_client is None:
        _ai_client = AIClient()
    return _ai_client
