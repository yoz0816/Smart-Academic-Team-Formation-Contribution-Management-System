from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Numeric,
    String,
    Text,
    TIMESTAMP,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class TeamMember(Base):
    __tablename__ = "team_members"

    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "student_id",
            name="uq_student_team_course",
        ),
        ForeignKeyConstraint(
            ["course_id", "team_id"],
            ["teams.course_id", "teams.id"],
        ),
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )

    course_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        nullable=False,
    )

    team_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        nullable=False,
    )

    student_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("student_profiles.id"),
        nullable=False,
    )

    joined_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        server_default=func.current_timestamp(),
    )

    team: Mapped["Team"] = relationship(
        "Team",
        back_populates="members",
    )

    student: Mapped["StudentProfile"] = relationship(
        "StudentProfile",
        back_populates="team_memberships",
    )

    def __repr__(self) -> str:
        return (
            f"<TeamMember(id={self.id}, "
            f"team_id={self.team_id}, "
            f"student_id={self.student_id})>"
        )


class TaskAssignment(Base):
    __tablename__ = "task_assignments"

    __table_args__ = (
        UniqueConstraint(
            "task_id",
            "student_id",
            name="uq_task_student",
        ),
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )

    task_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("team_tasks.id"),
        nullable=False,
    )

    student_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("student_profiles.id"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        Enum(
            "assigned",
            "in_progress",
            "submitted",
            "completed",
            name="assignment_status",
        ),
        nullable=False,
        default="assigned",
        server_default="assigned",
    )

    assigned_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        server_default=func.current_timestamp(),
    )

    task: Mapped["TeamTask"] = relationship(
        "TeamTask",
        back_populates="assignments",
    )

    student: Mapped["StudentProfile"] = relationship(
        "StudentProfile",
        back_populates="task_assignments",
    )

    contributions: Mapped[list["Contribution"]] = relationship(
        "Contribution",
        back_populates="assignment",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<TaskAssignment(id={self.id}, "
            f"task_id={self.task_id}, "
            f"student_id={self.student_id}, "
            f"status={self.status!r})>"
        )


class Contribution(Base):
    __tablename__ = "contributions"

    __table_args__ = (
        CheckConstraint(
            "hours_spent IS NULL OR hours_spent >= 0",
            name="chk_contribution_hours",
        ),
        Index(
            "idx_contributions_review",
            "review_status",
        ),
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )

    assignment_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("task_assignments.id"),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    hours_spent: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2),
        nullable=True,
    )

    evidence_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    submitted_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        server_default=func.current_timestamp(),
    )

    reviewed_by: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    review_status: Mapped[str] = mapped_column(
        Enum(
            "pending",
            "accepted",
            "rejected",
            name="contribution_review_status",
        ),
        nullable=False,
        default="pending",
        server_default="pending",
    )

    review_feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    assignment: Mapped["TaskAssignment"] = relationship(
        "TaskAssignment",
        back_populates="contributions",
    )

    reviewer: Mapped["User | None"] = relationship(
        "User",
        back_populates="contributions_reviewed",
        foreign_keys=[reviewed_by],
    )

    def __repr__(self) -> str:
        return (
            f"<Contribution(id={self.id}, "
            f"assignment_id={self.assignment_id}, "
            f"review_status={self.review_status!r})>"
        )