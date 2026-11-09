from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKey,
    Numeric,
    String,
    TIMESTAMP,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class TeamGeneration(Base):
    __tablename__ = "team_generations"

    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "id",
            name="uq_generation_course",
        ),
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )

    course_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("courses.id"),
        nullable=False,
    )

    generated_by: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        Enum(
            "draft",
            "generated",
            "approved",
            "rejected",
            name="generation_status",
        ),
        nullable=False,
        default="draft",
        server_default="draft",
    )

    generated_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
    )

    approved_by: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
    )

    created_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        server_default=func.current_timestamp(),
    )

    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="team_generations",
    )

    generated_by_user: Mapped["User"] = relationship(
        "User",
        back_populates="team_generations_created",
        foreign_keys=[generated_by],
    )

    approved_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="team_generations_approved",
        foreign_keys=[approved_by],
    )

    criteria: Mapped[list["TeamGenerationCriteria"]] = relationship(
        "TeamGenerationCriteria",
        back_populates="generation",
        cascade="all, delete-orphan",
    )
    teams: Mapped[list["Team"]] = relationship(
        "Team",
        back_populates="generation",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<TeamGeneration(id={self.id}, "
            f"course_id={self.course_id}, "
            f"status={self.status!r})>"
        )


class TeamGenerationCriteria(Base):
    __tablename__ = "team_generation_criteria"

    __table_args__ = (
        UniqueConstraint(
            "generation_id",
            "criterion",
            name="uq_generation_criterion",
        ),
        CheckConstraint(
            "weight BETWEEN 0 AND 100",
            name="chk_criterion_weight",
        ),
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )

    generation_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("team_generations.id"),
        nullable=False,
    )

    criterion: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    weight: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    generation: Mapped["TeamGeneration"] = relationship(
        "TeamGeneration",
        back_populates="criteria",
    )

    def __repr__(self) -> str:
        return (
            f"<TeamGenerationCriteria(id={self.id}, "
            f"criterion={self.criterion!r}, "
            f"weight={self.weight})>"
        )