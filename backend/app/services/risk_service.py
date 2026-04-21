from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.ids import generate_prefixed_id
from app.core.time import ensure_timezone, now_in_timezone
from app.models.engagement import RescheduleRequest, RiskSnapshot
from app.models.planning import Goal, Task


def latest_snapshot(db: Session, goal_id: str) -> RiskSnapshot | None:
    stmt = (
        select(RiskSnapshot)
        .where(RiskSnapshot.goal_id == goal_id)
        .order_by(RiskSnapshot.created_at.desc())
        .limit(1)
    )
    return db.scalar(stmt)


def build_risk_snapshot(db: Session, goal: Goal) -> RiskSnapshot:
    tasks = db.scalars(select(Task).where(Task.goal_id == goal.id)).all()
    completed = [task for task in tasks if task.status == "completed"]
    remaining = [task for task in tasks if task.status not in {"completed", "waived"}]
    missed = [task for task in tasks if task.status == "missed"]
    reschedules = db.scalars(select(RescheduleRequest).where(RescheduleRequest.task_id.in_([task.id for task in tasks] or [""]))).all()

    total_tasks = max(len(tasks), 1)
    completion_rate = len(completed) / total_tasks
    timezone_name = goal.user.timezone if goal.user else "Asia/Shanghai"
    today = now_in_timezone(timezone_name)
    days_left = max((ensure_timezone(goal.deadline, timezone_name) - today).days, 0)

    score = 15
    if days_left <= 3:
        score += 25
    elif days_left <= 7:
        score += 12
    score += min(len(reschedules) * 10, 30)
    score += int((1 - completion_rate) * 25)
    if len(remaining) > max(days_left, 1):
        score += 15
    score += min(len(missed) * 8, 16)
    score = max(0, min(score, 100))

    if score < 40:
        level = "low"
    elif score < 70:
        level = "medium"
    else:
        level = "high"

    reasons: list[str] = []
    if len(reschedules) >= 2:
        reasons.append(f"最近已改期 {len(reschedules)} 次，执行节奏有波动。")
    if len(remaining) > max(days_left, 1):
        reasons.append("剩余任务量已经接近或超过可用天数。")
    if completion_rate < 0.4:
        reasons.append("已完成任务占比较低，需要更稳定的推进。")
    if days_left <= 3:
        reasons.append("距离截止时间已经非常近。")
    if not reasons:
        reasons.append("当前进度基本可控，按计划推进即可。")

    suggestions = [
        "把接下来 2~3 天的任务颗粒度再切小一点。",
        "优先保住每日最小可执行版本，不求一次做满。",
    ]
    if level != "low":
        suggestions.append("必要时把难任务改成 20 分钟保底版。")
    if level == "high":
        suggestions.append("考虑开启冲刺模式或适当顺延截止时间。")

    snapshot = RiskSnapshot(
        id=generate_prefixed_id("risk"),
        goal_id=goal.id,
        risk_score=score,
        risk_level=level,
        reasons=reasons,
        suggestions=suggestions,
        created_at=today,
    )
    return snapshot


def refresh_risk_snapshot(db: Session, goal: Goal) -> RiskSnapshot:
    snapshot = build_risk_snapshot(db, goal)
    db.add(snapshot)
    db.flush()
    return snapshot
