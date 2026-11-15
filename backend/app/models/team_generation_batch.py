from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class TeamGenerationBatch(Base):
    __tablename__ = "team_generation_batches"

    __table_args__ = (
        UniqueConstraint(
            "assignment_id",
            "batch_number",
            name="uq_generation_batches_assignment_number",
        ),
        CheckConstraint(
            "batch_number >= 1",
            name="ck_generation_batches_batch_number",
        ),
        CheckConstraint(
            "total_students >= 0 AND total_teams >= 0",
            name="ck_generation_batches_counts",
        ),
        CheckConstraint(
            "average_formation_score IS NULL "
            "OR average_formation_score BETWEEN 0 AND 100",
            name="ck_generation_batches_average_score",
        ),
        UniqueConstraint(
            "id",
            "assignment_id",
            name="uq_generation_batches_id_assignment",
        ),
        CheckConstraint(
            """
            status IN (
                'generated',
                'pending_review',
                'approved',
                'published',
                'rejected',
                'superseded'
            )
            """,
            name="ck_generation_batches_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    assignment_id: Mapped[int] = mapped_column(
        ForeignKey("academic_assignments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    generated_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    batch_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    total_students: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )

    total_teams: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )

    average_formation_score: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="generated",
        server_default="generated",
        nullable=False,
        index=True,
    )

    review_notes: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
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
        back_populates="generation_batches",
    )

    admin = relationship(
        "User",
        back_populates="generated_team_batches",
        foreign_keys=[generated_by],
    )

    teams = relationship(
    "Team",
    back_populates="generation_batch",
    cascade="all, delete-orphan",
    overlaps="assignment,teams",
)