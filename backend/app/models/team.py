from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
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


class Team(Base):
    __tablename__ = "teams"

    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "id",
            name="uq_team_course_id",
        ),
        UniqueConstraint(
            "generation_id",
            "team_name",
            name="uq_team_name_generation",
        ),
        ForeignKeyConstraint(
            ["course_id", "generation_id"],
            ["team_generations.course_id", "team_generations.id"],
        ),
        Index(
            "idx_teams_generation",
            "generation_id",
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

    generation_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        nullable=False,
    )

    team_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        Enum(
            "pending",
            "approved",
            "rejected",
            name="team_status",
        ),
        nullable=False,
        default="pending",
        server_default="pending",
    )

    created_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        server_default=func.current_timestamp(),
    )

    generation: Mapped["TeamGeneration"] = relationship(
        "TeamGeneration",
        back_populates="teams",
    )

    members: Mapped[list["TeamMember"]] = relationship(
        "TeamMember",
        back_populates="team",
        cascade="all, delete-orphan",
    )

    score_breakdown: Mapped["TeamScoreBreakdown | None"] = relationship(
        "TeamScoreBreakdown",
        back_populates="team",
        uselist=False,
        cascade="all, delete-orphan",
    )

    tasks: Mapped[list["TeamTask"]] = relationship(
        "TeamTask",
        back_populates="team",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Team(id={self.id}, "
            f"team_name={self.team_name!r}, "
            f"status={self.status!r})>"
        )


class TeamScoreBreakdown(Base):
    __tablename__ = "team_score_breakdowns"

    __table_args__ = (
        CheckConstraint(
            "technical_score BETWEEN 0 AND 100 "
            "AND interest_score BETWEEN 0 AND 100 "
            "AND cgpa_score BETWEEN 0 AND 100 "
            "AND preference_score BETWEEN 0 AND 100 "
            "AND soft_skill_score BETWEEN 0 AND 100 "
            "AND problem_solving_score BETWEEN 0 AND 100 "
            "AND total_score BETWEEN 0 AND 100",
            name="chk_team_scores",
        ),
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )

    team_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("teams.id"),
        nullable=False,
        unique=True,
    )

    technical_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    interest_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    cgpa_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    preference_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    soft_skill_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    problem_solving_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    total_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    team: Mapped["Team"] = relationship(
        "Team",
        back_populates="score_breakdown",
    )

    def __repr__(self) -> str:
        return (
            f"<TeamScoreBreakdown(id={self.id}, "
            f"team_id={self.team_id}, "
            f"total_score={self.total_score})>"
        )


class TeamTask(Base):
    __tablename__ = "team_tasks"

    __table_args__ = (
        Index(
            "idx_tasks_team_status",
            "team_id",
            "status",
        ),
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )

    team_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("teams.id"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    deadline: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        Enum(
            "pending",
            "in_progress",
            "completed",
            "cancelled",
            name="task_status",
        ),
        nullable=False,
        default="pending",
        server_default="pending",
    )

    created_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        server_default=func.current_timestamp(),
    )

    team: Mapped["Team"] = relationship(
        "Team",
        back_populates="tasks",
    )

    assignments: Mapped[list["TaskAssignment"]] = relationship(
        "TaskAssignment",
        back_populates="task",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<TeamTask(id={self.id}, "
            f"title={self.title!r}, "
            f"status={self.status!r})>"
        )