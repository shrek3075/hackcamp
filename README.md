# SmartPlanner - AI-Powered Study Planning Backend 🎓

Duolingo-style study app that transforms syllabuses into personalized study timelines with AI coaching, practice questions, and gamification.

## 🚀 Features

- **Vision-Based Syllabus Extraction**: Upload PDF/image syllabuses → AI extracts all assignments, exams, projects
- **Calendar Integration**: Upload .ics calendar → AI categorizes events (no keyword matching!)
- **Smart Timeline Generation**: AI creates study schedule around your busy times
- **Daily Study Coach**: Duolingo-style daily recommendations and motivational messages
- **AI Practice Questions**: Generate practice problems for any topic
- **AI Tutor**: Explain concepts, answer questions, suggest resources
- **Progress Tracking**: Streaks, badges, stats, achievements

## 📋 Tech Stack

- **Backend**: FastAPI (Python)
- **AI**: OpenAI GPT-4o-mini (vision-capable, cheap, fast)
- **Database**: Supabase (PostgreSQL)
- **Deployment**: Uvicorn ASGI server

## 🛠️ Setup (15 minutes)

### 1. Prerequisites

- Python 3.9+
- OpenAI API key (get from https://platform.openai.com/api-keys)
- Supabase account (get from https://supabase.com)

### 2. Clone Repository

```bash
git clone https://github.com/shrek3075/hackcamp.git
cd hackcamp
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: For PDF vision support, also install:
```bash
pip install pdf2image
```

And install Poppler (required for pdf2image):
- **Windows**: Download from https://github.com/oschwartz10612/poppler-windows/releases/
- **Mac**: `brew install poppler`
- **Linux**: `sudo apt-get install poppler-utils`

### 4. Set Up Supabase

1. Go to https://supabase.com/dashboard
2. Create a new project
3. Go to SQL Editor
4. Copy and paste the contents of `supabase_schema.sql`
5. Run the SQL to create all tables
6. Get your API keys from Settings → API

### 5. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your keys:
```env
OPENAI_API_KEY=sk-your-openai-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

### 6. Run the Server

```bash
uvicorn app.main:app --reload
```

Server starts at: **http://localhost:8000**

API docs at: **http://localhost:8000/docs**

## 📚 API Endpoints

### Syllabus Management
- `POST /syllabus/upload` - Upload PDF/image syllabus
- `GET /syllabus/tasks/{user_id}` - Get extracted tasks

### Calendar
- `POST /calendar/upload` - Upload .ics calendar
- `GET /calendar/busy-blocks/{user_id}` - Get busy times

### Timeline Generation
- `POST /timeline/generate` - Generate study schedule
- `GET /timeline/{plan_id}` - Get specific timeline
- `GET /timeline/latest/{user_id}` - Get latest timeline

### Daily Coaching
- `GET /daily/{user_id}` - Get today's study plan (Duolingo-style)

### Practice & Tutoring
- `POST /practice/generate` - Generate practice questions
- `POST /practice/check-answer` - Check answer with AI feedback
- `POST /practice/explain` - AI explains a concept
- `POST /practice/ask` - Ask AI tutor a question
- `GET /practice/resources/{topic}` - Get study resource suggestions

### Progress Tracking
- `POST /progress/checkin` - Daily check-in (update streak)
- `GET /progress/stats/{user_id}` - Get progress statistics
- `GET /progress/report/{user_id}` - Comprehensive progress report
- `POST /progress/task/{task_id}/complete` - Mark task complete

### Health Check
- `GET /health` - Check API and service status

## 🎯 Complete User Flow

### Step 1: Onboarding (Upload Content)

**Upload Syllabus:**
```bash
curl -X POST "http://localhost:8000/syllabus/upload" \
  -F "user_id=user123" \
  -F "file=@syllabus.pdf"
```

Response:
```json
{
  "success": true,
  "tasks_extracted": 15,
  "tasks": [
    {
      "id": "uuid",
      "title": "Assignment 1: Intro to Python",
      "due_date": "2024-02-15",
      "task_type": "assignment",
      "weight": 15.0,
      "effort_hours": 4.5
    }
  ]
}
```

**Upload Calendar:**
```bash
curl -X POST "http://localhost:8000/calendar/upload" \
  -F "user_id=user123" \
  -F "file=@calendar.ics"
```

### Step 2: Generate Timeline

```bash
curl -X POST "http://localhost:8000/timeline/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "preferences": {
      "max_hours_per_day": 6.0,
      "preferred_start_time": "09:00",
      "preferred_end_time": "22:00"
    }
  }'
```

Response:
```json
{
  "plan_id": "uuid",
  "blocks": [
    {
      "task_title": "Assignment 1: Intro to Python",
      "start": "2024-02-01T14:00:00Z",
      "end": "2024-02-01T16:30:00Z",
      "duration_hours": 2.5,
      "reason": "due in 14 days, 15% of grade, session 1/2"
    }
  ],
  "total_hours": 45.5
}
```

### Step 3: Daily Study (Duolingo-Style)

```bash
curl "http://localhost:8000/daily/user123?user_name=Alex"
```

Response:
```json
{
  "date": "2024-02-01",
  "blocks": [
    {
      "task_title": "Assignment 1",
      "start": "2024-02-01T14:00:00Z",
      "end": "2024-02-01T16:30:00Z"
    }
  ],
  "total_hours": 2.5,
  "motivation": "Great work Alex! You're on a 5-day streak! Today's focus: Assignment 1. Let's keep the momentum going! 🔥",
  "streak": 5,
  "progress_percent": 23.5
}
```

### Step 4: Practice & Learn

**Generate Practice Questions:**
```bash
curl -X POST "http://localhost:8000/practice/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python lists and loops",
    "difficulty": "medium",
    "num_questions": 5
  }'
```

**Get Explanation:**
```bash
curl -X POST "http://localhost:8000/practice/explain" \
  -H "Content-Type: application/json" \
  -d '{
    "concept": "Big O notation",
    "detail_level": "medium"
  }'
```

### Step 5: Track Progress

```bash
curl -X POST "http://localhost:8000/progress/checkin" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "completed_block_ids": ["block_id_1", "block_id_2"]
  }'
```

Response:
```json
{
  "success": true,
  "message": "Great job! 6-day streak!",
  "stats": {
    "current_streak": 6,
    "task_completion_percent": 25.0,
    "completed_hours": 12.5
  },
  "badges": [
    {"name": "Week Warrior", "icon": "⭐", "description": "7-day streak!"}
  ]
}
```

## 🏗️ Project Structure

```
HackCamp/
├── app/
│   ├── main.py                 # FastAPI app
│   ├── models.py               # Pydantic schemas
│   ├── clients/
│   │   ├── ai_client.py        # OpenAI GPT-4o-mini
│   │   └── supabase.py         # Database client
│   ├── services/
│   │   ├── syllabus_extractor.py    # Vision-based extraction
│   │   ├── calendar_parser.py       # AI calendar categorization
│   │   ├── timeline_generator.py    # Smart scheduler
│   │   ├── study_coach.py           # Daily recommendations
│   │   ├── practice_generator.py    # AI practice questions
│   │   ├── tutor.py                 # AI explanations
│   │   ├── effort_estimator.py      # Task effort estimation
│   │   └── progress_tracker.py      # Streaks & stats
│   └── routes/
│       ├── syllabus.py
│       ├── calendar.py
│       ├── timeline.py
│       ├── daily.py
│       ├── practice.py
│       └── progress.py
├── requirements.txt
├── supabase_schema.sql
├── .env.example
├── .gitignore
└── README.md
```

## 🧪 Testing

### Test Health Check
```bash
curl http://localhost:8000/health
```

### Test with Example Files

Create a test syllabus (text):
```bash
curl -X POST "http://localhost:8000/syllabus/upload" \
  -F "user_id=test_user" \
  -F 'syllabus_text=Assignment 1 (15%): Due Feb 15
Midterm Exam (30%): March 10
Final Project (25%): April 20'
```

## 💰 Cost Estimation

Using GPT-4o-mini (very cheap):
- Syllabus extraction: ~$0.001 per page
- Practice questions: ~$0.0005 per generation
- Calendar categorization: ~$0.0001 per event
- Daily coaching: ~$0.0003 per message

**Estimated cost for one student for entire semester: ~$1-2**

## 🎨 Frontend Integration

The backend returns clean JSON. Example integration:

```javascript
// Upload syllabus
const formData = new FormData();
formData.append('user_id', userId);
formData.append('file', syllabusFile);

const response = await fetch('http://localhost:8000/syllabus/upload', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(`Extracted ${data.tasks_extracted} tasks!`);

// Get daily plan
const daily = await fetch(`http://localhost:8000/daily/${userId}`);
const plan = await daily.json();

console.log(plan.motivation); // Show motivational message
console.log(plan.blocks);     // Display today's study blocks
```

## 🔒 Security Notes

For MVP/Hackathon:
- RLS (Row Level Security) is disabled in Supabase for easier development
- CORS is set to allow all origins
- No authentication implemented

**Before production:**
1. Enable Supabase RLS policies
2. Add proper authentication (JWT tokens)
3. Configure CORS to allow only your frontend domain
4. Add rate limiting
5. Validate all inputs

## 🐛 Troubleshooting

**Issue**: `pdf2image` errors
**Fix**: Install Poppler (see setup instructions)

**Issue**: OpenAI API errors
**Fix**: Check your API key has credits

**Issue**: Supabase connection errors
**Fix**: Verify SUPABASE_URL and SUPABASE_KEY in .env

**Issue**: Import errors
**Fix**: Make sure you're in the project root and virtual environment is activated

## 📝 API Documentation

Once running, visit:
- **Interactive docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🚀 Deployment

### Quick Deploy to Render/Railway/Heroku

1. Push code to GitHub
2. Connect to deployment platform
3. Set environment variables
4. Deploy!

Example for Render:
```bash
# Render will auto-detect requirements.txt
# Just set env vars in Render dashboard
```

## 📞 Support

For issues or questions during hackathon:
- Check `/docs` endpoint for API details
- Review `supabase_schema.sql` for database structure
- All services have error handling with descriptive messages

## 🎉 Next Steps (Post-Hackathon)

- [ ] Add user authentication (Supabase Auth)
- [ ] Implement email/push notifications
- [ ] Add collaborative study groups
- [ ] Integrate with Google Calendar API (OAuth)
- [ ] Add mobile app support
- [ ] Implement spaced repetition algorithm
- [ ] Add voice input for questions
- [ ] Create achievement system with rewards

## 📄 License

MIT License - Build something awesome! 🚀

---

**Built for HackCamp 2024** | Powered by OpenAI GPT-4o-mini & Supabase
