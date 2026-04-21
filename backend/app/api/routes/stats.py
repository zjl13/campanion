from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.engagement import ProofReview, ProofSubmission, RescheduleRequest
from app.models.planning import Goal, Task
from app.models.user import User
from app.schemas.stats import OverviewStatsResponse, RiskResponse
from app.services.risk_service import latest_snapshot, refresh_risk_snapshot


router = APIRouter(tags=["stats"])


@router.get("/goals/{goal_id}/risk", response_model=RiskResponse)
def get_goal_risk(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RiskResponse:
    goal = db.get(Goal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    snapshot = latest_snapshot(db, goal.id) or refresh_risk_snapshot(db, goal)
    db.commit()
    return RiskResponse(
        risk_score=snapshot.risk_score,
        risk_level=snapshot.risk_level,
        reasons=snapshot.reasons,
        suggestions=snapshot.suggestions,
    )


@router.get("/stats/overview", response_model=OverviewStatsResponse)
def get_overview_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OverviewStatsResponse:
    tasks = db.scalars(
        select(Task).join(Task.goal).where(Goal.user_id == current_user.id)
    ).all()
    completed_tasks = len([task for task in tasks if task.status == "completed"])
    completion_rate = completed_tasks / max(len(tasks), 1)
    proof_ids = [proof.id for proof in db.scalars(select(ProofSubmission).where(ProofSubmission.user_id == current_user.id)).all()]
    accepted = 0
    if proof_ids:
        reviews = db.scalars(select(ProofReview).where(ProofReview.proof_id.in_(proof_ids))).all()
        accepted = len([review for review in reviews if review.review_status == "accepted"])
        checkin_rate = accepted / max(len(reviews), 1)
    else:
        checkin_rate = 0.0
    reschedule_count = len(db.scalars(select(RescheduleRequest).where(RescheduleRequest.user_id == current_user.id)).all())
    current_streak = 0
    for task in sorted(tasks, key=lambda item: item.scheduled_start, reverse=True):
        if task.status == "completed":
            current_streak += 1
        else:
            break
    return OverviewStatsResponse(
        completed_tasks=completed_tasks,
        completion_rate=round(completion_rate, 2),
        checkin_rate=round(checkin_rate, 2),
        reschedule_count=reschedule_count,
        current_streak_days=current_streak,
    )

