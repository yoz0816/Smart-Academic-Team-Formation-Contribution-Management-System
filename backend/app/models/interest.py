from __future__ import annotations

from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Interest(Base):
    __tablename__ = "interests"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        unique=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    student_interests: Mapped[list["StudentInterest"]] = relationship(
        "StudentInterest",
        back_populates="interest",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Interest(id={self.id}, name={self.name!r})>"


class StudentInterest(Base):
    __tablename__ = "student_interests"

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "interest_id",
            name="uq_student_interest",
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

    interest_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("interests.id"),
        nullable=False,
    )

    student: Mapped["StudentProfile"] = relationship(
        "StudentProfile",
        back_populates="interests",
    )

    interest: Mapped["Interest"] = relationship(
        "Interest",
        back_populates="student_interests",
    )

    def __repr__(self) -> str:
        return (
            f"<StudentInterest(id={self.id}, "
            f"student_id={self.student_id}, "
            f"interest_id={self.interest_id})>"
        )