"""
AI-powered effort estimation service
"""
from typing import List, Dict
from app.models import Task
from app.clients.ai_client import get_ai_client


def estimate_task_efforts(tasks: List[Task]) -> Dict[str, float]:
    """
    Estimate effort hours for tasks using AI

    Args:
        tasks: List of Task objects

    Returns:
        Dictionary mapping task titles to estimated effort hours
    """
    if not tasks:
        return {}

    # Convert tasks to dict format for AI
    tasks_data = [
        {
            "title": task.title,
            "type": task.task_type,
            "weight": task.weight,
            "notes": task.notes
        }
        for task in tasks
    ]

    # Call AI
    ai_client = get_ai_client()

    try:
        result = ai_client.estimate_effort(tasks_data)
        estimates = result.get("estimates", [])

        # Build mapping
        effort_map = {}
        for estimate in estimates:
            title = estimate.get("title")
            effort_hours = estimate.get("effort_hours", 3.0)
            effort_map[title] = effort_hours

        return effort_map

    except Exception as e:
        print(f"AI estimation failed: {e}")
        # Fallback: simple defaults
        return {task.title: 3.0 for task in tasks}


def apply_effort_estimates(tasks: List[Task]) -> List[Task]:
    """
    Estimate and apply effort hours to tasks in-place

    Args:
        tasks: List of Task objects (modified in place)

    Returns:
        The same list with effort_hours populated
    """
    effort_map = estimate_task_efforts(tasks)

    for task in tasks:
        if task.title in effort_map:
            task.effort_hours = effort_map[task.title]
        else:
            task.effort_hours = 3.0

    return tasks
