from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.serializers import serialize_buddy
from app.db.session import get_db
from app.models.user import BuddyProfile, User
from app.schemas.buddy import BuddyCreateRequest, BuddyResponse
from app.services.persona import build_persona_payload


router = APIRouter(prefix="/buddies", tags=["buddies"])


@router.post("", response_model=BuddyResponse)
def create_buddy(
    payload: BuddyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BuddyResponse:
    persona = build_persona_payload(payload)
    buddy = BuddyProfile(
        user_id=current_user.id,
        style=payload.style,
        tone=payload.tone,
        strictness=payload.strictness,
        buddy_type=payload.buddy_type,
        language=payload.language,
        display_name=str(persona["display_name"]),
        persona_summary=str(persona["persona_summary"]),
        persona_config=dict(persona["persona_config"]),
    )
    db.add(buddy)
    db.commit()
    db.refresh(buddy)
    return BuddyResponse.model_validate(serialize_buddy(buddy))

