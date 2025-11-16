"""
Test timeline generation end-to-end

This script tests the complete flow:
1. Upload study materials with exam date
2. Generate timeline
"""
import requests
import json
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000"
USER_ID = "test_timeline_user"

def test_timeline_flow():
    print("🧪 Testing Timeline Generation End-to-End\n")

    # Step 1: Upload study materials with exam date
    print("1️⃣ Uploading study materials...")

    exam_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")

    # Test with text-based syllabus
    upload_data = {
        "user_id": USER_ID,
        "syllabus_text": """
World War II Study Guide

Chapter 1: Causes of WWII
- Treaty of Versailles and German resentment
- Rise of fascism in Europe
- Economic depression and political instability
- Failure of the League of Nations

Chapter 2: Major Events and Battles
- Invasion of Poland (1939)
- Battle of Britain (1940)
- Operation Barbarossa (1941)
- Pearl Harbor and US entry
- D-Day invasion (1944)
- Atomic bombs and Japan's surrender

Chapter 3: Key Leaders and Decisions
- Hitler, Stalin, Churchill, Roosevelt
- Strategic alliances and diplomacy
- War crimes and the Holocaust

Chapter 4: Home Front and Society
- War production and rationing
- Role of women in the workforce
- Propaganda and public morale
        """,
        "grade_level": "high_school",
        "exam_date": exam_date,
        "exam_weight": "25",
        "hours_per_day": "2",
        "study_depth": "standard",
        "generate_quiz": "false"
    }

    try:
        response = requests.post(
            f"{API_BASE}/syllabus/upload",
            data=upload_data,
            timeout=60
        )

        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code}")
            print(response.text)
            return False

        result = response.json()
        print(f"✅ Upload successful!")
        print(f"   - Materials extracted: {len(result.get('study_materials', []))}")
        print(f"   - Topics found: {sum(len(m.get('topics', [])) for m in result.get('study_materials', []))}")

        if result.get('study_schedule'):
            schedule = result['study_schedule']
            print(f"   - Study schedule generated: {len(schedule.get('daily_schedule', []))} days")
            print(f"   - Total hours: {schedule.get('metadata', {}).get('total_hours_needed', 0)}h")

        print()

    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

    # Step 2: Generate timeline
    print("2️⃣ Generating timeline...")

    try:
        response = requests.post(
            f"{API_BASE}/timeline/generate",
            json={"user_id": USER_ID},
            timeout=60
        )

        if response.status_code != 200:
            print(f"❌ Timeline generation failed: {response.status_code}")
            print(response.text)
            return False

        result = response.json()
        print(f"✅ Timeline generated!")

        metadata = result.get('metadata', {})
        print(f"\n📊 Timeline Metadata:")
        print(f"   - Total hours: {metadata.get('total_hours', 0)}h")
        print(f"   - Tasks scheduled: {metadata.get('tasks_scheduled', 0)}")
        print(f"   - Days covered: {metadata.get('days_covered', 0)}")
        print(f"   - Exam date: {metadata.get('exam_date', 'N/A')}")

        schedule = result.get('schedule', [])
        print(f"\n📅 Daily Schedule ({len(schedule)} days):")

        for i, day in enumerate(schedule[:5], 1):  # Show first 5 days
            print(f"\n   Day {i}: {day.get('date', 'N/A')} ({day.get('day_name', 'N/A')})")
            print(f"   Time: {day.get('session_start', 'N/A')} - {day.get('session_end', 'N/A')}")
            print(f"   Total hours: {day.get('total_hours', 0)}h")

            tasks = day.get('tasks', [])
            if tasks:
                print(f"   Tasks ({len(tasks)}):")
                for task in tasks[:3]:  # Show first 3 tasks
                    print(f"     - {task.get('title', 'Untitled')} ({task.get('duration_hours', 0)}h)")

        if len(schedule) > 5:
            print(f"\n   ... and {len(schedule) - 5} more days")

        print("\n✅ Timeline generation test PASSED!")
        return True

    except Exception as e:
        print(f"❌ Timeline generation error: {e}")
        return False

if __name__ == "__main__":
    success = test_timeline_flow()
    exit(0 if success else 1)
