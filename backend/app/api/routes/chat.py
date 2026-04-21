from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.serializers import serialize_chat_message
from app.db.session import get_db
from app.models.engagement import ChatMessage
from app.models.planning import Task
from app.models.user import User
from app.schemas.chat import ChatCreateRequest, ChatCreateResponse, ChatListResponse
from app.services.chat_service import build_chat_reply, create_message


router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/messages", response_model=ChatListResponse)
def list_messages(
    cursor: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatListResponse:
    stmt = select(ChatMessage).where(ChatMessage.user_id == current_user.id)
    if cursor:
        stmt = stmt.where(ChatMessage.created_at < datetime.fromisoformat(cursor))
    messages = db.scalars(stmt.order_by(ChatMessage.created_at.desc()).limit(limit)).all()
    ordered = list(reversed(messages))
    next_cursor = ordered[0].created_at.isoformat() if ordered else None
    return ChatListResponse(
        messages=[serialize_chat_message(message) for message in ordered],
        next_cursor=next_cursor,
    )


@router.post("/messages", response_model=ChatCreateResponse)
def create_chat_message(
    payload: ChatCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatCreateResponse:
    task = db.get(Task, payload.context_task_id) if payload.context_task_id else None
    if task and task.goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    create_message(
        db,
        user_id=current_user.id,
        buddy_id=task.goal.buddy_id if task else None,
        role="user",
        content=payload.message,
        related_goal_id=task.goal_id if task else None,
        related_task_id=task.id if task else None,
    )
    reply_text, actions = build_chat_reply(db, current_user, payload.message, task=task)
    assistant = create_message(
        db,
        user_id=current_user.id,
        buddy_id=task.goal.buddy_id if task else None,
        role="assistant",
        content=reply_text,
        related_goal_id=task.goal_id if task else None,
        related_task_id=task.id if task else None,
        metadata={"actions": actions},
    )
    db.commit()
    return ChatCreateResponse(
        assistant_message=serialize_chat_message(assistant),
        actions=actions,
    )
