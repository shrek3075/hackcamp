@echo off
echo 🧪 Testing Timeline Generation End-to-End
echo.

echo 1️⃣ Uploading study materials...
curl -X POST "http://localhost:8000/syllabus/upload" ^
  -F "user_id=test_timeline_user" ^
  -F "syllabus_text=World War II Study Guide\n\nChapter 1: Causes of WWII\n- Treaty of Versailles and German resentment\n- Rise of fascism in Europe\n- Economic depression and political instability\n- Failure of the League of Nations\n\nChapter 2: Major Events and Battles\n- Invasion of Poland (1939)\n- Battle of Britain (1940)\n- Operation Barbarossa (1941)\n- Pearl Harbor and US entry\n- D-Day invasion (1944)\n- Atomic bombs and Japan's surrender" ^
  -F "grade_level=high_school" ^
  -F "exam_date=2025-11-25" ^
  -F "exam_weight=25" ^
  -F "hours_per_day=2" ^
  -F "study_depth=standard" ^
  -F "generate_quiz=false"

echo.
echo.
echo 2️⃣ Generating timeline...
curl -X POST "http://localhost:8000/timeline/generate" ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\": \"test_timeline_user\"}"

echo.
echo.
echo ✅ Test complete!
pause
