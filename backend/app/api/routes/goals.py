from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.serializers import serialize_goal, serialize_planned_task
from app.db.session import get_db
from app.models.planning import Goal, Plan, Task
from app.models.user import BuddyProfile, User
from app.schemas.goal import GoalCreateRequest, GoalCreateResponse, GoalPlanResponse, GoalResponse
from app.services.planner import generate_plan
from app.services.risk_service import latest_snapshot


router = APIRouter(prefix="/goals", tags=["goals"])


def latest_plan_for_goal(db: Session, goal_id: str) -> Plan | None:
    stmt = select(Plan).where(Plan.goal_id == goal_id).order_by(Plan.version.desc()).limit(1)
    return db.scalar(stmt)


@router.post("", response_model=GoalCreateResponse)
def create_goal(
    payload: GoalCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GoalCreateResponse:
    if payload.buddy_id:
        buddy = db.get(BuddyProfile, payload.buddy_id)
        if not buddy or buddy.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buddy not found")
    goal = Goal(
        user_id=current_user.id,
        buddy_id=payload.buddy_id,
        title=payload.title,
        description=payload.description,
        goal_type=payload.goal_type,
        priority=payload.priority,
        deadline=payload.deadline,
        status="active",
    )
    db.add(goal)
    db.flush()
    generate_plan(db, current_user, goal, source="initial")
    db.commit()
    return GoalCreateResponse(goal_id=goal.id, planning_status="completed")


@router.post("/{goal_id}/generate-plan", response_model=GoalPlanResponse)
def regenerate_goal_plan(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GoalPlanResponse:
    goal = db.get(Goal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    plan, tasks = generate_plan(db, current_user, goal, source="regenerated")
    db.commit()
    return GoalPlanResponse(
        goal_id=goal.id,
        plan_id=plan.id,
        risk_score=plan.risk_score,
        summary=plan.summary,
        tasks=[serialize_planned_task(task) for task in tasks],
    )


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GoalResponse:
    goal = db.get(Goal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return GoalResponse.model_validate(serialize_goal(goal))


@router.get("/{goal_id}/plan", response_model=GoalPlanResponse)
def get_goal_plan(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GoalPlanResponse:
    goal = db.get(Goal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    plan = latest_plan_for_goal(db, goal_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    tasks = db.scalars(
        select(Task).where(Task.plan_id == plan.id).order_by(Task.scheduled_start.asc())
    ).all()
    snapshot = latest_snapshot(db, goal_id)
    return GoalPlanResponse(
        goal_id=goal.id,
        plan_id=plan.id,
        risk_score=snapshot.risk_score if snapshot else plan.risk_score,
        summary=plan.summary,
        tasks=[serialize_planned_task(task) for task in tasks],
    )
