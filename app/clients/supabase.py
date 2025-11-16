"""
Supabase client for database operations
"""
import os
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from datetime import datetime


class SupabaseClient:
    """Wrapper for Supabase database operations"""

    def __init__(self, url: str = None, key: str = None):
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_KEY")

        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY required")

        self.client: Client = create_client(self.url, self.key)

    # ===== TASKS =====

    def insert_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict]:
        """Insert multiple tasks into database"""
        try:
            result = self.client.table("tasks").insert(tasks).execute()
            return result.data
        except Exception as e:
            raise Exception(f"Error inserting tasks: {str(e)}")

    def get_tasks(self, user_id: str, completed: Optional[bool] = None) -> List[Dict]:
        """Get tasks for a user"""
        try:
            query = self.client.table("tasks").select("*").eq("user_id", user_id)

            if completed is not None:
                query = query.eq("completed", completed)

            result = query.execute()
            return result.data
        except Exception as e:
            raise Exception(f"Error fetching tasks: {str(e)}")

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Dict:
        """Update a task"""
        try:
            result = self.client.table("tasks").update(updates).eq("id", task_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise Exception(f"Error updating task: {str(e)}")

    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        try:
            self.client.table("tasks").delete().eq("id", task_id).execute()
            return True
        except Exception as e:
            raise Exception(f"Error deleting task: {str(e)}")

    # ===== BUSY BLOCKS =====

    def insert_busy_blocks(self, blocks: List[Dict[str, Any]]) -> List[Dict]:
        """Insert busy time blocks"""
        try:
            result = self.client.table("busy_blocks").insert(blocks).execute()
            return result.data
        except Exception as e:
            raise Exception(f"Error inserting busy blocks: {str(e)}")

    def get_busy_blocks(self, user_id: str, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Get busy blocks for a user within date range"""
        try:
            query = self.client.table("busy_blocks").select("*").eq("user_id", user_id)

            if start_date:
                query = query.gte("start", start_date)
            if end_date:
                query = query.lte("end", end_date)

            result = query.execute()
            return result.data
        except Exception as e:
            raise Exception(f"Error fetching busy blocks: {str(e)}")

    def delete_busy_block(self, block_id: str) -> bool:
        """Delete a busy block"""
        try:
            self.client.table("busy_blocks").delete().eq("id", block_id).execute()
            return True
        except Exception as e:
            raise Exception(f"Error deleting busy block: {str(e)}")

    # ===== PLANS =====

    def insert_plan(self, plan: Dict[str, Any]) -> Dict:
        """Save a generated plan"""
        try:
            result = self.client.table("plans").insert(plan).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise Exception(f"Error inserting plan: {str(e)}")

    def get_plan(self, plan_id: str) -> Optional[Dict]:
        """Get a plan by ID"""
        try:
            result = self.client.table("plans").select("*").eq("id", plan_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise Exception(f"Error fetching plan: {str(e)}")

    def get_latest_plan(self, user_id: str) -> Optional[Dict]:
        """Get the most recent plan for a user"""
        try:
            result = (
                self.client.table("plans")
                .select("*")
                .eq("user_id", user_id)
                .order("generated_at", desc=True)
                .limit(1)
                .execute()
            )
            return result.data[0] if result.data else None
        except Exception as e:
            raise Exception(f"Error fetching latest plan: {str(e)}")

    def get_user_plans(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get all plans for a user"""
        try:
            result = (
                self.client.table("plans")
                .select("*")
                .eq("user_id", user_id)
                .order("generated_at", desc=True)
                .limit(limit)
                .execute()
            )
            return result.data
        except Exception as e:
            raise Exception(f"Error fetching user plans: {str(e)}")

    # ===== USER PREFERENCES =====

    def save_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict:
        """Save or update user preferences"""
        try:
            # Upsert preferences
            data = {"user_id": user_id, **preferences, "updated_at": datetime.utcnow().isoformat()}

            result = (
                self.client.table("user_preferences")
                .upsert(data, on_conflict="user_id")
                .execute()
            )
            return result.data[0] if result.data else None
        except Exception as e:
            raise Exception(f"Error saving preferences: {str(e)}")

    def get_preferences(self, user_id: str) -> Optional[Dict]:
        """Get user preferences"""
        try:
            result = self.client.table("user_preferences").select("*").eq("user_id", user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            raise Exception(f"Error fetching preferences: {str(e)}")


# Global instance
_supabase_client: Optional[SupabaseClient] = None


def get_supabase_client() -> SupabaseClient:
    """Get or create Supabase client singleton"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client
