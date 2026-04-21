from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.time import now_in_timezone
from app.models.engagement import ChatMessage, RescheduleRequest
from app.models.planning import Goal, Task
from app.models.user import BuddyProfile, User


def get_active_buddy(db: Session, user_id: str, buddy_id: str | None = None) -> BuddyProfile | None:
    stmt = select(BuddyProfile).where(BuddyProfile.user_id == user_id)
    if buddy_id:
        stmt = stmt.where(BuddyProfile.id == buddy_id)
    stmt = stmt.order_by(BuddyProfile.created_at.desc())
    return db.scalar(stmt)


def style_prefix(buddy: BuddyProfile | None) -> str:
    if not buddy:
        return "我在这。"
    if buddy.style == "humorous":
        return f"{buddy.display_name}上线："
    if buddy.style == "serious":
        return "按计划推进："
    if buddy.style == "calm":
        return "先稳住节奏："
    return f"{buddy.display_name}陪你："


def create_message(
    db: Session,
    *,
    user_id: str,
    role: str,
    content: str,
    buddy_id: str | None = None,
    message_type: str = "normal",
    related_goal_id: str | None = None,
    related_task_id: str | None = None,
    metadata: dict[str, object] | None = None,
    created_at: datetime | None = None,
) -> ChatMessage:
    message = ChatMessage(
        user_id=user_id,
        buddy_id=buddy_id,
        role=role,
        message_type=message_type,
        content=content,
        related_goal_id=related_goal_id,
        related_task_id=related_task_id,
        extra_metadata=metadata or {},
        created_at=created_at or now_in_timezone("Asia/Shanghai"),
    )
    db.add(message)
    db.flush()
    return message


def build_chat_reply(
    db: Session,
    user: User,
    content: str,
    task: Task | None = None,
) -> tuple[str, list[dict[str, str]]]:
    buddy = get_active_buddy(db, user.id, task.goal.buddy_id if task and task.goal else None)
    lead = style_prefix(buddy)
    lowered = content.lower()
    recent_reschedules = 0
    if task:
        recent_reschedules = len(
            db.scalars(select(RescheduleRequest).where(RescheduleRequest.task_id == task.id)).all()
        )

    if any(keyword in content for keyword in ["不想", "拖", "没动力", "学不动", "不太想"]):
        reply = (
            f"{lead}你现在更像是启动阻力，不一定是真的做不了。"
            f"先把 {task.title if task else '眼前这件事'} 缩成 10~20 分钟启动版，"
            "做完再决定要不要继续。"
        )
        if recent_reschedules >= 2:
            reply += "这几次已经连续改过期了，今晚先保住最小版本会更重要。"
        actions = [
            {"type": "quick_reschedule", "label": "改成保底版"},
            {"type": "keep_original", "label": "按原计划开始"},
        ]
        return reply, actions

    if any(keyword in content for keyword in ["累", "困", "状态差", "头疼", "不舒服"]):
        reply = (
            f"{lead}我先按疲惫处理。你可以休息 15 分钟后回来，"
            f"或者把 {task.title if task else '任务'} 改成更短的保底版。"
        )
        return reply, [
            {"type": "quick_reschedule", "label": "改成 20 分钟版"},
            {"type": "pause_short", "label": "先休息 15 分钟"},
        ]

    if any(keyword in lowered for keyword in ["done", "finished"]) or any(keyword in content for keyword in ["完成", "做完", "搞定"]):
        reply = f"{lead}收到，这一步很关键。记得顺手补一句总结或上传证明，我帮你把记录补完整。"
        return reply, [{"type": "upload_proof", "label": "去打卡"}]

    reply = f"{lead}我在。你告诉我现在卡在哪一步，我帮你把下一步压缩到可以立刻开始。"
    return reply, [{"type": "share_blocker", "label": "说下卡点"}]


def create_plan_message(db: Session, user: User, goal: Goal, summary: str) -> ChatMessage:
    buddy = get_active_buddy(db, user.id, goal.buddy_id)
    content = f"{style_prefix(buddy)}{summary}"
    return create_message(
        db,
        user_id=user.id,
        buddy_id=goal.buddy_id,
        role="assistant",
        content=content,
        message_type="reminder",
        related_goal_id=goal.id,
    )


def create_risk_warning_message(db: Session, user: User, goal: Goal, level: str) -> ChatMessage:
    buddy = get_active_buddy(db, user.id, goal.buddy_id)
    content = (
        f"{style_prefix(buddy)}按当前节奏，这个目标的风险已经到 {level}。"
        "我们可以把后面两天改成更小的任务，先把节奏拉回来。"
    )
    return create_message(
        db,
        user_id=user.id,
        buddy_id=goal.buddy_id,
        role="assistant",
        content=content,
        message_type="risk",
        related_goal_id=goal.id,
    )
