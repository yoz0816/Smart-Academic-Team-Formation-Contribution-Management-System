from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    TIMESTAMP,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class StudentPreference(Base):
    __tablename__ = "student_preferences"

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "preferred_student_id",
            name="uq_student_preference",
        ),
        CheckConstraint(
            "student_id <> preferred_student_id",
            name="chk_preference_not_self",
        ),
        CheckConstraint(
            "priority > 0",
            name="chk_preference_priority",
        ),
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )

    student_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("student_profiles.id"),
        nullable=False,
    )

    preferred_student_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("student_profiles.id"),
        nullable=False,
    )

    priority: Mapped[int] = mapped_column(
        TINYINT(unsigned=True),
        nullable=False,
        default=1,
        server_default="1",
    )

    created_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        server_default=func.current_timestamp(),
    )

    student: Mapped["StudentProfile"] = relationship(
        "StudentProfile",
        foreign_keys=[student_id],
        back_populates="preferences_sent",
    )

    preferred_student: Mapped["StudentProfile"] = relationship(
        "StudentProfile",
        foreign_keys=[preferred_student_id],
        back_populates="preferences_received",
    )

    def __repr__(self) -> str:
        return (
            f"<StudentPreference(id={self.id}, "
            f"student_id={self.student_id}, "
            f"preferred_student_id={self.preferred_student_id})>"
        )