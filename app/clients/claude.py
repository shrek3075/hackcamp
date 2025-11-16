"""
Claude API client for AI-powered text extraction and analysis
"""
import os
import json
from typing import Dict, Any, List
from anthropic import Anthropic


class ClaudeClient:
    """Wrapper for Claude API calls"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"  # Latest model

    def extract_syllabus_tasks(self, syllabus_text: str) -> Dict[str, Any]:
        """
        Extract tasks from syllabus using Claude

        Args:
            syllabus_text: Raw syllabus content

        Returns:
            Dict with 'tasks' key containing list of extracted tasks
        """
        prompt = f"""You are a syllabus parser. Extract all assignments, exams, projects, quizzes, and readings with due dates and weights.

Return ONLY valid JSON in this exact format (no markdown, no explanations):
{{"tasks":[{{"title":"Assignment 1","due":"2024-02-15","type":"assignment","weight":15.0,"notes":"Chapter 1-3"}},{{"title":"Midterm Exam","due":"2024-03-10","type":"exam","weight":30.0,"notes":null}}]}}

Rules:
- Use ISO date format (YYYY-MM-DD) for due dates
- If a date is ambiguous or missing, use null
- type must be one of: assignment, exam, project, quiz, reading, other
- weight is percentage (e.g., 15.0 for 15%), use null if not specified
- Extract ALL tasks mentioned in the syllabus

Syllabus content:
{syllabus_text}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.0,  # Deterministic for structured output
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract text from response
            response_text = response.content[0].text.strip()

            # Parse JSON response
            result = json.loads(response_text)

            return result

        except json.JSONDecodeError as e:
            # Fallback: try to extract JSON from markdown blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
                result = json.loads(json_text)
                return result
            else:
                raise ValueError(f"Claude returned invalid JSON: {e}")

        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")

    def estimate_effort(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Estimate effort hours for a list of tasks

        Args:
            tasks: List of task dictionaries

        Returns:
            Dict with 'estimates' key containing effort hours per task
        """
        tasks_json = json.dumps(tasks, indent=2)

        prompt = f"""You estimate effort hours for academic tasks.

Typical ranges:
- reading: 0.5–2h (depending on page count/difficulty)
- assignment: 2–6h (depending on complexity)
- project: 6–20h (depending on scope)
- exam prep: 4–12h (depending on weight/coverage)
- quiz: 1–3h

Return ONLY valid JSON in this exact format (no markdown):
{{"estimates":[{{"title":"Assignment 1","effort_hours":4.0}},{{"title":"Midterm Exam","effort_hours":8.0}}]}}

Tasks to estimate:
{tasks_json}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = response.content[0].text.strip()
            result = json.loads(response_text)
            return result

        except json.JSONDecodeError:
            # Fallback
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
                result = json.loads(json_text)
                return result
            else:
                raise ValueError("Claude returned invalid JSON for effort estimation")

        except Exception as e:
            raise Exception(f"Claude API error in effort estimation: {str(e)}")

    def suggest_schedule(self, tasks: List[Dict], busy_blocks: List[Dict], preferences: Dict) -> Dict[str, Any]:
        """
        Use Claude to suggest optimal schedule (optional - can use heuristic instead)

        Args:
            tasks: List of tasks with effort hours
            busy_blocks: List of busy time blocks
            preferences: User scheduling preferences

        Returns:
            Dict with suggested schedule blocks
        """
        context = f"""Tasks to schedule:
{json.dumps(tasks, indent=2)}

Busy blocks (unavailable times):
{json.dumps(busy_blocks, indent=2)}

User preferences:
{json.dumps(preferences, indent=2)}"""

        prompt = f"""You are a study schedule optimizer. Create a daily study plan for the next {preferences.get('days_to_plan', 10)} days.

Rules:
- Respect all busy blocks (don't schedule during these times)
- Prioritize tasks due soon
- Don't exceed max_hours_per_day: {preferences.get('max_hours_per_day', 6)}
- Schedule within preferred hours: {preferences.get('preferred_start_time', '09:00')} - {preferences.get('preferred_end_time', '22:00')}
- Add breaks between study blocks
- Allocate more time to higher-weight tasks

Return ONLY valid JSON:
{{"blocks":[{{"task":"Assignment 1","start":"2024-02-01T10:00:00","end":"2024-02-01T12:00:00","reason":"Due in 5 days, high priority"}}]}}

{context}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.5,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = response.content[0].text.strip()
            result = json.loads(response_text)
            return result

        except Exception as e:
            raise Exception(f"Claude API error in schedule suggestion: {str(e)}")


# Global instance (lazy initialization)
_claude_client: ClaudeClient = None


def get_claude_client() -> ClaudeClient:
    """Get or create Claude client singleton"""
    global _claude_client
    if _claude_client is None:
        _claude_client = ClaudeClient()
    return _claude_client
