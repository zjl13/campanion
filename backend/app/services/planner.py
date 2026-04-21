from __future__ import annotations

from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.time import now_in_timezone
from app.models.planning import Goal, Plan, Task
from app.models.user import User
from app.services.chat_service import create_plan_message, create_risk_warning_message
from app.services.risk_service import refresh_risk_snapshot
from app.services.scheduling import cancel_task_reminders, create_task_reminders, find_open_slot


def task_templates(goal: Goal) -> list[dict[str, object]]:
    if goal.goal_type == "study":
        return [
            {"title": f"{goal.title}：梳理重点范围", "minutes": 35, "difficulty": "easy", "hint": "拍一张笔记或发 1 句今日重点总结。"},
            {"title": f"{goal.title}：高频内容复盘", "minutes": 40, "difficulty": "medium", "hint": "上传复盘页或写出今天记住的 5 个要点。"},
            {"title": f"{goal.title}：专项练习 1 组", "minutes": 45, "difficulty": "medium", "hint": "上传练习截图或写正确率。"},
            {"title": f"{goal.title}：错题/薄弱点整理", "minutes": 35, "difficulty": "medium", "hint": "拍整理页或写 1 条薄弱点结论。"},
            {"title": f"{goal.title}：专项练习 2 组", "minutes": 50, "difficulty": "hard", "hint": "上传练习截图。"},
            {"title": f"{goal.title}：模拟测试", "minutes": 60, "difficulty": "hard", "hint": "上传成绩页或用文字汇报完成情况。"},
            {"title": f"{goal.title}：复盘与下阶段安排", "minutes": 30, "difficulty": "easy", "hint": "发一条复盘总结。"},
        ]
    if goal.goal_type == "reading":
        return [
            {"title": f"{goal.title}：阅读第 1 段", "minutes": 30, "difficulty": "easy", "hint": "上传书页或一句摘录。"},
            {"title": f"{goal.title}：阅读第 2 段", "minutes": 30, "difficulty": "easy", "hint": "上传书页或一句摘录。"},
            {"title": f"{goal.title}：整理人物/观点", "minutes": 25, "difficulty": "medium", "hint": "写 2 句摘要。"},
            {"title": f"{goal.title}：阅读第 3 段", "minutes": 30, "difficulty": "easy", "hint": "上传书页或一句摘录。"},
            {"title": f"{goal.title}：阅读第 4 段", "minutes": 30, "difficulty": "easy", "hint": "上传书页或一句摘录。"},
            {"title": f"{goal.title}：输出笔记", "minutes": 35, "difficulty": "medium", "hint": "拍笔记或发总结。"},
            {"title": f"{goal.title}：回顾与收尾", "minutes": 25, "difficulty": "easy", "hint": "写 1 条本周收获。"},
        ]
    if goal.goal_type == "fitness":
        return [
            {"title": f"{goal.title}：轻量热身", "minutes": 20, "difficulty": "easy", "hint": "上传运动截图或自拍。"},
            {"title": f"{goal.title}：主训练 1", "minutes": 45, "difficulty": "medium", "hint": "上传运动记录。"},
            {"title": f"{goal.title}：恢复与拉伸", "minutes": 20, "difficulty": "easy", "hint": "上传拉伸记录或一句反馈。"},
            {"title": f"{goal.title}：主训练 2", "minutes": 45, "difficulty": "medium", "hint": "上传运动记录。"},
            {"title": f"{goal.title}：核心练习", "minutes": 30, "difficulty": "medium", "hint": "上传训练截图。"},
            {"title": f"{goal.title}：主训练 3", "minutes": 50, "difficulty": "hard", "hint": "上传运动记录。"},
            {"title": f"{goal.title}：一周复盘", "minutes": 20, "difficulty": "easy", "hint": "写体感和下周调整。"},
        ]
    return [
        {"title": f"{goal.title}：拆解目标", "minutes": 30, "difficulty": "easy", "hint": "写出接下来 3 个小步骤。"},
        {"title": f"{goal.title}：准备材料", "minutes": 35, "difficulty": "easy", "hint": "拍材料截图或列清单。"},
        {"title": f"{goal.title}：核心执行 1", "minutes": 45, "difficulty": "medium", "hint": "上传过程截图。"},
        {"title": f"{goal.title}：核心执行 2", "minutes": 45, "difficulty": "medium", "hint": "上传过程截图。"},
        {"title": f"{goal.title}：修补薄弱点", "minutes": 30, "difficulty": "medium", "hint": "写本次卡点。"},
        {"title": f"{goal.title}：收尾整理", "minutes": 30, "difficulty": "easy", "hint": "上传结果截图。"},
        {"title": f"{goal.title}：复盘下一步", "minutes": 25, "difficulty": "easy", "hint": "写 1 条复盘。"},
    ]


def latest_plan_version(db: Session, goal_id: str) -> int:
    stmt = select(func.max(Plan.version)).where(Plan.goal_id == goal_id)
    return db.scalar(stmt) or 0


def deactivate_future_tasks(db: Session, goal_id: str, now) -> None:
    tasks = db.scalars(
        select(Task).where(
            Task.goal_id == goal_id,
            Task.scheduled_start >= now,
            Task.status.in_(["planned", "scheduled", "active"]),
        )
    ).all()
    for task in tasks:
        task.status = "waived"
        cancel_task_reminders(db, task.id)


def generate_plan(db: Session, user: User, goal: Goal, source: str = "initial") -> tuple[Plan, list[Task]]:
    now = now_in_timezone(user.timezone)
    if source != "initial":
        deactivate_future_tasks(db, goal.id, now)

    plan = Plan(
        goal_id=goal.id,
        version=latest_plan_version(db, goal.id) + 1,
        source=source,
        summary="",
        risk_score=0,
        raw_model_output={},
        created_at=now,
    )
    db.add(plan)
    db.flush()

    tasks: list[Task] = []
    for index, template in enumerate(task_templates(goal)):
        anchor_day = (now + timedelta(days=index)).date()
        start_time, end_time = find_open_slot(
            db,
            user,
            anchor_day=anchor_day,
            duration_minutes=int(template["minutes"]),
            not_before=now if index == 0 else None,
        )
        task = Task(
            goal_id=goal.id,
            plan_id=plan.id,
            title=str(template["title"]),
            description=f"围绕目标“{goal.title}”推进一小步。",
            task_type=goal.goal_type,
            status="scheduled",
            scheduled_start=start_time,
            scheduled_end=end_time,
            estimated_minutes=int(template["minutes"]),
            difficulty=str(template["difficulty"]),
            proof_requirement={
                "type": "image_or_text",
                "hint": str(template["hint"]),
            },
        )
        db.add(task)
        db.flush()
        create_task_reminders(db, task)
        tasks.append(task)

    db.flush()
    snapshot = refresh_risk_snapshot(db, goal)
    plan.risk_score = snapshot.risk_score
    plan.summary = (
        f"我先按未来 7 天给你排了一版能落地的计划，优先保证每天都有明确启动点。"
        f"当前风险分 {snapshot.risk_score}，建议先照这个节奏跑起来。"
    )
    plan.raw_model_output = {
        "goal_summary": goal.title,
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "scheduled_start": task.scheduled_start.isoformat(),
                "scheduled_end": task.scheduled_end.isoformat(),
            }
            for task in tasks
        ],
    }
    create_plan_message(db, user, goal, plan.summary)
    if snapshot.risk_level == "high":
        create_risk_warning_message(db, user, goal, snapshot.risk_level)
    return plan, tasks

