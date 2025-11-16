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
        self.nano_model = "gpt-4o-mini"  # Using mini for smart scheduling tasks

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

    def extract_comprehensive_study_content(
        self,
        text: Optional[str] = None,
        images: Optional[List[str]] = None,
        filename: str = ""
    ) -> Dict[str, Any]:
        """
        Extract comprehensive study content from text/images

        Analyzes study materials to extract:
        - Topics and subtopics
        - Learning objectives
        - Key terms with definitions
        - Complexity analysis
        - Study time estimates

        Args:
            text: Extracted text content (if available)
            images: List of base64 encoded images (from PDF pages or photos)
            filename: Original filename for context

        Returns:
            Dict with topics, overall_complexity, and other metadata
        """
        system_prompt = """You are an expert educational content analyzer. Extract comprehensive study information from the provided materials.

Analyze the content deeply and return ONLY valid JSON (no markdown):
{
  "topics": [
    {
      "name": "Topic name",
      "subtopics": ["Subtopic 1", "Subtopic 2"],
      "complexity": "beginner|intermediate|advanced",
      "estimated_hours": 3.0,
      "learning_objectives": [
        "Understand concept X",
        "Be able to apply Y"
      ],
      "key_terms": [
        {
          "term": "Important Term",
          "definition": "Clear, concise definition",
          "importance": "high|medium|low"
        }
      ]
    }
  ],
  "overall_complexity": "beginner|intermediate|advanced|mixed",
  "suggested_prerequisites": ["Topic A", "Topic B"],
  "estimated_total_hours": 10.0
}

Guidelines:
- Extract ALL major topics, not just headings
- Identify learning objectives (what student should be able to do)
- Extract key terms with accurate definitions
- Estimate complexity based on content depth
- Estimate realistic study hours per topic
- Be thorough but concise"""

        messages = [{"role": "system", "content": system_prompt}]

        # Build user message with available content
        if images and len(images) > 0:
            # Vision-based analysis
            content = [{"type": "text", "text": f"Analyze this study material from '{filename}' and extract comprehensive content:"}]

            # Add text if available
            if text:
                content.append({"type": "text", "text": f"\n\nExtracted text:\n{text[:3000]}"})  # Limit to avoid token overflow

            # Add images
            for img_b64 in images[:10]:  # Limit to 10 images
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{img_b64}"}
                })

            messages.append({"role": "user", "content": content})

        elif text:
            # Text-only analysis
            messages.append({
                "role": "user",
                "content": f"Analyze this study material from '{filename}':\n\n{text}"
            })

        else:
            raise ValueError("Must provide either text or images")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            # Validate structure
            if "topics" not in result:
                result["topics"] = []
            if "overall_complexity" not in result:
                result["overall_complexity"] = "mixed"

            return result

        except json.JSONDecodeError as e:
            raise ValueError(f"AI returned invalid JSON: {e}")
        except Exception as e:
            raise Exception(f"Content extraction failed: {str(e)}")

    def generate_diagnostic_quiz(
        self,
        topics: List[Dict[str, Any]],
        questions_per_topic: int = 3
    ) -> Dict[str, Any]:
        """
        Generate diagnostic quiz questions to assess current knowledge

        Args:
            topics: List of topics with their subtopics, key_terms, and learning_objectives
            questions_per_topic: Number of questions to generate per topic

        Returns:
            Dict with questions array
        """
        system_prompt = """You are an expert educational assessment designer. Create diagnostic quiz questions to assess student knowledge.

Create multiple-choice questions that:
- Test understanding of key concepts
- Range from basic to advanced difficulty
- Have clear, unambiguous correct answers
- Include helpful explanations
- Cover different aspects of each topic

Return ONLY valid JSON (no markdown):
{
  "questions": [
    {
      "topic": "Topic Name",
      "question": "Clear question text?",
      "options": {
        "A": "First option",
        "B": "Second option",
        "C": "Third option",
        "D": "Fourth option"
      },
      "correct_answer": "B",
      "explanation": "Brief explanation of why B is correct"
    }
  ]
}

Guidelines:
- Make questions specific and focused
- Include distractors that test common misconceptions
- Vary difficulty levels (easy, medium, hard)
- Ensure exactly one correct answer
- Keep questions concise but complete"""

        try:
            # Prepare topics summary
            topics_summary = []
            for topic in topics:
                summary = {
                    "name": topic["name"],
                    "subtopics": topic.get("subtopics", []),
                    "key_terms": [kt["term"] for kt in topic.get("key_terms", [])[:5]],  # Limit to 5
                    "complexity": topic.get("complexity", "intermediate")
                }
                topics_summary.append(summary)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Generate {questions_per_topic} diagnostic questions per topic:\n{json.dumps(topics_summary, indent=2)}"
                    }
                ],
                temperature=0.7,  # Higher temperature for variety
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            # Validate structure
            if "questions" not in result:
                result["questions"] = []

            return result

        except json.JSONDecodeError as e:
            raise ValueError(f"AI returned invalid JSON: {e}")
        except Exception as e:
            raise Exception(f"Quiz generation failed: {str(e)}")

    def generate_smart_study_schedule(
        self,
        topics: List[Dict],
        exam_date: str,
        current_date: str,
        max_hours_per_day: float = 2.0,
        busy_blocks: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Use AI to generate an intelligent study schedule

        Args:
            topics: List of topics with names, hours, complexity
            exam_date: When is the exam (YYYY-MM-DD)
            current_date: Today's date (YYYY-MM-DD)
            max_hours_per_day: Maximum study hours per day
            busy_blocks: Optional list of busy time blocks from calendar

        Returns:
            Dict with daily_schedule array
        """
        system_prompt = """You are an expert study planner. Create a realistic, optimized study schedule that USES THE FULL TIME PERIOD AVAILABLE.

🚨 CRITICAL RULE: If the user has 55 days until the exam, your schedule MUST span most of those 55 days, NOT just 7-10 days!

IMPORTANT RULES:
- USE THE FULL TIME PERIOD - if they have 50+ days, create 40+ study days
- Distribute topics intelligently based on difficulty and importance
- Harder topics get more time early on
- Spread learning over time (spacing effect) - don't cram everything into a few days
- Review day should only review, not learn new material (max 30% of original time per topic)
- NEVER exceed the max_hours_per_day limit
- Each day should be realistic and achievable (light days are OK!)
- Better to study 30 minutes for 50 days than 5 hours for 7 days

Return ONLY valid JSON:
{
  "daily_schedule": [
    {
      "date": "2025-11-16",
      "day_name": "Saturday",
      "topics": [
        {
          "topic_name": "Topic 1",
          "hours": 1.5,
          "rationale": "Starting with hardest topic while fresh"
        }
      ],
      "total_hours": 1.5
    }
  ]
}"""

        # Build the request
        from datetime import datetime as dt
        exam_dt = dt.fromisoformat(exam_date)
        current_dt = dt.fromisoformat(current_date)
        days_available = (exam_dt - current_dt).days

        topics_summary = []
        total_hours_needed = 0
        for t in topics:
            topics_summary.append({
                "name": t["name"],
                "estimated_hours": t["estimated_hours"],
                "complexity": t["complexity"],
                "subtopics_count": len(t.get("subtopics", []))
            })
            total_hours_needed += t["estimated_hours"]

        user_message = f"""Create a study schedule with these constraints:

EXAM DATE: {exam_date}
CURRENT DATE: {current_date}
DAYS AVAILABLE: {days_available} days
MAX HOURS/DAY: {max_hours_per_day}h
TOTAL HOURS NEEDED: {total_hours_needed}h

TOPICS TO COVER:
{json.dumps(topics_summary, indent=2)}

{"BUSY BLOCKS (avoid these times):" + json.dumps(busy_blocks, indent=2) if busy_blocks else ""}

🚨 CRITICAL REQUIREMENTS:
1. CREATE A SCHEDULE FOR THE FULL {days_available} DAYS (or close to it)
2. Use BLOCK STUDY METHOD: Study complete topics in focused blocks (1-3 days per topic)
3. After completing a topic/block, REVIEW it before moving to the next
4. Start studying NOW and continue until the exam
5. Aim for {round(total_hours_needed / max(1, days_available - 1), 1)}h per day average
6. You can have lighter days (1h) and heavier days ({max_hours_per_day}h), but use the full time

Schedule strategy (BLOCK METHOD):
- Study ONE complete topic/unit at a time in 1-3 day blocks
- Complete all learning for a topic before moving to the next (don't split topics)
- After finishing each topic block, do a review session (30min-1h)
- Prioritize harder/complex topics earlier
- Final 2-3 days: comprehensive review of ALL topics
- Never exceed {max_hours_per_day}h per day
- Aim for {max(days_available - 2, days_available * 0.8)} study days minimum

Example flow: Topic A (2 days) → Review A (30min) → Topic B (1 day) → Review B → Topic C (2 days) → Review C → Final Review All (2 days)"""

        try:
            # Calculate max_tokens based on days (need ~50 tokens per day)
            estimated_tokens = max(2000, days_available * 60)
            max_tokens_limit = min(16000, estimated_tokens)  # Cap at 16k

            response = self.client.chat.completions.create(
                model=self.model,  # Use full model for complex scheduling
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,  # Higher temp for creative schedule distribution
                max_tokens=max_tokens_limit,  # Allow long schedules
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            raise Exception(f"AI schedule generation failed: {str(e)}")

    def teach_with_context(
        self,
        user_question: str,
        study_materials: List[Dict],
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Teaching-focused AI that helps students learn from their study materials

        Like NotebookLM - has full context of all documents and teaches concepts

        Args:
            user_question: Student's question
            study_materials: List of study materials with topics, terms, etc.
            conversation_history: Previous messages for context

        Returns:
            Dict with response, referenced_topics, and suggested_followups
        """
        system_prompt = """You are a STRICT tutor who ONLY uses the student's uploaded notes.

🚨 ABSOLUTE RULES - NEVER BREAK THESE:

1. **ONLY USE THE STUDENT'S STUDY MATERIALS BELOW**
   - If asked for "key points" → COPY them directly from the notes
   - If asked "what are the causes" → LIST only what's in the notes
   - DO NOT add your own knowledge or examples
   - DO NOT expand beyond what's written in their materials

2. **FOR SIMPLE REQUESTS (key points, list, summary):**
   - Just EXTRACT and FORMAT the information from the notes
   - Don't explain unless asked
   - Don't add context from AI knowledge
   - Example: "Give me key points" → List ONLY points from notes

3. **IF ASKED TO EXPLAIN:**
   - Use ONLY concepts from the notes to explain
   - Don't bring in outside knowledge
   - Reference the notes explicitly

4. **IF TOPIC NOT IN NOTES:**
   - Say: "That's not in your uploaded notes."
   - STOP THERE. Don't provide AI knowledge.
   - Suggest: "Check your textbook or ask your professor."

5. **ALWAYS START WITH:**
   - "From your notes on [topic]..."
   - "Your notes mention..."
   - "According to your uploaded materials..."

6. **NEVER SAY:**
   - "Generally..." or "Typically..." (that's AI knowledge)
   - Don't add historical context not in notes
   - Don't provide examples not in notes

YOUR ONLY JOB: Extract and format information FROM THE NOTES. Nothing else.

✨ FORMATTING REQUIREMENTS - YOU MUST USE THESE:
- **ALWAYS** use **bold** for key terms, names, dates, and important concepts
- **ALWAYS** use bullet points (•) when listing 2+ items or explaining multiple concepts
- Use numbered lists (1., 2., 3.) for steps or sequences
- Break content into SHORT paragraphs (2-3 sentences max)
- Add blank lines between distinct ideas

📝 EXAMPLE RESPONSES:

User: "Give me key points on causes of WWII"
You: "From your notes on WWII causes:
• **Treaty of Versailles** - imposed harsh terms on Germany
• **Economic depression** - created instability in Europe
• **Rise of fascism** - Hitler's Nazi party gained power"

User: "Explain the Treaty of Versailles"
You: "According to your notes:
The **Treaty of Versailles** (1919) ended WWI but created resentment in Germany. Your notes mention it:
• Forced Germany to accept blame for the war
• Required massive reparations payments
• Reduced German military size
This treaty is listed in your materials as a key cause of WWII."

❌ WRONG (using AI knowledge):
"The Treaty of Versailles was signed on June 28, 1919. Generally, historians view it as..."

✅ CORRECT (from notes only):
"Your notes state the Treaty of Versailles imposed harsh terms on Germany after WWI."

🚫 ABSOLUTE RULE: If it's not in the notes, DON'T say it.

Keep responses SHORT and directly from notes. 2-3 bullet points max for simple requests."""

        # Build context from study materials
        materials_context = "=== STUDENT'S STUDY MATERIALS ===\n\n"
        materials_context += "Below is the FULL CONTENT from the student's uploaded notes. Use this to answer their questions.\n\n"

        for material in study_materials:
            materials_context += f"\n{'='*60}\n"
            materials_context += f"📄 DOCUMENT: {material.get('source_file', 'Document')}\n"
            materials_context += f"{'='*60}\n\n"

            # Include FULL raw content if available (like NotebookLM)
            raw_content = material.get('raw_content')
            if raw_content:
                materials_context += f"{raw_content}\n\n"
            else:
                # Fallback to structured topics if no raw content
                materials_context += f"Complexity: {material.get('complexity_level', 'mixed')}\n\n"

                for topic in material.get('topics', []):
                    materials_context += f"Topic: {topic.get('name')}\n"
                    materials_context += f"Subtopics: {', '.join(topic.get('subtopics', []))}\n"

                    # Add key terms
                    if topic.get('key_terms'):
                        materials_context += "Key Terms:\n"
                        for kt in topic.get('key_terms', []):
                            materials_context += f"  • {kt.get('term')}: {kt.get('definition')}\n"

                    # Add learning objectives
                    if topic.get('learning_objectives'):
                        materials_context += "Learning Objectives:\n"
                        for obj in topic.get('learning_objectives', []):
                            materials_context += f"  • {obj}\n"

                    materials_context += "\n"

        materials_context += f"\n{'='*60}\n"
        materials_context += "=== END OF MATERIALS ===\n\n"

        # Build conversation
        messages = [{"role": "system", "content": system_prompt}]

        # Add materials context
        messages.append({"role": "system", "content": materials_context})

        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-6:]:  # Last 6 messages for context
                messages.append({
                    "role": msg.get("role"),
                    "content": msg.get("content")
                })

        # Add current question with strict reminder
        user_message = f"""{user_question}

REMINDER: Answer ONLY using the study materials provided above. Do not use your general AI knowledge. If the information is not in the notes, say so."""
        messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # LOW temp = stick to facts from notes, no creativity
                max_tokens=600  # Shorter responses
            )

            answer = response.choices[0].message.content.strip()

            # Extract referenced topics (simple heuristic - could be improved)
            referenced_topics = []
            for material in study_materials:
                for topic in material.get('topics', []):
                    topic_name = topic.get('name', '')
                    if topic_name.lower() in answer.lower():
                        referenced_topics.append(topic_name)

            # Generate follow-up suggestions
            followup_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Generate 2-3 short follow-up questions a student might ask to deepen their understanding. Return as JSON array."},
                    {"role": "user", "content": f"Original question: {user_question}\nAnswer given: {answer}\n\nSuggest follow-ups as JSON: {{\"followups\": [\"question1\", \"question2\"]}}"}
                ],
                temperature=0.7,
                max_tokens=150,
                response_format={"type": "json_object"}
            )

            followup_data = json.loads(followup_response.choices[0].message.content)
            suggested_followups = followup_data.get("followups", [])

            return {
                "message": answer,
                "referenced_topics": list(set(referenced_topics)),  # Deduplicate
                "suggested_followups": suggested_followups
            }

        except Exception as e:
            print(f"Teaching AI failed: {e}")
            return {
                "message": "I'm having trouble processing that right now. Could you rephrase your question?",
                "referenced_topics": [],
                "suggested_followups": []
            }

    def analyze_study_guide(
        self,
        content: str,
        guide_type: str = "study_guide"
    ) -> Dict[str, Any]:
        """
        Analyze a study guide or practice test to extract focus topics

        This helps the AI prioritize certain topics in:
        - Quiz generation
        - Study time allocation
        - Tutor responses

        Args:
            content: Text content of study guide/practice test
            guide_type: Type (study_guide, practice_test, exam_outline)

        Returns:
            Dict with focus_topics, key_concepts, question_types
        """
        system_prompt = """Analyze this study guide/practice test to identify key focus areas.

Your goal: Extract what topics the student should FOCUS ON for their exam.

Return ONLY valid JSON:
{
  "focus_topics": [
    "Topic 1 name",
    "Topic 2 name"
  ],
  "key_concepts": [
    "Key concept 1",
    "Key concept 2"
  ],
  "question_types": [
    "Multiple choice",
    "Short answer",
    "Essay"
  ],
  "importance_weights": {
    "Topic 1 name": 10,
    "Topic 2 name": 8
  }
}

Extract:
1. Main topics/themes covered (focus_topics)
2. Specific concepts emphasized (key_concepts)
3. Types of questions used (question_types)
4. Weight each topic by how much it appears (importance_weights, scale 1-10)

If it's a practice test, infer topics from the questions.
If it's a study guide, use the section headings and emphasized content."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Type: {guide_type}\n\nContent:\n{content[:4000]}"}  # Limit context
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"Study guide analysis failed: {e}")
            return {
                "focus_topics": [],
                "key_concepts": [],
                "question_types": ["multiple_choice"],
                "importance_weights": {}
            }

    def generate_focused_quiz(
        self,
        study_materials: List[Dict],
        focus_topics: List[str],
        key_concepts: List[str],
        num_questions: int = 10,
        difficulty: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate quiz FOCUSED on specific topics from study guide

        Unlike regular quiz generation, this:
        - Only covers topics in focus_topics
        - Emphasizes key_concepts
        - Mirrors exam-like questions

        Args:
            study_materials: All study content
            focus_topics: Topics to focus on (from study guide)
            key_concepts: Specific concepts to cover
            num_questions: Number of questions
            difficulty: easy, medium, or hard

        Returns:
            Quiz with questions focused on priority areas
        """
        system_prompt = f"""Generate a {difficulty} difficulty quiz FOCUSED on specific exam topics.

🎯 PRIORITY TOPICS (focus on these):
{json.dumps(focus_topics, indent=2)}

🔑 KEY CONCEPTS (must cover):
{json.dumps(key_concepts, indent=2)}

Generate {num_questions} multiple choice questions that:
1. ONLY cover the priority topics listed above
2. Include all key concepts
3. Mirror real exam questions (not just definition recall)
4. Test understanding, not just memorization
5. Distribute evenly across focus topics

Return ONLY valid JSON:
{{
  "questions": [
    {{
      "question": "What was the primary cause of...?",
      "topic": "Topic name from focus_topics",
      "options": {{
        "A": "Option 1",
        "B": "Option 2",
        "C": "Option 3",
        "D": "Option 4"
      }},
      "correct_answer": "A",
      "explanation": "Brief explanation with reference to key concepts",
      "difficulty": "{difficulty}",
      "covers_key_concepts": ["concept1", "concept2"]
    }}
  ]
}}"""

        # Build context from study materials
        materials_context = ""
        for material in study_materials[:3]:  # Limit to 3 materials to save tokens
            materials_context += f"\n{material.get('source_file', 'Document')}:\n"
            for topic in material.get('topics', [])[:5]:
                materials_context += f"  - {topic.get('name')}\n"
                if topic.get('subtopics'):
                    for sub in topic.get('subtopics', [])[:3]:
                        materials_context += f"    • {sub}\n"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Study materials context:\n{materials_context[:2000]}\n\nGenerate focused quiz."}
                ],
                temperature=0.6,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"Focused quiz generation failed: {e}")
            return {"questions": []}


# Global singleton
_ai_client: Optional[AIClient] = None


def get_ai_client() -> AIClient:
    """Get or create AI client singleton"""
    global _ai_client
    if _ai_client is None:
        _ai_client = AIClient()
    return _ai_client
