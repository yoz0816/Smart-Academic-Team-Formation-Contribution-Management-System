
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Numeric,
    String,
    TIMESTAMP,
    func,
)
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    __table_args__ = (
        CheckConstraint(
            "cgpa >= 0 AND cgpa <= cgpa_scale",
            name="chk_student_cgpa",
        ),
        CheckConstraint(
            "cgpa_scale > 0",
            name="chk_cgpa_scale",
        ),
        CheckConstraint(
            "year_of_study > 0",
            name="chk_student_year",
        ),
        CheckConstraint(
            "problem_solving_score IS NULL OR "
            "problem_solving_score BETWEEN 0 AND 100",
            name="chk_problem_solving",
        ),
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("users.id", name="fk_profile_user"),
        nullable=False,
        unique=True,
    )

    student_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    department: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    year_of_study: Mapped[int] = mapped_column(
        TINYINT(unsigned=True),
        nullable=False,
    )

    cgpa: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    cgpa_scale: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("4.00"),
        server_default="4.00",
    )

    problem_solving_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    created_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        server_default=func.current_timestamp(),
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="student_profile",
    )
    skills: Mapped[list["StudentSkill"]] = relationship(
        "StudentSkill",
        back_populates="student",
        cascade="all, delete-orphan",
    )

    interests: Mapped[list["StudentInterest"]] = relationship(
        "StudentInterest",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    preferences_sent: Mapped[list["StudentPreference"]] = relationship(
        "StudentPreference",
        foreign_keys="StudentPreference.student_id",
        back_populates="student",
        cascade="all, delete-orphan",
    )

    preferences_received: Mapped[list["StudentPreference"]] = relationship(
        "StudentPreference",
        foreign_keys="StudentPreference.preferred_student_id",
        back_populates="preferred_student",
        cascade="all, delete-orphan",
    )
    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    team_memberships: Mapped[list["TeamMember"]] = relationship(
        "TeamMember",
        back_populates="student",
        cascade="all, delete-orphan",
    )

    task_assignments: Mapped[list["TaskAssignment"]] = relationship(
        "TaskAssignment",
        back_populates="student",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<StudentProfile(id={self.id}, "
            f"student_number={self.student_number!r})>"
        )
