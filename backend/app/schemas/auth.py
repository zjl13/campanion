from pydantic import BaseModel

from app.schemas.common import UserSummary


class DevLoginRequest(BaseModel):
    device_id: str
    nickname: str


class DevLoginResponse(BaseModel):
    access_token: str
    user: UserSummary

