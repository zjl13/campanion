from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Time, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.core.ids import generate_prefixed_id
from app.db.base import Base
from app.models.base import TimestampMixin


class Goal(TimestampMixin, Base):
    __tablename__ = "goals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: generate_prefixed_id("goal"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    buddy_id: Mapped[str | None] = mapped_column(ForeignKey("buddy_profiles.id"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    goal_type: Mapped[str] = mapped_column(String(24), nullable=False)
    priority: Mapped[str] = mapped_column(String(24), default="medium", nullable=False)
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="active", nullable=False)

    user: Mapped["User"] = relationship(back_populates="goals")
    buddy: Mapped["BuddyProfile | None"] = relationship(back_populates="goals")
    plans: Mapped[list["Plan"]] = relationship(back_populates="goal")
    tasks: Mapped[list["Task"]] = relationship(back_populates="goal")


class CalendarBlock(TimestampMixin, Base):
    __tablename__ = "calendar_blocks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: generate_prefixed_id("blk"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    block_type: Mapped[str] = mapped_column(String(24), nullable=False)
    start_time: Mapped[time] = mapped_column(Time(), nullable=False)
    end_time: Mapped[time] = mapped_column(Time(), nullable=False)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)
    repeat_rule: Mapped[str] = mapped_column(String(24), default="weekly", nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date(), nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date(), nullable=True)

    user: Mapped["User"] = relationship(back_populates="calendar_blocks")


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: generate_prefixed_id("plan"))
    goal_id: Mapped[str] = mapped_column(ForeignKey("goals.id"), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(String(24), default="initial", nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    raw_model_output: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    goal: Mapped[Goal] = relationship(back_populates="plans")
    tasks: Mapped[list["Task"]] = relationship(back_populates="plan")


class Task(TimestampMixin, Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: generate_prefixed_id("tsk"))
    goal_id: Mapped[str] = mapped_column(ForeignKey("goals.id"), nullable=False, index=True)
    plan_id: Mapped[str] = mapped_column(ForeignKey("plans.id"), nullable=False, index=True)
    parent_task_id: Mapped[str | None] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_type: Mapped[str] = mapped_column(String(24), nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="scheduled", nullable=False, index=True)
    scheduled_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    scheduled_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(24), default="medium", nullable=False)
    proof_requirement: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    completion_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    goal: Mapped[Goal] = relationship(back_populates="tasks")
    plan: Mapped[Plan] = relationship(back_populates="tasks")

if TYPE_CHECKING:
    from app.models.user import BuddyProfile, User
