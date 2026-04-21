from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import MessageAction


class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    message_type: str
    related_goal_id: str | None = None
    related_task_id: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
    created_at: datetime


class ChatListResponse(BaseModel):
    messages: list[ChatMessageResponse]
    next_cursor: str | None = None


class ChatCreateRequest(BaseModel):
    message: str
    context_task_id: str | None = None


class ChatCreateResponse(BaseModel):
    assistant_message: ChatMessageResponse
    actions: list[MessageAction]
