from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class PreferredTeammate(Base):
    __tablename__ = "preferred_teammates"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "preferred_user_id",
            name="uq_preferred_teammates_pair",
        ),
        CheckConstraint(
            "user_id != preferred_user_id",
            name="ck_preferred_teammates_not_self",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    preferred_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    student = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="sent_preferences",
    )

    preferred_student = relationship(
        "User",
        foreign_keys=[preferred_user_id],
        back_populates="received_preferences",
    )
