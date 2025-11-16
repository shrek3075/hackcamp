"""
Mock database client for testing without Supabase
Stores data in memory - data is lost when server restarts
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime


class MockDBClient:
    """In-memory database for testing"""

    def __init__(self):
        self.tasks = []
        self.busy_blocks = []
        self.plans = []
        self.preferences = {}

    # ===== TASKS =====

    def insert_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict]:
        """Insert multiple tasks"""
        result = []
        for task in tasks:
            task_copy = task.copy()
            if 'id' not in task_copy or not task_copy['id']:
                task_copy['id'] = str(uuid.uuid4())
            if 'created_at' not in task_copy:
                task_copy['created_at'] = datetime.utcnow().isoformat()
            self.tasks.append(task_copy)
            result.append(task_copy)
        return result

    def get_tasks(self, user_id: str, completed: Optional[bool] = None) -> List[Dict]:
        """Get tasks for a user"""
        result = [t for t in self.tasks if t.get('user_id') == user_id]
        if completed is not None:
            result = [t for t in result if t.get('completed', False) == completed]
        return result

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Optional[Dict]:
        """Update a task"""
        for task in self.tasks:
            if task.get('id') == task_id:
                task.update(updates)
                return task
        return None

    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        self.tasks = [t for t in self.tasks if t.get('id') != task_id]
        return True

    # ===== BUSY BLOCKS =====

    def insert_busy_blocks(self, blocks: List[Dict[str, Any]]) -> List[Dict]:
        """Insert busy time blocks"""
        result = []
        for block in blocks:
            block_copy = block.copy()
            if 'id' not in block_copy or not block_copy['id']:
                block_copy['id'] = str(uuid.uuid4())
            if 'created_at' not in block_copy:
                block_copy['created_at'] = datetime.utcnow().isoformat()
            self.busy_blocks.append(block_copy)
            result.append(block_copy)
        return result

    def get_busy_blocks(self, user_id: str, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Get busy blocks for a user"""
        result = [b for b in self.busy_blocks if b.get('user_id') == user_id]
        # For now, ignore date filtering in mock
        return result

    def delete_busy_block(self, block_id: str) -> bool:
        """Delete a busy block"""
        self.busy_blocks = [b for b in self.busy_blocks if b.get('id') != block_id]
        return True

    # ===== PLANS =====

    def insert_plan(self, plan: Dict[str, Any]) -> Dict:
        """Save a generated plan"""
        plan_copy = plan.copy()
        if 'id' not in plan_copy or not plan_copy['id']:
            plan_copy['id'] = str(uuid.uuid4())
        if 'generated_at' not in plan_copy:
            plan_copy['generated_at'] = datetime.utcnow().isoformat()
        self.plans.append(plan_copy)
        return plan_copy

    def get_plan(self, plan_id: str) -> Optional[Dict]:
        """Get a plan by ID"""
        for plan in self.plans:
            if plan.get('id') == plan_id:
                return plan
        return None

    def get_latest_plan(self, user_id: str) -> Optional[Dict]:
        """Get the most recent plan for a user"""
        user_plans = [p for p in self.plans if p.get('user_id') == user_id]
        if not user_plans:
            return None
        # Sort by generated_at descending
        user_plans.sort(key=lambda p: p.get('generated_at', ''), reverse=True)
        return user_plans[0]

    def get_user_plans(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get all plans for a user"""
        user_plans = [p for p in self.plans if p.get('user_id') == user_id]
        user_plans.sort(key=lambda p: p.get('generated_at', ''), reverse=True)
        return user_plans[:limit]

    # ===== USER PREFERENCES =====

    def save_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict:
        """Save or update user preferences"""
        pref_data = {"user_id": user_id, **preferences, "updated_at": datetime.utcnow().isoformat()}
        self.preferences[user_id] = pref_data
        return pref_data

    def get_preferences(self, user_id: str) -> Optional[Dict]:
        """Get user preferences"""
        return self.preferences.get(user_id)


# Global instance
_mock_db_client: Optional[MockDBClient] = None


def get_mock_db_client() -> MockDBClient:
    """Get or create mock DB client singleton"""
    global _mock_db_client
    if _mock_db_client is None:
        _mock_db_client = MockDBClient()
    return _mock_db_client
