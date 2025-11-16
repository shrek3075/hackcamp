@echo off
echo ========================================
echo SmartPlanner - PDF Upload Test
echo ========================================
echo.
echo Uploading WWII-1.pdf...
echo.

curl -X POST "http://localhost:8000/syllabus/upload" ^
  -F "user_id=shrey_id" ^
  -F "files=@C:/Users/shrey/Downloads/HackCamp/WWII-1.pdf" ^
  -F "generate_quiz=true" ^
  -H "Accept: application/json"

echo.
echo.
echo ========================================
echo Upload Complete!
echo ========================================
pause
