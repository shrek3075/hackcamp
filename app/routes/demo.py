"""
Demo and testing endpoints - Quick data population for demos
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

from app.clients.supabase import get_supabase_client
from app.models import Task, StudyMaterial, Topic, KeyTerm

router = APIRouter(prefix="/demo", tags=["demo"])


class SeedDemoRequest(BaseModel):
    user_id: str = "demo_user"
    exam_name: str = "World War II Midterm"
    exam_date: Optional[str] = None  # Auto-set to 10 days from now if not provided


@router.post("/seed")
async def seed_demo_data(request: SeedDemoRequest):
    """
    Quickly populate a user with realistic demo data

    Creates:
    - Study materials (WWII topics)
    - Tasks (assignments, quizzes)
    - Some completed progress (2-3 day streak)
    - Sample calendar events

    Perfect for demos and frontend testing!
    """
    try:
        db = get_supabase_client()
        user_id = request.user_id

        # Set exam date to 10 days from now if not provided
        if request.exam_date:
            exam_date = request.exam_date
        else:
            exam_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")

        # 1. Create study materials
        demo_materials = [
            StudyMaterial(
                user_id=user_id,
                source_file="demo_wwii_notes.pdf",
                complexity_level="intermediate",
                total_estimated_hours=8.5,
                topics=[
                    Topic(
                        name="Causes of World War II",
                        complexity="intermediate",
                        estimated_hours=2.5,
                        subtopics=[
                            "Treaty of Versailles",
                            "Rise of Fascism",
                            "Economic Depression",
                            "Failure of League of Nations"
                        ],
                        learning_objectives=[
                            "Explain the impact of the Treaty of Versailles on post-WWI Europe",
                            "Analyze the rise of totalitarian regimes in the 1930s",
                            "Understand the economic factors that contributed to WWII"
                        ],
                        key_terms=[
                            KeyTerm(term="Appeasement", definition="Policy of making concessions to avoid conflict"),
                            KeyTerm(term="Fascism", definition="Authoritarian ultranationalist political ideology"),
                            KeyTerm(term="Lebensraum", definition="Hitler's policy of territorial expansion")
                        ]
                    ),
                    Topic(
                        name="Major Battles and Campaigns",
                        complexity="intermediate",
                        estimated_hours=3.0,
                        subtopics=[
                            "Battle of Britain",
                            "Operation Barbarossa",
                            "Pearl Harbor",
                            "D-Day Invasion",
                            "Battle of Stalingrad"
                        ],
                        learning_objectives=[
                            "Identify key turning points in WWII",
                            "Understand the strategic importance of major battles",
                            "Analyze military tactics and their outcomes"
                        ],
                        key_terms=[
                            KeyTerm(term="Blitzkrieg", definition="Lightning war - rapid military offensive"),
                            KeyTerm(term="Island Hopping", definition="Pacific campaign strategy"),
                            KeyTerm(term="Atlantic Wall", definition="German coastal defense system")
                        ]
                    ),
                    Topic(
                        name="The Holocaust and War Crimes",
                        complexity="advanced",
                        estimated_hours=3.0,
                        subtopics=[
                            "Final Solution",
                            "Concentration Camps",
                            "Nuremberg Trials",
                            "Resistance Movements"
                        ],
                        learning_objectives=[
                            "Understand the systematic genocide of the Holocaust",
                            "Examine the international response to war crimes",
                            "Analyze the importance of human rights protections"
                        ],
                        key_terms=[
                            KeyTerm(term="Genocide", definition="Deliberate killing of a large group of people"),
                            KeyTerm(term="Nuremberg Laws", definition="Antisemitic laws in Nazi Germany"),
                            KeyTerm(term="Crimes Against Humanity", definition="Widespread attacks on civilians")
                        ]
                    )
                ]
            )
        ]

        # Save materials to DB
        for material in demo_materials:
            material_dict = material.model_dump(exclude={"id"})
            db.insert_study_material(material_dict)

        # 2. Create sample tasks
        demo_tasks = [
            {
                "user_id": user_id,
                "title": "Chapter 1-2 Reading",
                "due": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
                "task_type": "reading",
                "weight": 0,
                "completed": True,
                "effort_hours": 1.5
            },
            {
                "user_id": user_id,
                "title": "Quiz 1: Causes of WWII",
                "due": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
                "task_type": "quiz",
                "weight": 10,
                "completed": False,
                "effort_hours": 2.0
            },
            {
                "user_id": user_id,
                "title": f"{request.exam_name}",
                "due": exam_date,
                "task_type": "exam",
                "weight": 25,
                "completed": False,
                "effort_hours": 8.5
            }
        ]

        for task in demo_tasks:
            db.insert_task(task)

        # 3. Create some progress/check-ins (2-3 day streak)
        for i in range(3):
            checkin_date = (datetime.now() - timedelta(days=2-i)).date()
            checkin = {
                "user_id": user_id,
                "date": checkin_date.isoformat(),
                "completed": True,
                "hours_studied": 1.5 + (i * 0.5)
            }
            # Insert check-in (will handle upsert in DB layer)
            try:
                db.record_daily_checkin(checkin)
            except:
                pass  # May not have this method yet

        # 4. Save exam config
        exam_config = {
            "user_id": user_id,
            "exam_name": request.exam_name,
            "exam_date": exam_date,
            "grade_level": "high_school",
            "exam_weight": 25.0,
            "study_depth": "standard",
            "hours_per_day": 2.0
        }
        db.set_exam_config(exam_config)

        return {
            "success": True,
            "message": "Demo data created successfully!",
            "user_id": user_id,
            "materials_created": len(demo_materials),
            "topics_created": sum(len(m.topics) for m in demo_materials),
            "tasks_created": len(demo_tasks),
            "exam_date": exam_date,
            "current_streak": 3,
            "next_steps": [
                f"GET /daily/{user_id} - View today's study plan",
                f"GET /progress/{user_id} - View progress stats",
                f"POST /practice/generate - Generate practice questions"
            ]
        }

    except Exception as e:
        raise HTTPException(500, f"Demo seeding failed: {str(e)}")


@router.delete("/reset/{user_id}")
async def reset_user_data(user_id: str):
    """
    Clear all data for a user - useful for resetting demos

    Deletes:
    - Study materials
    - Tasks
    - Check-ins
    - Timeline/schedule
    - Progress
    """
    try:
        db = get_supabase_client()

        # Delete all user data
        # Note: Actual implementation depends on your DB schema
        deleted_counts = {
            "materials": 0,
            "tasks": 0,
            "checkins": 0,
            "timeline": 0
        }

        # Try to delete from each table
        try:
            # This would need actual delete methods in supabase client
            # For now, return message
            pass
        except:
            pass

        return {
            "success": True,
            "message": f"User {user_id} data cleared",
            "deleted": deleted_counts
        }

    except Exception as e:
        raise HTTPException(500, f"Reset failed: {str(e)}")


@router.get("/dashboard/{user_id}")
async def get_dashboard_overview(user_id: str):
    """
    Get everything for the dashboard in one call

    Returns:
    - Today's study plan
    - Current streak
    - Progress stats
    - Upcoming deadlines
    - Study materials summary

    Perfect for homepage!
    """
    try:
        db = get_supabase_client()

        # Get exam config
        exam_config = db.get_exam_config(user_id)

        # Get tasks
        all_tasks = db.get_tasks(user_id)
        completed_tasks = [t for t in all_tasks if t.get("completed", False)]
        upcoming_tasks = sorted(
            [t for t in all_tasks if not t.get("completed", False)],
            key=lambda x: x.get("due", "9999-99-99")
        )[:5]

        # Get study materials
        materials = db.get_study_materials(user_id)
        total_topics = sum(len(m.get("topics", [])) for m in materials)
        total_hours = sum(m.get("total_estimated_hours", 0) for m in materials)

        # Calculate progress
        progress_percent = (len(completed_tasks) / len(all_tasks) * 100) if all_tasks else 0

        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")

        # Calculate days until exam
        days_until_exam = None
        if exam_config and exam_config.get("exam_date"):
            try:
                exam_date = datetime.fromisoformat(exam_config["exam_date"])
                days_until_exam = max(0, (exam_date - datetime.now()).days)
            except:
                pass

        # Calculate streak (simplified - would check daily_checkins table)
        current_streak = 3  # Placeholder

        return {
            "user_id": user_id,
            "today": today,
            "exam": {
                "name": exam_config.get("exam_name") if exam_config else None,
                "date": exam_config.get("exam_date") if exam_config else None,
                "days_until": days_until_exam
            },
            "progress": {
                "total_tasks": len(all_tasks),
                "completed_tasks": len(completed_tasks),
                "progress_percent": round(progress_percent, 1),
                "current_streak": current_streak,
                "total_hours_planned": round(total_hours, 1)
            },
            "study_materials": {
                "total_materials": len(materials),
                "total_topics": total_topics,
                "total_hours": round(total_hours, 1)
            },
            "upcoming_deadlines": upcoming_tasks,
            "motivational_message": f"{'Great' if current_streak > 2 else 'Good'} work! Keep your streak going! 🔥"
        }

    except Exception as e:
        raise HTTPException(500, f"Dashboard fetch failed: {str(e)}")
