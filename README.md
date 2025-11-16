# SmartPlanner - AI-Powered Study Planning Platform

**Transform your study chaos into an organized, intelligent learning journey**

A comprehensive full-stack study planning application that uses AI to extract syllabus content, generate personalized study schedules, create practice quizzes, and provide 24/7 AI tutoring with smart scheduling that respects your busy days.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Key Features Deep Dive](#key-features-deep-dive)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [Cost & Performance](#cost--performance)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

---

## Features

### AI-Powered Intelligence
- **Vision-Based Content Extraction** - Upload PDF syllabi, images, or PowerPoint slides and let AI extract topics, assignments, and learning objectives
- **AI Study Plan Generation** - Gemini 2.5 Flash creates personalized day-by-day study plans based on your syllabus
- **AI Tutor Chat** - 24/7 conversational AI tutor powered by GPT-4o-mini for concept explanations and study guidance
- **Intelligent Quiz Generation** - AI creates practice quizzes based on your notes and study materials

### Study Tools
- **Interactive Quiz Game** - Gamified quiz interface with score tracking and immediate feedback
- **Notes Management** - Create, edit, and organize study notes with tags and categories
- **Topic Mindmap** - Visual flowchart of your study topics with achievement tracking
- **Progress Dashboard** - Track completion rates, study hours, and achievements
- **Multi-Subject Support** - Manage multiple study plans simultaneously

### Smart Scheduling
- **Busy Day Management** - Mark specific days as unavailable (e.g., Mondays, Fridays)
- **Flexible Study Hours** - Set total study hours and let AI distribute them optimally
- **Spaced Repetition** - Built-in review sessions before exams

---

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for blazing-fast builds
- **Tailwind CSS** for modern, responsive UI
- **shadcn/ui** component library
- **React Router** for navigation
- **Supabase Client** for real-time data
- **React Markdown** for formatted AI responses
- **PDF.js** for PDF parsing

### Backend
- **FastAPI** (Python) for high-performance API
- **OpenAI GPT-4o-mini** for vision and text AI
- **Supabase** (PostgreSQL) for database
- **Uvicorn** ASGI server

### AI & Cloud Services
- **Supabase Edge Functions** (Deno) for serverless AI processing
- **Gemini 2.5 Flash** for study plan generation
- **GPT-4o-mini** for content extraction and tutoring
- **Lovable AI Gateway** for AI orchestration

---

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- OpenAI API key
- Supabase account with Lovable API key configured

### 1. Clone Repository
```bash
git clone https://github.com/shrek3075/hackcamp.git
cd hackcamp
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your OpenAI and Supabase credentials

# Run backend server
python -m uvicorn app.main:app --reload
# Server starts at http://localhost:8000
```

### 3. Frontend Setup
```bash
cd frontend/study-planner-pro

# Install dependencies
npm install

# Run development server
npm run dev
# Frontend starts at http://localhost:5173
```

### 4. Access Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Detailed Setup

### Backend Configuration

#### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

**For PDF support:**
```bash
pip install pdf2image
```

**Install Poppler** (required for pdf2image):
- **Windows**: Download from [poppler-windows releases](https://github.com/oschwartz10612/poppler-windows/releases/)
- **Mac**: `brew install poppler`
- **Linux**: `sudo apt-get install poppler-utils`

#### 2. Set Up Supabase Database
1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Create a new project
3. Go to SQL Editor
4. Run the SQL from `supabase_schema.sql`
5. Get your API keys from Settings → API

#### 3. Configure Environment Variables
Create `.env` file:
```env
OPENAI_API_KEY=sk-your-openai-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

#### 4. Deploy Supabase Edge Functions
```bash
cd frontend/study-planner-pro

# Install Supabase CLI
npm install -g supabase

# Login to Supabase
supabase login

# Link project
supabase link --project-ref your-project-ref

# Deploy functions
npx supabase functions deploy generate-study-plan
npx supabase functions deploy generate-quiz
npx supabase functions deploy generate-study-recommendations
```

**Set Lovable API Key** in Supabase:
```bash
supabase secrets set LOVABLE_API_KEY=your-lovable-api-key
```

### Frontend Configuration

#### 1. Install Dependencies
```bash
cd frontend/study-planner-pro
npm install
```

#### 2. Configure Supabase
Update `src/integrations/supabase/client.ts` with your Supabase credentials (if not using environment variables).

#### 3. Run Development Server
```bash
npm run dev
```

---

## Key Features Deep Dive

### 1. Calendar Integration

Upload your `.ics` calendar file to get intelligent study scheduling:

**Features:**
- Parses calendar events for the next 60 days
- Calculates free time slots with 15-minute buffers
- Prioritizes earlier study times
- Avoids scheduling conflicts
- Shows available time slots per day

**How it works:**
1. Upload calendar on Details page
2. Set study time window (default: 3:15 PM - 10:00 PM)
3. Mark busy days (e.g., Mondays, Fridays)
4. Generate study plan
5. View specific time recommendations for each session

### 2. AI Study Plan Generation

Powered by Gemini 2.5 Flash for comprehensive planning:

**Input:**
- Subject name
- Test date
- Syllabus content (PDF, text, or extracted)
- Calendar events (optional)
- Study time preferences
- Busy days

**Output:**
- Day-by-day study schedule
- Specific topics per session
- Suggested time ranges
- Session duration and priority
- Daily goals and milestones
- Total hours calculation

**Smart Features:**
- Respects calendar conflicts
- Distributes topics evenly
- Includes review sessions
- Calculates actual day of week
- Skips busy days

### 3. AI Tutor

24/7 conversational AI assistant:

**Capabilities:**
- Explain complex concepts
- Answer study questions
- Provide learning strategies
- Context-aware (knows your study plan)
- Markdown-formatted responses
- Real-time chat interface

**Technologies:**
- GPT-4o-mini for natural conversations
- React Markdown for beautiful formatting
- Study plan context integration

### 4. Quiz System

Two-part quiz functionality:

**A. AI Quiz Generation**
- Generates quizzes from your notes
- 5 questions per quiz
- Multiple choice, true/false, fill-in-blank
- Difficulty levels: easy, medium, hard
- Explanations for each answer

**B. Interactive Quiz Game**
- Full-screen quiz interface
- Score tracking
- Timed sessions
- Immediate feedback
- Achievement system

### 5. Progress Tracking

Comprehensive progress monitoring:

**Metrics:**
- Session completion percentage
- Study hours logged
- Topics mastered
- Daily streak tracking
- Achievement badges

**Views:**
- Progress dashboard with charts
- Mindmap with topic checkboxes
- Study plan with completion status
- History of past study plans

### 6. Mindmap Visualization

Visual representation of study topics:

**Features:**
- Hierarchical topic structure
- Main topics with subtopics
- Progress indicator
- Checkbox achievements
- Color-coded completion
- Connection lines showing relationships

---

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
│  ┌─────────┐  ┌──────────┐  ┌────────┐  ┌───────────┐ │
│  │ Details │  │   Plan   │  │ Tutor  │  │  Progress │ │
│  │  Page   │  │   Page   │  │  Chat  │  │  Tracker  │ │
│  └─────────┘  └──────────┘  └────────┘  └───────────┘ │
│                           │                              │
│                           ▼                              │
│                  Supabase Client                         │
└───────────────────────────┬─────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
    ┌──────────────────┐    ┌──────────────────┐
    │  Supabase Edge   │    │  FastAPI Backend │
    │    Functions     │    │     (Python)     │
    │                  │    │                  │
    │ • Study Plans    │    │ • Syllabus Parse │
    │ • Quiz Gen       │    │ • Timeline Gen   │
    │ • Mindmap Gen    │    │ • Progress API   │
    └────────┬─────────┘    └────────┬─────────┘
             │                       │
             ▼                       ▼
    ┌────────────────┐      ┌────────────────┐
    │  Gemini 2.5    │      │  OpenAI GPT-4o │
    │     Flash      │      │      mini      │
    └────────────────┘      └────────────────┘
                │
                ▼
        ┌───────────────┐
        │   Supabase    │
        │  PostgreSQL   │
        └───────────────┘
```

### Data Flow

**Study Plan Creation:**
1. User uploads syllabus + calendar on Details page
2. Frontend parses calendar with ical.js
3. Calculates free time slots with buffers
4. Sends to Supabase Edge Function `generate-study-plan`
5. Edge Function calls Gemini 2.5 Flash with structured prompt
6. AI generates day-by-day plan with specific times
7. Plan saved to Supabase database
8. Frontend displays plan on Plan page

**Quiz Generation:**
1. User creates notes in NotesView
2. Notes synced to localStorage and database
3. User clicks "Generate Quiz"
4. Frontend calls `generate-quiz` Edge Function
5. AI analyzes notes and creates questions
6. Quiz displayed in game interface

**AI Tutor:**
1. User sends message in Tutor chat
2. Frontend includes study plan context
3. Request sent to GPT-4o-mini via Edge Function
4. AI responds with context-aware advice
5. Response rendered with ReactMarkdown

---

## API Documentation

### Backend API Endpoints (FastAPI - Port 8000)

#### Syllabus Management
- `POST /syllabus/upload` - Upload syllabus (PDF, image, text)
- `GET /syllabus/tasks/{user_id}` - Get extracted tasks

#### Calendar
- `POST /calendar/upload` - Upload .ics calendar
- `GET /calendar/busy-blocks/{user_id}` - Get busy time blocks

#### Timeline Generation
- `POST /timeline/generate` - Generate study timeline
- `GET /timeline/{plan_id}` - Get specific timeline
- `GET /timeline/latest/{user_id}` - Get latest timeline

#### Progress Tracking
- `POST /progress/checkin` - Daily check-in
- `GET /progress/stats/{user_id}` - Get progress stats
- `POST /progress/task/{task_id}/complete` - Mark task complete

#### Practice & Tutoring
- `POST /practice/generate` - Generate practice questions
- `POST /practice/explain` - AI explains concept
- `POST /practice/ask` - Ask AI tutor

#### Configuration
- `POST /config/semester` - Set semester dates
- `GET /config/semester/{user_id}` - Get semester config

### Supabase Edge Functions (Port 54321)

#### Study Plan Generation
**Endpoint:** `POST /functions/v1/generate-study-plan`

**Request:**
```json
{
  "subject": "Physics 101",
  "testDate": "2025-12-15",
  "startDate": "2025-11-16",
  "busyDays": ["Monday", "Friday"],
  "totalStudyHours": 40,
  "syllabusContent": "...",
  "calendarEvents": [...],
  "studyTimeWindow": {
    "startTime": "15:15",
    "endTime": "22:00"
  },
  "dailyFreeSlots": {
    "2025-11-16": ["15:15 - 18:00", "19:00 - 22:00"]
  }
}
```

**Response:**
```json
{
  "studyPlan": {
    "totalDays": 20,
    "totalHours": 40,
    "dailyPlans": [
      {
        "day": 1,
        "date": "2025-11-16",
        "dayOfWeek": "Saturday",
        "totalStudyHours": 2,
        "sessions": [
          {
            "topic": "Newton's Laws",
            "duration": 1,
            "description": "Study fundamental concepts",
            "priority": "high",
            "suggestedTime": "15:15 - 16:15"
          }
        ],
        "goals": "Master basic mechanics",
        "freeTimeSlots": ["15:15 - 18:00", "19:00 - 22:00"]
      }
    ],
    "summary": "Comprehensive physics study plan"
  }
}
```

#### Quiz Generation
**Endpoint:** `POST /functions/v1/generate-quiz`

**Request:**
```json
{
  "notes": [
    {
      "title": "Newton's Laws",
      "content": "First law: Object in motion..."
    }
  ],
  "difficulty": "medium"
}
```

**Response:**
```json
{
  "questions": [
    {
      "type": "multiple_choice",
      "question": "What is Newton's First Law?",
      "options": ["A", "B", "C", "D"],
      "correctAnswer": 0,
      "explanation": "..."
    }
  ]
}
```

#### Mindmap Generation
**Endpoint:** `POST /functions/v1/generate-study-recommendations`

**Request:**
```json
{
  "subject": "Physics 101",
  "syllabusContent": "...",
  "type": "flowchart"
}
```

**Response:**
```json
{
  "flowchart": {
    "subject": "Physics 101",
    "mainTopics": [
      {
        "name": "Mechanics",
        "subtopics": ["Kinematics", "Dynamics", "Energy"],
        "description": "Study of motion and forces"
      }
    ],
    "summary": "Physics topic structure"
  }
}
```

---

## Project Structure

```
HackCamp/
├── app/                                    # FastAPI Backend
│   ├── main.py                            # Main application
│   ├── models.py                          # Pydantic schemas
│   ├── clients/
│   │   ├── ai_client.py                  # OpenAI client
│   │   └── supabase.py                   # Supabase client
│   ├── services/
│   │   ├── syllabus_extractor.py         # Vision-based extraction
│   │   ├── calendar_parser.py            # Calendar AI categorization
│   │   ├── timeline_generator.py         # Smart scheduler
│   │   ├── effort_estimator.py           # Task effort estimation
│   │   ├── quiz_generator.py             # Quiz generation
│   │   └── study_schedule_generator.py   # Study scheduling
│   └── routes/
│       ├── syllabus.py
│       ├── calendar.py
│       ├── timeline.py
│       ├── config.py
│       └── tutor.py
│
├── frontend/study-planner-pro/            # React Frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Auth.tsx                  # Authentication
│   │   │   ├── Details.tsx               # Study plan creation
│   │   │   ├── Plan.tsx                  # Study plan view
│   │   │   ├── Mindmap.tsx               # Topic visualization
│   │   │   ├── Progress.tsx              # Progress tracking
│   │   │   ├── AITutor.tsx               # AI chat interface
│   │   │   ├── QuizGame.tsx              # Interactive quiz
│   │   │   └── History.tsx               # Past plans
│   │   ├── components/
│   │   │   ├── ui/                       # shadcn/ui components
│   │   │   └── NotesView.tsx             # Notes management
│   │   └── integrations/
│   │       └── supabase/
│   │           └── client.ts             # Supabase client
│   │
│   ├── supabase/functions/               # Edge Functions
│   │   ├── generate-study-plan/
│   │   │   └── index.ts                  # Study plan AI
│   │   ├── generate-quiz/
│   │   │   └── index.ts                  # Quiz AI
│   │   └── generate-study-recommendations/
│   │       └── index.ts                  # Mindmap AI
│   │
│   ├── package.json
│   └── vite.config.ts
│
├── requirements.txt                       # Python dependencies
├── supabase_schema.sql                    # Database schema
├── .env.example                           # Environment template
├── COMPREHENSIVE_FEATURES.md              # Feature documentation
├── QUICKSTART.md                          # Quick start guide
└── README.md                              # This file
```

---

## Screenshots

### Study Plan Creation
![Details Page](docs/screenshots/details-page.png)
*Upload syllabus, configure calendar, and set study preferences*

### AI-Generated Study Plan
![Study Plan](docs/screenshots/study-plan.png)
*Day-by-day schedule with specific time recommendations*

### Topic Mindmap
![Mindmap](docs/screenshots/mindmap.png)
*Visual representation of study topics with progress tracking*

### AI Tutor Chat
![AI Tutor](docs/screenshots/ai-tutor.png)
*24/7 AI assistance with beautiful markdown formatting*

### Quiz Game
![Quiz Game](docs/screenshots/quiz-game.png)
*Interactive quiz interface with score tracking*

### Progress Dashboard
![Progress](docs/screenshots/progress.png)
*Track completion rates and study hours*

---

## Cost & Performance

### AI Cost Estimation (per student per semester)

**Backend (GPT-4o-mini):**
- Syllabus extraction: ~$0.001 per page
- Calendar categorization: ~$0.0001 per event
- Content analysis: ~$0.002 per document

**Edge Functions (Gemini 2.5 Flash):**
- Study plan generation: ~$0.0005 per plan
- Quiz generation: ~$0.0003 per quiz
- Mindmap generation: ~$0.0002 per mindmap

**Total estimated cost: $1-3 per student per semester**

### Performance Metrics

**Response Times:**
- Syllabus upload: 3-8 seconds
- Study plan generation: 4-10 seconds
- Quiz generation: 2-4 seconds
- AI tutor response: 1-3 seconds
- Calendar parsing: <1 second

**Concurrent Users:**
- FastAPI: 100+ concurrent requests
- Supabase: Scales automatically
- Edge Functions: Serverless scaling

---

## Future Enhancements

### Short-term (Next Sprint)
- [ ] Mobile responsive improvements
- [ ] Export study plan to PDF/iCal
- [ ] Email/push notifications
- [ ] Spaced repetition algorithm refinement
- [ ] Study session timer with breaks

### Medium-term
- [ ] Google Calendar OAuth integration
- [ ] Collaborative study groups
- [ ] Flashcard generation from notes
- [ ] Voice input for AI tutor
- [ ] Study resource recommendations
- [ ] Achievement system with rewards

### Long-term
- [ ] Mobile app (React Native)
- [ ] Chrome extension for quick access
- [ ] Video lecture integration
- [ ] Peer tutoring marketplace
- [ ] Analytics dashboard for educators
- [ ] Integration with LMS platforms

---

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow existing code style
- Add tests for new features
- Update documentation
- Keep commits atomic and descriptive

---

## Troubleshooting

### Backend Issues

**Issue:** `pdf2image` errors
**Fix:** Install Poppler (see setup instructions)

**Issue:** OpenAI API errors
**Fix:** Check API key has credits at https://platform.openai.com/usage

**Issue:** Supabase connection errors
**Fix:** Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`

### Frontend Issues

**Issue:** Supabase functions not found
**Fix:** Deploy edge functions with `npx supabase functions deploy`

**Issue:** LOVABLE_API_KEY errors
**Fix:** Set secret with `supabase secrets set LOVABLE_API_KEY=your-key`

**Issue:** Calendar upload fails
**Fix:** Ensure .ics file is valid format

### General Issues

**Issue:** CORS errors
**Fix:** Check backend is running on correct port (8000)

**Issue:** Authentication errors
**Fix:** Clear browser cache and re-authenticate

---

## Security Notes

**Current Status (MVP/Hackathon):**
- RLS disabled in Supabase for easier development
- CORS allows all origins
- No rate limiting implemented

**Before Production:**
1. Enable Supabase Row Level Security (RLS)
2. Implement JWT authentication
3. Configure CORS for specific domains
4. Add rate limiting middleware
5. Input validation and sanitization
6. API key rotation policy
7. Audit logging

---

## License

MIT License - See [LICENSE](LICENSE) file for details

---

## Acknowledgments

- **OpenAI** for GPT-4o-mini API
- **Google** for Gemini 2.5 Flash
- **Supabase** for backend infrastructure
- **Lovable** for AI gateway
- **shadcn/ui** for beautiful components
- **HackCamp 2024** for the inspiration

---

## Contact & Support

**Project Repository:** https://github.com/shrek3075/hackcamp

**For Issues:**
- Check the [GitHub Issues](https://github.com/shrek3075/hackcamp/issues)
- Review API docs at http://localhost:8000/docs
- Check Supabase logs in dashboard

**Demo Video:** [Coming Soon]

---

**Built with by HackCamp Team** | Powered by AI
