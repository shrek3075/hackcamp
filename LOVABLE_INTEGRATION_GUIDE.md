# Connecting Lovable Frontend to SmartPlanner Backend

## 🚀 Quick Start (5 Minutes)

### Step 1: Make Sure Backend is Running

```bash
cd C:\Users\shrey\Downloads\HackCamp
python -m uvicorn app.main:app --reload
```

**Server will be at**: `http://localhost:8000`

**Test it's working**: Open `http://localhost:8000/docs` in browser

---

### Step 2: Create API Client in Lovable

In your Lovable project, create a new file called `api.ts` or `api.js`:

```typescript
// api.ts - SmartPlanner API Client

const API_BASE_URL = 'http://localhost:8000';

// Helper function for all API calls
async function apiCall(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API request failed');
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// ============== DEMO ENDPOINTS ==============

export async function seedDemoData(userId: string = 'demo_user') {
  return apiCall('/demo/seed', {
    method: 'POST',
    body: JSON.stringify({
      user_id: userId,
      exam_name: 'World War II Midterm',
    }),
  });
}

export async function getDashboard(userId: string) {
  return apiCall(`/demo/dashboard/${userId}`);
}

export async function resetUser(userId: string) {
  return apiCall(`/demo/reset/${userId}`, {
    method: 'DELETE',
  });
}

// ============== CORE FEATURES ==============

export async function getTodaysPlan(userId: string, userName?: string) {
  const query = userName ? `?user_name=${userName}` : '';
  return apiCall(`/daily/${userId}${query}`);
}

export async function generatePracticeQuestions(params: {
  topic: string;
  difficulty?: 'easy' | 'medium' | 'hard';
  num_questions?: number;
  question_type?: 'multiple_choice' | 'short_answer' | 'mixed';
}) {
  return apiCall('/practice/generate', {
    method: 'POST',
    body: JSON.stringify({
      difficulty: 'medium',
      num_questions: 5,
      question_type: 'multiple_choice',
      ...params,
    }),
  });
}

export async function chatWithTutor(params: {
  user_id: string;
  message: string;
  conversation_history?: Array<{ role: string; content: string }>;
}) {
  return apiCall('/tutor/chat', {
    method: 'POST',
    body: JSON.stringify({
      conversation_history: [],
      ...params,
    }),
  });
}

export async function markProgress(userId: string, completedBlockIds: string[] = []) {
  return apiCall('/progress/checkin', {
    method: 'POST',
    body: JSON.stringify({
      user_id: userId,
      completed_block_ids: completedBlockIds,
    }),
  });
}

export async function getProgressStats(userId: string) {
  return apiCall(`/progress/${userId}`);
}

// ============== FILE UPLOAD ==============

export async function uploadStudyMaterials(params: {
  user_id: string;
  files?: File[];
  syllabus_text?: string;
  grade_level?: string;
  exam_date?: string;
  exam_weight?: number;
  hours_per_day?: number;
  study_depth?: 'basic' | 'standard' | 'comprehensive';
}) {
  const formData = new FormData();

  formData.append('user_id', params.user_id);
  formData.append('grade_level', params.grade_level || 'high_school');
  formData.append('study_depth', params.study_depth || 'standard');
  formData.append('generate_quiz', 'false');

  if (params.exam_date) formData.append('exam_date', params.exam_date);
  if (params.exam_weight) formData.append('exam_weight', params.exam_weight.toString());
  if (params.hours_per_day) formData.append('hours_per_day', params.hours_per_day.toString());

  if (params.files && params.files.length > 0) {
    params.files.forEach(file => {
      formData.append('files', file);
    });
  } else if (params.syllabus_text) {
    formData.append('syllabus_text', params.syllabus_text);
  }

  const response = await fetch(`${API_BASE_URL}/syllabus/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Upload failed');
  }

  return await response.json();
}

export async function uploadCalendar(params: {
  user_id: string;
  file: File;
  exam_date?: string;
  preferred_study_start?: number;
  preferred_study_end?: number;
}) {
  const formData = new FormData();

  formData.append('user_id', params.user_id);
  formData.append('file', params.file);

  if (params.exam_date) formData.append('exam_date', params.exam_date);
  if (params.preferred_study_start) formData.append('preferred_study_start', params.preferred_study_start.toString());
  if (params.preferred_study_end) formData.append('preferred_study_end', params.preferred_study_end.toString());

  const response = await fetch(`${API_BASE_URL}/calendar/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Calendar upload failed');
  }

  return await response.json();
}

// ============== TIMELINE ==============

export async function generateTimeline(userId: string) {
  return apiCall('/timeline/generate', {
    method: 'POST',
    body: JSON.stringify({ user_id: userId }),
  });
}
```

---

### Step 3: Use in Your React Components

#### Example 1: Dashboard/Home Page

```typescript
// Dashboard.tsx
import { useEffect, useState } from 'react';
import { getDashboard, seedDemoData } from './api';

export function Dashboard() {
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const userId = 'demo_user'; // Get from auth/context later

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      setLoading(true);
      const data = await getDashboard(userId);
      setDashboard(data);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
      // If no data, seed demo data
      await seedDemoData(userId);
      const data = await getDashboard(userId);
      setDashboard(data);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div>Loading...</div>;
  if (!dashboard) return <div>No data</div>;

  return (
    <div className="dashboard">
      <h1>Welcome back! 🎓</h1>

      {/* Streak Display */}
      <div className="streak-card">
        <h2>🔥 {dashboard.progress.current_streak} Day Streak!</h2>
        <p>{dashboard.motivational_message}</p>
      </div>

      {/* Exam Countdown */}
      {dashboard.exam && (
        <div className="exam-card">
          <h3>{dashboard.exam.name}</h3>
          <p>{dashboard.exam.days_until} days until exam</p>
          <p>Date: {dashboard.exam.date}</p>
        </div>
      )}

      {/* Progress */}
      <div className="progress-card">
        <h3>Your Progress</h3>
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${dashboard.progress.progress_percent}%` }}
          />
        </div>
        <p>{dashboard.progress.completed_tasks} / {dashboard.progress.total_tasks} tasks completed</p>
      </div>

      {/* Today's Tasks */}
      <button onClick={() => window.location.href = '/today'}>
        Start Today's Study Session →
      </button>
    </div>
  );
}
```

#### Example 2: Today's Study Page

```typescript
// TodayPage.tsx
import { useEffect, useState } from 'react';
import { getTodaysPlan, markProgress } from './api';

export function TodayPage() {
  const [plan, setPlan] = useState<any>(null);
  const userId = 'demo_user';

  useEffect(() => {
    loadTodaysPlan();
  }, []);

  async function loadTodaysPlan() {
    const data = await getTodaysPlan(userId, 'Student');
    setPlan(data);
  }

  async function completeToday() {
    await markProgress(userId);
    alert('Great job! Streak updated! 🔥');
    loadTodaysPlan(); // Refresh
  }

  if (!plan) return <div>Loading...</div>;

  return (
    <div className="today-page">
      <h1>Today's Study Plan</h1>
      <p>{plan.motivational_message}</p>

      <div className="tasks-list">
        {plan.todays_tasks?.map((task: any, idx: number) => (
          <div key={idx} className="task-card">
            <h3>{task.topic}</h3>
            <p>⏰ {task.time}</p>
            <p>📚 {task.hours}h</p>
          </div>
        ))}
      </div>

      <button onClick={completeToday}>
        ✅ Mark Today Complete
      </button>
    </div>
  );
}
```

#### Example 3: Practice Questions Page

```typescript
// PracticePage.tsx
import { useState } from 'react';
import { generatePracticeQuestions } from './api';

export function PracticePage() {
  const [questions, setQuestions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [showResult, setShowResult] = useState(false);

  async function loadQuestions(topic: string) {
    setLoading(true);
    try {
      const data = await generatePracticeQuestions({
        topic,
        difficulty: 'medium',
        num_questions: 5,
      });
      setQuestions(data.questions || []);
      setCurrentQuestion(0);
    } finally {
      setLoading(false);
    }
  }

  function checkAnswer() {
    setShowResult(true);
  }

  function nextQuestion() {
    setCurrentQuestion(prev => prev + 1);
    setSelectedAnswer('');
    setShowResult(false);
  }

  if (loading) return <div>Generating questions...</div>;
  if (questions.length === 0) {
    return (
      <div>
        <h1>Practice Questions</h1>
        <button onClick={() => loadQuestions('Causes of World War II')}>
          Start Practice
        </button>
      </div>
    );
  }

  const q = questions[currentQuestion];
  const isCorrect = selectedAnswer === q.correct_answer;

  return (
    <div className="practice-page">
      <h2>Question {currentQuestion + 1} / {questions.length}</h2>

      <div className="question-card">
        <h3>{q.question}</h3>

        <div className="options">
          {Object.entries(q.options).map(([key, value]: [string, any]) => (
            <button
              key={key}
              className={`option ${selectedAnswer === key ? 'selected' : ''}`}
              onClick={() => setSelectedAnswer(key)}
              disabled={showResult}
            >
              {key}. {value}
            </button>
          ))}
        </div>

        {!showResult && selectedAnswer && (
          <button onClick={checkAnswer}>Check Answer</button>
        )}

        {showResult && (
          <div className={`result ${isCorrect ? 'correct' : 'incorrect'}`}>
            <h4>{isCorrect ? '✅ Correct!' : '❌ Incorrect'}</h4>
            <p>{q.explanation}</p>
            {currentQuestion < questions.length - 1 && (
              <button onClick={nextQuestion}>Next Question →</button>
            )}
            {currentQuestion === questions.length - 1 && (
              <button onClick={() => window.location.href = '/dashboard'}>
                Finish Practice
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
```

#### Example 4: AI Tutor Chat

```typescript
// TutorPage.tsx
import { useState } from 'react';
import { chatWithTutor } from './api';

export function TutorPage() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const userId = 'demo_user';

  async function sendMessage() {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await chatWithTutor({
        user_id: userId,
        message: input,
        conversation_history: messages,
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.message,
        topics: response.referenced_topics,
        followups: response.suggested_followups,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="tutor-page">
      <h1>🧠 AI Study Tutor</h1>

      <div className="chat-container">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <p>{msg.content}</p>
            {msg.topics && (
              <div className="topics">
                📚 Topics: {msg.topics.join(', ')}
              </div>
            )}
          </div>
        ))}
        {loading && <div className="message assistant">Thinking...</div>}
      </div>

      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask me anything about your study materials..."
        />
        <button onClick={sendMessage} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
}
```

---

## 🔧 Common Issues & Solutions

### Issue 1: CORS Errors

**Error**: `Access to fetch at 'http://localhost:8000' has been blocked by CORS policy`

**Solution**: Already fixed! Backend has CORS enabled. If you still see this:
1. Make sure backend is running
2. Clear browser cache
3. Use `http://localhost:8000` not `http://127.0.0.1:8000`

### Issue 2: "Cannot reach server"

**Check**:
```bash
# Test if server is running
curl http://localhost:8000/

# Should return: {"message":"Welcome to SmartPlanner API!",...}
```

### Issue 3: 404 Not Found on endpoints

**Solution**: Make sure you're using the correct endpoint paths:
- ✅ `/demo/dashboard/demo_user`
- ❌ `/dashboard/demo_user`

### Issue 4: Need to change API URL for production

```typescript
// In api.ts, change:
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Then in .env:
VITE_API_URL=https://your-backend.com
```

---

## 🎯 Recommended Integration Order

1. **Day 1 (Now - 2 hours)**:
   - Copy `api.ts` into Lovable
   - Create Dashboard component
   - Call `seedDemoData()` and `getDashboard()`
   - Display streak, progress, exam countdown

2. **Day 1 (2-4 hours)**:
   - Add Today's Study page
   - Show today's tasks
   - Add "Mark Complete" button

3. **Day 1 (4-6 hours)**:
   - Add Practice Questions page
   - Interactive quiz with check answers
   - Show correct/incorrect feedback

4. **Day 1 (6-8 hours)**:
   - Polish UI
   - Add loading states
   - Add error handling
   - Test user flow

5. **Optional (if time)**:
   - AI Tutor chat
   - File upload
   - Calendar integration

---

## 💡 Pro Tips

1. **Start with demo data**: Always call `seedDemoData()` first to test
2. **One user for demo**: Use `'demo_user'` everywhere for now
3. **Check Network tab**: F12 → Network to debug API calls
4. **Use React Query**: For better state management (optional)
5. **Mobile first**: Make it work on phone screens

---

## 🚀 Quick Test

Run this in your browser console to test backend:

```javascript
// Test backend connection
fetch('http://localhost:8000/')
  .then(r => r.json())
  .then(console.log);

// Seed demo data
fetch('http://localhost:8000/demo/seed', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_id: 'demo_user' })
})
  .then(r => r.json())
  .then(console.log);

// Get dashboard
fetch('http://localhost:8000/demo/dashboard/demo_user')
  .then(r => r.json())
  .then(console.log);
```

---

**You're ready to connect! Start with the Dashboard component and go from there.** 🎓
