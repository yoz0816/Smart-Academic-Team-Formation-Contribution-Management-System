from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    Index,
    String,
    TIMESTAMP,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class UserSession(Base):
    __tablename__ = "user_sessions"

    __table_args__ = (
        UniqueConstraint(
            "token_hash",
            name="uq_user_sessions_token_hash",
        ),
        Index(
            "idx_user_sessions_user_expiry",
            "user_id",
            "expires_at",
        ),
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    csrf_token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
    )

    last_seen_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    def __repr__(self) -> str:
        return f"<UserSession(id={self.id}, user_id={self.user_id})>"