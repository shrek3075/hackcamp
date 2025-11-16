# SmartPlanner - 5-Minute Quickstart 🚀

## Setup (Do This First!)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install pdf2image  # For PDF support
```

### 2. Install Poppler (for PDFs)
- **Windows**: Download from https://github.com/oschwartz10612/poppler-windows/releases/ and add to PATH
- **Mac**: `brew install poppler`
- **Linux**: `sudo apt-get install poppler-utils`

### 3. Set Up Supabase
1. Go to https://supabase.com → Create project
2. Copy `supabase_schema.sql` → Run in SQL Editor
3. Get API keys from Settings → API

### 4. Configure .env
```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=sk-your-key-here
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-key-here
```

### 5. Run Server
```bash
uvicorn app.main:app --reload
```

Server: http://localhost:8000
Docs: http://localhost:8000/docs

---

## Test Flow (Copy-Paste Commands)

### 1. Upload Syllabus (Text)
```bash
curl -X POST "http://localhost:8000/syllabus/upload" \
  -F "user_id=demo_user" \
  -F 'syllabus_text=
Assignment 1 (15%): Python basics - Due Feb 15, 2024
Midterm Exam (30%): Covers chapters 1-5 - March 10, 2024
Final Project (25%): Build a web app - April 20, 2024
Quiz 1 (5%): Loops and functions - Feb 8, 2024'
```

### 2. Upload Calendar (Create test.ics first)
Create `test.ics`:
```ics
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
DTSTART:20240201T100000Z
DTEND:20240201T110000Z
SUMMARY:CS101 Lecture
END:VEVENT
BEGIN:VEVENT
DTSTART:20240201T140000Z
DTEND:20240201T160000Z
SUMMARY:Work Shift
END:VEVENT
END:VCALENDAR
```

Upload:
```bash
curl -X POST "http://localhost:8000/calendar/upload" \
  -F "user_id=demo_user" \
  -F "file=@test.ics"
```

### 3. Generate Timeline
```bash
curl -X POST "http://localhost:8000/timeline/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
    "preferences": {
      "max_hours_per_day": 5.0,
      "preferred_start_time": "09:00",
      "preferred_end_time": "21:00"
    }
  }'
```

### 4. Get Today's Plan
```bash
curl "http://localhost:8000/daily/demo_user?user_name=Alex"
```

### 5. Generate Practice Questions
```bash
curl -X POST "http://localhost:8000/practice/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python loops and functions",
    "difficulty": "medium",
    "num_questions": 3
  }'
```

### 6. Get AI Explanation
```bash
curl -X POST "http://localhost:8000/practice/explain" \
  -H "Content-Type: application/json" \
  -d '{
    "concept": "for loops in Python",
    "detail_level": "simple"
  }'
```

### 7. Check-in (Update Streak)
```bash
curl -X POST "http://localhost:8000/progress/checkin" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
    "completed_block_ids": []
  }'
```

### 8. Get Progress Stats
```bash
curl "http://localhost:8000/progress/stats/demo_user"
```

---

## Common Issues & Fixes

**"ModuleNotFoundError: No module named 'app'"**
→ Make sure you're in the project root: `cd HackCamp`

**"OPENAI_API_KEY not found"**
→ Create `.env` file with your API key

**"Supabase connection failed"**
→ Check SUPABASE_URL and SUPABASE_KEY in `.env`

**PDF upload fails**
→ Install pdf2image and Poppler (see setup above)

**"No tasks found"**
→ Upload syllabus first before generating timeline

---

## API Endpoints Cheat Sheet

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/syllabus/upload` | POST | Upload PDF/text syllabus |
| `/calendar/upload` | POST | Upload .ics calendar |
| `/timeline/generate` | POST | Create study schedule |
| `/daily/{user_id}` | GET | Today's study plan |
| `/practice/generate` | POST | Generate practice questions |
| `/practice/explain` | POST | AI explains concept |
| `/practice/ask` | POST | Ask AI tutor |
| `/progress/checkin` | POST | Daily check-in |
| `/progress/stats/{user_id}` | GET | Progress statistics |
| `/health` | GET | Check API status |

---

## Frontend Integration Example

```javascript
// Upload syllabus
const formData = new FormData();
formData.append('user_id', 'user123');
formData.append('file', syllabusFile);

const response = await fetch('http://localhost:8000/syllabus/upload', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(`Extracted ${data.tasks_extracted} tasks!`);

// Get today's plan
const dailyResponse = await fetch('http://localhost:8000/daily/user123');
const plan = await dailyResponse.json();

// Show to user
document.getElementById('motivation').textContent = plan.motivation;
document.getElementById('streak').textContent = `${plan.streak} days`;
```

---

## Demo Script for Presentation

1. **Show health check**: Visit http://localhost:8000/health
2. **Upload syllabus**: Use curl command or Swagger UI
3. **Show extracted tasks**: Point out AI-estimated effort hours
4. **Upload calendar**: Show AI categorization (no keywords!)
5. **Generate timeline**: Show scheduled study blocks
6. **Daily plan**: Show Duolingo-style coaching message
7. **Practice questions**: Generate and show questions
8. **AI tutor**: Ask for explanation
9. **Progress tracking**: Show streak and badges

---

## Files You Need

- ✅ `requirements.txt` - All dependencies
- ✅ `supabase_schema.sql` - Database schema
- ✅ `.env` - Your API keys (create from .env.example)
- ✅ `app/` - All backend code
- ✅ `README.md` - Full documentation

---

## Quick Deploy (After Hackathon)

**Render.com**:
1. Connect GitHub repo
2. Set environment variables
3. Deploy! (auto-detects requirements.txt)

**Railway**:
```bash
railway login
railway link
railway up
```

---

## Cost Breakdown

**OpenAI GPT-4o-mini costs** (very cheap):
- Input: $0.15 / 1M tokens
- Output: $0.60 / 1M tokens

**Typical request costs**:
- Syllabus extraction (10 pages): ~$0.005
- Practice questions (5 questions): ~$0.001
- Daily coaching message: ~$0.0003
- Calendar categorization (100 events): ~$0.01

**Total for one student per semester**: ~$2-3

---

**Need help? Check:**
- Full docs: http://localhost:8000/docs
- README.md for detailed info
- Supabase dashboard for database issues

Good luck with your hackathon! 🚀
