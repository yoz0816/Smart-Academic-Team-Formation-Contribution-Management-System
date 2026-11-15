from datetime import datetime
from decimal import Decimal


from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from sqlalchemy import JSON

class Team(Base):
    __tablename__ = "teams"

    __table_args__ = (
        UniqueConstraint(
            "assignment_id",
            "team_number",
            name="uq_teams_assignment_number",
        ),
        UniqueConstraint(
            "id",
            "assignment_id",
            name="uq_teams_id_assignment",
        ),
        CheckConstraint(
            "status IN ('draft', 'pending_review', 'approved', 'published')",
            name="ck_teams_status",
        ),
        CheckConstraint(
            "formation_score IS NULL OR formation_score BETWEEN 0 AND 100",
            name="ck_teams_formation_score",
        ),
        CheckConstraint(
            "team_number >= 1",
            name="ck_teams_team_number",
        ),
        ForeignKeyConstraint(
    ["generation_batch_id", "assignment_id"],
    [
        "team_generation_batches.id",
        "team_generation_batches.assignment_id",
    ],
    ondelete="CASCADE",
    name="fk_teams_generation_batch_assignment",
),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    assignment_id: Mapped[int] = mapped_column(
        ForeignKey("academic_assignments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    team_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    team_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    formation_score: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2),
        nullable=True,
    )
    score_breakdown: Mapped[dict | None] = mapped_column(
    JSON,
    nullable=True,
)

    status: Mapped[str] = mapped_column(
        String(20),
        default="draft",
        server_default="draft",
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    assignment = relationship(
        "AcademicAssignment",
        back_populates="teams",
    )

    members = relationship(
        "TeamMember",
        back_populates="team",
        cascade="all, delete-orphan",
    )
    generation_batch_id: Mapped[int] = mapped_column(
    nullable=False,
    index=True,
)
    generation_batch = relationship(
    "TeamGenerationBatch",
    back_populates="teams",
    overlaps="assignment,teams",
)
    tasks = relationship(
    "Task",
    back_populates="team",
    cascade="all, delete-orphan",
)