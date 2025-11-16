"""
SmartPlanner Backend - AI-Powered Study Planning API

Duolingo-style study app with:
- Syllabus extraction (vision-based)
- Calendar integration
- AI study timeline generation
- Daily study coach
- Practice questions & tutoring
- Progress tracking & gamification
"""
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from dateutil import tz

# Load environment variables from .env file
load_dotenv()

# Verify API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    print("WARNING: OPENAI_API_KEY not found in environment!")
else:
    print("SUCCESS: OpenAI API Key loaded successfully")

from app.routes import syllabus, calendar, timeline, daily, practice, progress
from app.models import HealthResponse

# Create FastAPI app
app = FastAPI(
    title="SmartPlanner API",
    description="AI-powered study planning and coaching platform",
    version="1.0.0"
)

# CORS middleware (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(syllabus.router)
app.include_router(calendar.router)
app.include_router(timeline.router)
app.include_router(daily.router)
app.include_router(practice.router)
app.include_router(progress.router)


@app.get("/", tags=["root"])
async def root():
    """API root - welcome message"""
    return {
        "message": "Welcome to SmartPlanner API!",
        "docs": "/docs",
        "version": "1.0.0",
        "features": [
            "Syllabus extraction (PDF/image vision)",
            "Calendar integration (.ics)",
            "AI study timeline generation",
            "Daily study recommendations",
            "Practice question generation",
            "AI tutoring & explanations",
            "Progress tracking & streaks"
        ]
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """
    Health check endpoint

    Returns API status and service availability
    """
    services = {}

    # Check OpenAI API
    try:
        from app.clients.ai_client import get_ai_client
        ai_client = get_ai_client()
        services["openai"] = "connected"
    except Exception as e:
        services["openai"] = f"error: {str(e)}"

    # Check Supabase
    try:
        from app.clients.supabase import get_supabase_client
        db = get_supabase_client()
        services["supabase"] = "connected"
    except Exception as e:
        services["supabase"] = f"error: {str(e)}"

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(tz=tz.UTC),
        services=services
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
