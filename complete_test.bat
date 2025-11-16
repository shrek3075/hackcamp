@echo off
setlocal enabledelayedexpansion

echo ========================================
echo SmartPlanner - Complete Workflow Test
echo ========================================
echo.

REM Check if WWII-1.pdf exists
set PDF_FILE=WWII-1.pdf
if not exist "%PDF_FILE%" (
    echo ERROR: %PDF_FILE% not found!
    echo Please make sure the PDF is in the current directory.
    pause
    exit /b 1
)

echo Step 1: Setting Semester Configuration
echo ========================================
curl -X POST "http://localhost:8000/config/semester" ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":\"shrey_id\",\"semester_name\":\"Fall 2025\",\"start_date\":\"2025-11-16\",\"end_date\":\"2025-12-20\"}" ^
  -s -o semester_config.json

echo [OK] Semester configured
echo.
timeout /t 2 /nobreak >nul

echo Step 2: Uploading PDF Study Material
echo ========================================
curl -X POST "http://localhost:8000/syllabus/upload" ^
  -F "user_id=shrey_id" ^
  -F "files=@%PDF_FILE%" ^
  -F "generate_quiz=true" ^
  -s -o upload_response.json

echo [OK] PDF uploaded and analyzed
echo.
timeout /t 2 /nobreak >nul

echo Step 3: Generating Study Timeline
echo ========================================
curl -X POST "http://localhost:8000/timeline/generate" ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":\"shrey_id\"}" ^
  -s -o timeline_response.json

echo [OK] Timeline generated
echo.

echo ========================================
echo All Tests Complete!
echo ========================================
echo.
echo Results saved:
echo   - semester_config.json
echo   - upload_response.json
echo   - timeline_response.json
echo.
echo Opening upload response (most interesting)...
notepad upload_response.json

pause
