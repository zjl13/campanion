from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.serializers import serialize_user_summary
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User, UserPreference
from app.schemas.auth import DevLoginRequest, DevLoginResponse


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/dev-login", response_model=DevLoginResponse)
def dev_login(payload: DevLoginRequest, db: Session = Depends(get_db)) -> DevLoginResponse:
    user = db.scalar(select(User).where(User.device_id == payload.device_id))
    if not user:
        user = User(device_id=payload.device_id, nickname=payload.nickname, timezone="Asia/Shanghai")
        db.add(user)
        db.flush()
        db.add(UserPreference(user_id=user.id))
    else:
        user.nickname = payload.nickname
    db.commit()
    db.refresh(user)
    return DevLoginResponse(
        access_token=f"{settings.dev_token_prefix}-{user.id}",
        user=serialize_user_summary(user),
    )

