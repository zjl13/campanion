from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.core.ids import generate_prefixed_id
from app.db.base import Base
from app.models.base import TimestampMixin


class ReminderEvent(TimestampMixin, Base):
    __tablename__ = "reminder_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: generate_prefixed_id("rem"))
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"), nullable=False, index=True)
    reminder_type: Mapped[str] = mapped_column(String(24), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(24), default="pending", nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: generate_prefixed_id("msg"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    buddy_id: Mapped[str | None] = mapped_column(ForeignKey("buddy_profiles.id"), nullable=True, index=True)
    role: Mapped[str] = mapped_column(String(24), nullable=False)
    message_type: Mapped[str] = mapped_column(String(32), default="normal", nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    related_goal_id: Mapped[str | None] = mapped_column(ForeignKey("goals.id"), nullable=True)
    related_task_id: Mapped[str | None] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    extra_metadata: Mapped[dict[str, object]] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["User"] = relationship(back_populates="chat_messages")


class ProofSubmission(Base):
    __tablename__ = "proof_submissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: generate_prefixed_id("prf"))
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    media_type: Mapped[str] = mapped_column(String(24), nullable=False)
    file_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    text_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ProofReview(Base):
    __tablename__ = "proof_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: generate_prefixed_id("prv"))
    proof_id: Mapped[str] = mapped_column(ForeignKey("proof_submissions.id"), nullable=False, unique=True)
    review_status: Mapped[str] = mapped_column(String(32), nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    feedback: Mapped[str] = mapped_column(Text, nullable=False)
    raw_model_output: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class RescheduleRequest(Base):
    __tablename__ = "reschedule_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: generate_prefixed_id("rsq"))
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    reason_text: Mapped[str] = mapped_column(Text, nullable=False)
    reason_category: Mapped[str] = mapped_column(String(32), nullable=False)
    action_taken: Mapped[str] = mapped_column(String(32), nullable=False)
    new_task_id: Mapped[str | None] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    model_summary: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class RiskSnapshot(Base):
    __tablename__ = "risk_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: generate_prefixed_id("risk"))
    goal_id: Mapped[str] = mapped_column(ForeignKey("goals.id"), nullable=False, index=True)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(16), nullable=False)
    reasons: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    suggestions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

if TYPE_CHECKING:
    from app.models.planning import Goal, Task
    from app.models.user import BuddyProfile, User
