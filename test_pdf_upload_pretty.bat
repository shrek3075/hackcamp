@echo off
echo ========================================
echo SmartPlanner - PDF Upload Test
echo ========================================
echo.
echo Uploading WWII-1.pdf and saving response...
echo.

curl -X POST "http://localhost:8000/syllabus/upload" ^
  -F "user_id=shrey_id" ^
  -F "files=@C:/Users/shrey/Downloads/HackCamp/WWII-1.pdf" ^
  -F "generate_quiz=true" ^
  -H "Accept: application/json" ^
  -o upload_response.json

echo.
echo ========================================
echo Upload Complete!
echo Response saved to: upload_response.json
echo ========================================
echo.
echo Opening response in notepad...
notepad upload_response.json
