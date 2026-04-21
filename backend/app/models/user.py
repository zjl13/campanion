from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import time

from sqlalchemy import ForeignKey, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.core.ids import generate_prefixed_id
from app.db.base import Base
from app.models.base import TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: generate_prefixed_id("usr"))
    device_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    nickname: Mapped[str] = mapped_column(String(64), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Shanghai", nullable=False)

    preferences: Mapped[UserPreference | None] = relationship(back_populates="user", uselist=False)
    buddy_profiles: Mapped[list[BuddyProfile]] = relationship(back_populates="user")
    goals: Mapped[list["Goal"]] = relationship(back_populates="user")
    calendar_blocks: Mapped[list["CalendarBlock"]] = relationship(back_populates="user")
    chat_messages: Mapped[list["ChatMessage"]] = relationship(back_populates="user")


class UserPreference(TimestampMixin, Base):
    __tablename__ = "user_preferences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: generate_prefixed_id("pref"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    sleep_start: Mapped[time | None] = mapped_column(Time(), nullable=True)
    sleep_end: Mapped[time | None] = mapped_column(Time(), nullable=True)
    reminder_level: Mapped[str] = mapped_column(String(24), default="standard", nullable=False)
    preferred_style: Mapped[str] = mapped_column(String(24), default="encouraging", nullable=False)
    focus_time_blocks: Mapped[list[dict[str, str | int]]] = mapped_column(JSON, default=list, nullable=False)

    user: Mapped[User] = relationship(back_populates="preferences")


class BuddyProfile(TimestampMixin, Base):
    __tablename__ = "buddy_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: generate_prefixed_id("bud"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    style: Mapped[str] = mapped_column(String(24), nullable=False)
    tone: Mapped[str] = mapped_column(String(24), default="supportive", nullable=False)
    strictness: Mapped[str] = mapped_column(String(24), nullable=False)
    buddy_type: Mapped[str] = mapped_column(String(24), nullable=False)
    language: Mapped[str] = mapped_column(String(24), default="zh-CN", nullable=False)
    display_name: Mapped[str] = mapped_column(String(64), nullable=False)
    persona_summary: Mapped[str] = mapped_column(String(500), nullable=False)
    persona_config: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)

    user: Mapped[User] = relationship(back_populates="buddy_profiles")
    goals: Mapped[list["Goal"]] = relationship(back_populates="buddy")

if TYPE_CHECKING:
    from app.models.engagement import ChatMessage
    from app.models.planning import CalendarBlock, Goal
