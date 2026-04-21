from __future__ import annotations

from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.time import ensure_timezone, now_in_timezone
from app.models.engagement import RescheduleRequest
from app.models.planning import Goal, Task
from app.models.user import User
from app.services.chat_service import create_message, get_active_buddy, style_prefix
from app.services.risk_service import refresh_risk_snapshot
from app.services.scheduling import cancel_task_reminders, create_task_reminders, find_open_slot


def classify_reason(reason_text: str) -> str:
    text = reason_text.lower()
    if any(keyword in reason_text for keyword in ["组会", "开会", "上课", "课程", "加班", "冲突", "临时"]) or any(
        keyword in text for keyword in ["meeting", "class", "conflict"]
    ):
        return "schedule_conflict"
    if any(keyword in reason_text for keyword in ["累", "困", "状态不好", "不舒服", "头疼"]):
        return "fatigue"
    if any(keyword in reason_text for keyword in ["急事", "紧急", "医院", "家里出事"]):
        return "emergency"
    if any(keyword in reason_text for keyword in ["不想", "没动力", "不想做", "拖延"]):
        return "procrastination_risk"
    return "other"


def suggested_action(reason_category: str) -> str:
    if reason_category in {"schedule_conflict", "emergency"}:
        return "postpone"
    if reason_category == "fatigue":
        return "downgrade_task"
    if reason_category == "procrastination_risk":
        return "split_task"
    return "postpone"


def adjusted_duration(task: Task, action: str) -> int:
    if action == "downgrade_task":
        return max(15, min(25, task.estimated_minutes // 2))
    if action == "split_task":
        return max(10, min(20, task.estimated_minutes // 2))
    return task.estimated_minutes


def title_for_new_task(task: Task, action: str) -> str:
    if action == "downgrade_task":
        return f"{task.title}（保底版）"
    if action == "split_task":
        return f"{task.title}（启动版）"
    return task.title


def build_reply(user: User, goal: Goal, task: Task, new_task: Task, category: str, action: str, db: Session) -> str:
    buddy = get_active_buddy(db, user.id, goal.buddy_id)
    lead = style_prefix(buddy)
    if category == "schedule_conflict":
        return f"{lead}这次更像正常冲突，我先把你挪到 {new_task.scheduled_start.strftime('%H:%M')}，今晚继续保住进度。"
    if category == "fatigue":
        return f"{lead}我先不跟状态硬碰硬，给你改成 {new_task.estimated_minutes} 分钟保底版，时间放在 {new_task.scheduled_start.strftime('%H:%M')}。"
    if category == "procrastination_risk":
        return f"{lead}这更像启动难，不是彻底做不了。我把它切成 {new_task.estimated_minutes} 分钟启动版，先在 {new_task.scheduled_start.strftime('%H:%M')} 开始。"
    return f"{lead}我先帮你顺延到 {new_task.scheduled_start.strftime('%H:%M')}，计划继续，不让今天整段掉线。"


def reschedule_task(
    db: Session,
    *,
    user: User,
    task: Task,
    reason_text: str,
    preferred_strategy: str = "auto",
) -> tuple[RescheduleRequest, Task, str, str]:
    goal = task.goal
    category = classify_reason(reason_text)
    action = suggested_action(category) if preferred_strategy == "auto" else preferred_strategy
    duration = adjusted_duration(task, action)
    now = now_in_timezone(user.timezone)
    floor = max(
        now + timedelta(minutes=30),
        ensure_timezone(task.scheduled_end, user.timezone) + timedelta(minutes=30),
    )
    start_time, end_time = find_open_slot(
        db,
        user,
        anchor_day=floor.date(),
        duration_minutes=duration,
        not_before=floor,
    )

    task.status = "rescheduled"
    cancel_task_reminders(db, task.id)

    new_task = Task(
        goal_id=task.goal_id,
        plan_id=task.plan_id,
        parent_task_id=task.id,
        title=title_for_new_task(task, action),
        description=task.description,
        task_type=task.task_type,
        status="scheduled",
        scheduled_start=start_time,
        scheduled_end=end_time,
        estimated_minutes=duration,
        difficulty=task.difficulty,
        proof_requirement=task.proof_requirement,
    )
    db.add(new_task)
    db.flush()
    create_task_reminders(db, new_task)

    assistant_reply = build_reply(user, goal, task, new_task, category, action, db)
    request = RescheduleRequest(
        task_id=task.id,
        user_id=user.id,
        reason_text=reason_text,
        reason_category=category,
        action_taken=action,
        new_task_id=new_task.id,
        model_summary=assistant_reply,
        created_at=now,
    )
    db.add(request)
    create_message(
        db,
        user_id=user.id,
        buddy_id=goal.buddy_id,
        role="assistant",
        content=assistant_reply,
        message_type="normal",
        related_goal_id=goal.id,
        related_task_id=new_task.id,
    )
    refresh_risk_snapshot(db, goal)
    return request, new_task, assistant_reply, category
