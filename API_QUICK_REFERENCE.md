# SmartPlanner API - Quick Reference for Frontend

**Base URL**: `http://localhost:8000`

**API Docs**: `http://localhost:8000/docs` (Swagger UI)

## 🚀 DEMO ENDPOINTS (Start Here!)

### 1. Seed Demo Data
**Perfect for testing your frontend without uploading files**

```bash
POST /demo/seed
Content-Type: application/json

{
  "user_id": "demo_user",
  "exam_name": "World War II Midterm",
  "exam_date": "2025-11-25"  // optional, defaults to 10 days from now
}
```

**Response**:
```json
{
  "success": true,
  "message": "Demo data created successfully!",
  "user_id": "demo_user",
  "materials_created": 1,
  "topics_created": 3,
  "tasks_created": 3,
  "exam_date": "2025-11-25",
  "current_streak": 3
}
```

### 2. Get Dashboard Overview
**Everything you need for the homepage in ONE call**

```bash
GET /demo/dashboard/{user_id}
```

**Response**:
```json
{
  "user_id": "demo_user",
  "today": "2025-11-16",
  "exam": {
    "name": "World War II Midterm",
    "date": "2025-11-25",
    "days_until": 9
  },
  "progress": {
    "total_tasks": 3,
    "completed_tasks": 1,
    "progress_percent": 33.3,
    "current_streak": 3,
    "total_hours_planned": 8.5
  },
  "study_materials": {
    "total_materials": 1,
    "total_topics": 3,
    "total_hours": 8.5
  },
  "upcoming_deadlines": [...],
  "motivational_message": "Great work! Keep your streak going! 🔥"
}
```

### 3. Reset User Data
**Clear everything for a fresh demo**

```bash
DELETE /demo/reset/{user_id}
```

---

## 📚 CORE FEATURES

### Study Materials Upload

```bash
POST /syllabus/upload
Content-Type: multipart/form-data

user_id: demo_user
files: [file1.pdf, file2.jpg]
grade_level: high_school
exam_date: 2025-11-25
exam_weight: 25
hours_per_day: 2
study_depth: standard
generate_quiz: false
```

**OR upload text**:
```bash
syllabus_text: "Chapter 1: World War II Causes..."
```

### Get Today's Study Plan

```bash
GET /daily/{user_id}?user_name=John
```

**Response**:
```json
{
  "date": "2025-11-16",
  "todays_tasks": [
    {
      "time": "18:00-20:00",
      "topic": "Causes of World War II",
      "hours": 2.0,
      "type": "study"
    }
  ],
  "motivational_message": "Great job, John! You're on a 3-day streak!",
  "streak": 3,
  "progress_percent": 33.3
}
```

### Generate Practice Questions

```bash
POST /practice/generate
Content-Type: application/json

{
  "topic": "Causes of World War II",
  "difficulty": "medium",
  "num_questions": 5,
  "question_type": "multiple_choice"
}
```

**Response**:
```json
{
  "questions": [
    {
      "question": "What was the primary cause of WWII?",
      "options": {
        "A": "Treaty of Versailles",
        "B": "Economic depression",
        "C": "Rise of fascism",
        "D": "All of the above"
      },
      "correct_answer": "D",
      "explanation": "..."
    }
  ]
}
```

### AI Tutor Chat

```bash
POST /tutor/chat
Content-Type: application/json

{
  "user_id": "demo_user",
  "message": "Explain the causes of WWII",
  "conversation_history": []
}
```

**Response**:
```json
{
  "message": "The main causes of WWII were:\n• Treaty of Versailles...\n• Rise of fascism...",
  "referenced_topics": ["Causes of World War II"],
  "suggested_followups": [
    "What was the Treaty of Versailles?",
    "How did fascism rise in Europe?"
  ]
}
```

### Mark Progress / Check-in

```bash
POST /progress/checkin
Content-Type: application/json

{
  "user_id": "demo_user",
  "completed_block_ids": ["block_123"]
}
```

**Response**:
```json
{
  "success": true,
  "streak": 4,
  "hours_studied_today": 2.0,
  "total_hours_studied": 10.5,
  "message": "Amazing! 4 day streak! 🔥"
}
```

---

## 📅 CALENDAR INTEGRATION

### Upload Calendar (.ics file)

```bash
POST /calendar/upload
Content-Type: multipart/form-data

user_id: demo_user
file: calendar.ics
exam_date: 2025-11-25
preferred_study_start: 17  // 5pm
preferred_study_end: 21     // 9pm
```

**Response**:
```json
{
  "success": true,
  "blocks_extracted": 19,
  "free_time_analysis": {
    "total_free_hours": 45.5,
    "available_study_slots": [
      {
        "date": "2025-11-17",
        "day_name": "Sunday",
        "start": "17:00",
        "end": "21:00",
        "duration_hours": 4.0
      }
    ]
  }
}
```

---

## 🗓️ TIMELINE GENERATION

### Generate Study Timeline

```bash
POST /timeline/generate
Content-Type: application/json

{
  "user_id": "demo_user"
}
```

**Response**:
```json
{
  "metadata": {
    "total_hours": 8.5,
    "tasks_scheduled": 12,
    "days_covered": 9,
    "exam_date": "2025-11-25"
  },
  "schedule": [
    {
      "date": "2025-11-17",
      "day_name": "Sunday",
      "session_start": "18:00",
      "session_end": "20:00",
      "total_hours": 2.0,
      "tasks": [
        {
          "title": "Study: Causes of WWII",
          "duration_hours": 2.0,
          "topic": "Causes of World War II"
        }
      ]
    }
  ]
}
```

---

## ⚙️ CONFIGURATION

### Set Exam Config

```bash
POST /config/exam
Content-Type: application/json

{
  "user_id": "demo_user",
  "exam_name": "WWII Midterm",
  "exam_date": "2025-11-25",
  "grade_level": "high_school",
  "exam_weight": 25,
  "study_depth": "standard",
  "hours_per_day": 2.0
}
```

### Get Exam Config

```bash
GET /config/exam/{user_id}
```

---

## 📊 PROGRESS TRACKING

### Get Progress Stats

```bash
GET /progress/{user_id}
```

**Response**:
```json
{
  "total_tasks": 10,
  "completed_tasks": 4,
  "progress_percent": 40.0,
  "current_streak": 3,
  "total_hours_studied": 12.5,
  "days_studied": 5,
  "average_hours_per_day": 2.5,
  "next_milestone": "50% complete"
}
```

---

## 💡 QUICK START FOR FRONTEND

### Complete User Flow (Recommended)

```javascript
// 1. Seed demo data
const seedResponse = await fetch('http://localhost:8000/demo/seed', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_id: 'demo_user' })
});

// 2. Get dashboard overview
const dashboard = await fetch('http://localhost:8000/demo/dashboard/demo_user');
const data = await dashboard.json();

// 3. Show today's plan
const todaysPlan = await fetch('http://localhost:8000/daily/demo_user');

// 4. Generate practice questions
const practice = await fetch('http://localhost:8000/practice/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    topic: 'Causes of World War II',
    difficulty: 'medium',
    num_questions: 5,
    question_type: 'multiple_choice'
  })
});

// 5. Mark progress
const checkin = await fetch('http://localhost:8000/progress/checkin', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 'demo_user',
    completed_block_ids: []
  })
});
```

---

## 🎯 RECOMMENDED UI FLOW

### Page 1: Dashboard / Home
- Call `/demo/dashboard/{user_id}`
- Show: Streak, Progress %, Days until exam, Today's tasks

### Page 2: Today's Study
- Call `/daily/{user_id}`
- Show: Today's topics, Time blocks, Motivational message
- Button: "Start Studying" → Go to Practice

### Page 3: Practice Questions
- Call `/practice/generate` with current topic
- Show: Interactive quiz
- On complete → Call `/progress/checkin`

### Page 4: AI Tutor (Optional)
- Call `/tutor/chat`
- Chat interface for Q&A

### Page 5: Progress Stats
- Call `/progress/{user_id}`
- Show: Graphs, Streaks, Achievements

---

## 🔧 TESTING TIPS

1. **Start with demo data**: Call `/demo/seed` first
2. **Use Swagger UI**: Go to `http://localhost:8000/docs` to test endpoints
3. **Check server logs**: Server prints useful debug info
4. **Reset between tests**: Call `/demo/reset/{user_id}`

---

## ⚠️ COMMON ISSUES

**CORS errors?**
- Already configured with `allow_origins=["*"]`
- Should work from any frontend

**No data returned?**
- Make sure you called `/demo/seed` first
- Or upload actual syllabus with `/syllabus/upload`

**Encoding errors?**
- Fixed with UTF-8 configuration
- If you see weird characters, refresh server

---

## 🚀 DEPLOYMENT (Later)

For now, run locally:
```bash
cd HackCamp
python -m uvicorn app.main:app --reload
```

Access at: `http://localhost:8000`

---

**Questions?** Check `/docs` or ask Claude! 🤖
