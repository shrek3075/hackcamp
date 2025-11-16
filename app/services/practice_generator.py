"""
AI practice question generator
"""
from typing import List, Dict, Any
from openai import OpenAI
import os


class PracticeGenerator:
    """Generate practice questions for study topics"""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"

    def generate_practice_questions(
        self,
        topic: str,
        difficulty: str = "medium",
        num_questions: int = 5,
        question_type: str = "mixed"
    ) -> Dict[str, Any]:
        """
        Generate practice questions for a topic

        Args:
            topic: The topic to generate questions about
            difficulty: easy, medium, or hard
            num_questions: Number of questions to generate
            question_type: multiple_choice, short_answer, or mixed

        Returns:
            Dict with questions list
        """
        system_prompt = f"""You are a helpful tutor creating practice questions.

Generate {num_questions} {difficulty} {question_type} questions about: {topic}

For multiple choice: provide 4 options (A, B, C, D) with one correct answer
For short answer: provide the expected answer

Return ONLY valid JSON:
{{
  "questions": [
    {{
      "question": "What is...",
      "type": "multiple_choice",
      "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
      "correct_answer": "B",
      "explanation": "..."
    }}
  ]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            raise Exception(f"Failed to generate practice questions: {str(e)}")

    def check_answer(
        self,
        question: str,
        student_answer: str,
        correct_answer: str
    ) -> Dict[str, Any]:
        """
        Check student's answer with AI feedback

        Args:
            question: The question asked
            student_answer: Student's response
            correct_answer: The correct answer

        Returns:
            Dict with is_correct, feedback, and explanation
        """
        system_prompt = """You are a supportive tutor checking answers.

Compare the student's answer to the correct answer. Be encouraging but honest.

Return ONLY valid JSON:
{
  "is_correct": true/false,
  "feedback": "Great job! / Not quite...",
  "explanation": "detailed explanation",
  "score": 0-100
}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Question: {question}\nCorrect answer: {correct_answer}\nStudent answer: {student_answer}"
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            return {
                "is_correct": False,
                "feedback": "Could not check answer",
                "explanation": str(e),
                "score": 0
            }


# Global instance
_practice_generator = None


def get_practice_generator() -> PracticeGenerator:
    """Get or create practice generator singleton"""
    global _practice_generator
    if _practice_generator is None:
        _practice_generator = PracticeGenerator()
    return _practice_generator
