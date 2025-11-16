"""
AI tutor service - explains concepts and answers questions
"""
from typing import Dict, Any, List
from openai import OpenAI
import os


class AITutor:
    """AI tutor for explaining concepts"""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"

    def explain_concept(
        self,
        concept: str,
        context: str = None,
        detail_level: str = "medium"
    ) -> Dict[str, str]:
        """
        Explain a concept to the student

        Args:
            concept: The concept to explain
            context: Additional context (course, related topics)
            detail_level: simple, medium, or detailed

        Returns:
            Dict with explanation, examples, and key_points
        """
        detail_mapping = {
            "simple": "Explain in simple terms, like to a beginner",
            "medium": "Explain with moderate detail and examples",
            "detailed": "Provide a comprehensive explanation with examples and edge cases"
        }

        detail_instruction = detail_mapping.get(detail_level, detail_mapping["medium"])

        system_prompt = f"""You are a patient, helpful tutor. {detail_instruction}.

Return ONLY valid JSON:
{{
  "explanation": "clear explanation",
  "examples": ["example 1", "example 2"],
  "key_points": ["point 1", "point 2"],
  "common_mistakes": ["mistake 1", "mistake 2"]
}}"""

        context_str = f"\nContext: {context}" if context else ""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Explain: {concept}{context_str}"}
                ],
                temperature=0.5,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            return {
                "explanation": f"Error generating explanation: {str(e)}",
                "examples": [],
                "key_points": [],
                "common_mistakes": []
            }

    def answer_question(
        self,
        question: str,
        context: str = None,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Answer a student's question

        Args:
            question: The student's question
            context: Additional context about what they're studying
            conversation_history: Previous messages for context

        Returns:
            Answer string
        """
        messages = [
            {
                "role": "system",
                "content": "You are a helpful, patient tutor. Answer student questions clearly and encourage learning."
            }
        ]

        # Add conversation history if available
        if conversation_history:
            messages.extend(conversation_history[-5:])  # Last 5 messages for context

        # Add context if provided
        question_with_context = question
        if context:
            question_with_context = f"Context: {context}\n\nQuestion: {question}"

        messages.append({"role": "user", "content": question_with_context})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.6,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Sorry, I couldn't answer that question right now. Error: {str(e)}"

    def suggest_study_resources(
        self,
        topic: str,
        learning_style: str = "mixed"
    ) -> Dict[str, Any]:
        """
        Suggest study resources and strategies

        Args:
            topic: What the student is studying
            learning_style: visual, auditory, kinesthetic, or mixed

        Returns:
            Dict with resource suggestions
        """
        system_prompt = f"""You are a study coach. Suggest effective study resources and strategies for a {learning_style} learner.

Return ONLY valid JSON:
{{
  "strategies": ["strategy 1", "strategy 2"],
  "resources": ["resource 1", "resource 2"],
  "practice_tips": ["tip 1", "tip 2"]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Topic: {topic}"}
                ],
                temperature=0.6,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            return {
                "strategies": ["Review notes regularly", "Practice active recall"],
                "resources": ["Textbook", "Online tutorials"],
                "practice_tips": ["Take breaks", "Test yourself"]
            }


# Global instance
_ai_tutor = None


def get_ai_tutor() -> AITutor:
    """Get or create AI tutor singleton"""
    global _ai_tutor
    if _ai_tutor is None:
        _ai_tutor = AITutor()
    return _ai_tutor
