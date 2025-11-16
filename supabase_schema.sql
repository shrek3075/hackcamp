-- SmartPlanner Database Schema for Supabase
-- Run this in Supabase SQL Editor to create all tables

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tasks table (from syllabus)
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    due_date TEXT,  -- ISO format or null
    task_type TEXT NOT NULL,  -- assignment, exam, project, quiz, reading, other
    weight FLOAT,  -- percentage (e.g., 15.0 = 15%)
    notes TEXT,
    effort_hours FLOAT,  -- AI-estimated effort
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Busy blocks table (from calendar)
CREATE TABLE IF NOT EXISTS busy_blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    start TIMESTAMP WITH TIME ZONE NOT NULL,
    end TIMESTAMP WITH TIME ZONE NOT NULL,
    block_type TEXT NOT NULL,  -- class, work, personal, study, other
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Study plans/timelines table
CREATE TABLE IF NOT EXISTS plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    blocks JSONB NOT NULL,  -- Array of schedule blocks
    version INTEGER DEFAULT 1
);

-- Study blocks table (from generated timeline)
CREATE TABLE IF NOT EXISTS study_blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES plans(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    task_title TEXT NOT NULL,
    scheduled_start TIMESTAMP WITH TIME ZONE NOT NULL,
    scheduled_end TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_hours FLOAT NOT NULL,
    reason TEXT,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Daily check-ins table (for streaks)
CREATE TABLE IF NOT EXISTS daily_checkins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    completed BOOLEAN DEFAULT TRUE,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- Progress tracking table
CREATE TABLE IF NOT EXISTS progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    streak_days INTEGER DEFAULT 0,
    total_hours FLOAT DEFAULT 0,
    last_checkin DATE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    max_hours_per_day FLOAT DEFAULT 6.0,
    preferred_start_time TEXT DEFAULT '09:00',
    preferred_end_time TEXT DEFAULT '22:00',
    break_duration_minutes INTEGER DEFAULT 15,
    min_study_block_minutes INTEGER DEFAULT 30,
    days_to_plan INTEGER DEFAULT 10,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);

CREATE INDEX IF NOT EXISTS idx_busy_blocks_user_id ON busy_blocks(user_id);
CREATE INDEX IF NOT EXISTS idx_busy_blocks_start ON busy_blocks(start);

CREATE INDEX IF NOT EXISTS idx_plans_user_id ON plans(user_id);
CREATE INDEX IF NOT EXISTS idx_plans_generated_at ON plans(generated_at DESC);

CREATE INDEX IF NOT EXISTS idx_study_blocks_user_id ON study_blocks(user_id);
CREATE INDEX IF NOT EXISTS idx_study_blocks_task_id ON study_blocks(task_id);
CREATE INDEX IF NOT EXISTS idx_study_blocks_scheduled_start ON study_blocks(scheduled_start);

CREATE INDEX IF NOT EXISTS idx_daily_checkins_user_id ON daily_checkins(user_id);
CREATE INDEX IF NOT EXISTS idx_daily_checkins_date ON daily_checkins(date DESC);

-- Row Level Security (RLS) - Enable for production
-- For hackathon/MVP, you can disable RLS or set simple policies

-- Example RLS policies (uncomment for production):
-- ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Users can view their own tasks" ON tasks FOR SELECT USING (auth.uid() = user_id);
-- CREATE POLICY "Users can insert their own tasks" ON tasks FOR INSERT WITH CHECK (auth.uid() = user_id);
-- (Repeat for other tables)

-- For MVP/hackathon: Keep RLS disabled for easier development
-- Enable and configure properly before deploying to production!
