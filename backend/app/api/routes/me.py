from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.serializers import serialize_preferences, serialize_user_summary
from app.db.session import get_db
from app.models.user import User, UserPreference
from app.schemas.user import MeResponse, PreferenceResponse, PreferenceUpdateRequest


router = APIRouter(tags=["me"])


@router.get("/me", response_model=MeResponse)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MeResponse:
    preferences = current_user.preferences
    return MeResponse(
        user=serialize_user_summary(current_user),
        preferences=serialize_preferences(current_user, preferences),
    )


@router.put("/me/preferences", response_model=PreferenceResponse)
def update_preferences(
    payload: PreferenceUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PreferenceResponse:
    preferences = current_user.preferences
    if not preferences:
        preferences = UserPreference(user_id=current_user.id)
        db.add(preferences)
        db.flush()

    preferences.focus_time_blocks = [item.model_dump() for item in payload.preferred_focus_blocks]
    if payload.sleep_time:
        preferences.sleep_start = payload.sleep_time.start
        preferences.sleep_end = payload.sleep_time.end
    if payload.reminder_level:
        preferences.reminder_level = payload.reminder_level
    if payload.preferred_style:
        preferences.preferred_style = payload.preferred_style
    if payload.timezone:
        current_user.timezone = payload.timezone

    db.commit()
    db.refresh(current_user)
    return PreferenceResponse.model_validate(serialize_preferences(current_user, preferences))

