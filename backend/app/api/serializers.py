from app.models.engagement import ChatMessage, ProofReview
from app.models.planning import CalendarBlock, Goal, Task
from app.models.user import BuddyProfile, User, UserPreference


def serialize_user_summary(user: User) -> dict[str, object]:
    return {
        "id": user.id,
        "nickname": user.nickname,
        "timezone": user.timezone,
    }


def serialize_preferences(user: User, preferences: UserPreference | None) -> dict[str, object] | None:
    if not preferences:
        return None
    sleep_time = None
    if preferences.sleep_start and preferences.sleep_end:
        sleep_time = {
            "start": preferences.sleep_start.isoformat(timespec="minutes"),
            "end": preferences.sleep_end.isoformat(timespec="minutes"),
        }
    return {
        "preferred_focus_blocks": preferences.focus_time_blocks,
        "sleep_time": sleep_time,
        "timezone": user.timezone,
        "reminder_level": preferences.reminder_level,
        "preferred_style": preferences.preferred_style,
    }


def serialize_buddy(buddy: BuddyProfile) -> dict[str, object]:
    return {
        "buddy_id": buddy.id,
        "display_name": buddy.display_name,
        "persona_summary": buddy.persona_summary,
    }


def serialize_calendar_block(block: CalendarBlock) -> dict[str, object]:
    return {
        "id": block.id,
        "title": block.title,
        "type": block.block_type,
        "weekday": block.weekday,
        "start_time": block.start_time,
        "end_time": block.end_time,
        "repeat": block.repeat_rule,
        "start_date": block.start_date,
        "end_date": block.end_date,
    }


def serialize_goal(goal: Goal) -> dict[str, object]:
    return {
        "id": goal.id,
        "title": goal.title,
        "description": goal.description,
        "goal_type": goal.goal_type,
        "priority": goal.priority,
        "deadline": goal.deadline,
        "status": goal.status,
        "buddy_id": goal.buddy_id,
    }


def serialize_task(task: Task) -> dict[str, object]:
    return {
        "id": task.id,
        "goal_id": task.goal_id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "start_time": task.scheduled_start,
        "end_time": task.scheduled_end,
        "estimated_minutes": task.estimated_minutes,
        "actual_minutes": task.actual_minutes,
        "proof_requirement": {
            "type": task.proof_requirement.get("type", "image_or_text"),
            "hint": task.proof_requirement.get("hint", ""),
        },
        "completion_note": task.completion_note,
    }


def serialize_planned_task(task: Task) -> dict[str, object]:
    payload = serialize_task(task)
    payload.pop("goal_id", None)
    return payload


def serialize_chat_message(message: ChatMessage) -> dict[str, object]:
    return {
        "id": message.id,
        "role": message.role,
        "content": message.content,
        "message_type": message.message_type,
        "related_goal_id": message.related_goal_id,
        "related_task_id": message.related_task_id,
        "metadata": message.extra_metadata,
        "created_at": message.created_at,
    }


def serialize_review(proof_id: str, review: ProofReview) -> dict[str, object]:
    return {
        "proof_id": proof_id,
        "review_status": review.review_status,
        "confidence": float(review.confidence),
        "feedback": review.feedback,
    }
