from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class AcademicAssignment(Base):
    __tablename__ = "academic_assignments"

    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "title",
            name="uq_academic_assignments_course_title",
        ),
        CheckConstraint(
            "status IN ('draft', 'published', 'closed')",
            name="ck_academic_assignments_status",
        ),
        CheckConstraint(
            "deadline > opens_at",
            name="ck_academic_assignments_dates",
        ),
        CheckConstraint(
            """
            proposal_deadline IS NULL
            OR proposal_opens_at IS NULL
            OR proposal_deadline > proposal_opens_at
            """,
            name="ck_academic_assignments_proposal_dates",
        ),
        CheckConstraint(
            """
            modification_deadline IS NULL
            OR proposal_deadline IS NULL
            OR modification_deadline >= proposal_deadline
            """,
            name="ck_academic_assignments_modification_deadline",
        ),
        CheckConstraint(
            """
            final_submission_deadline IS NULL
            OR modification_deadline IS NULL
            OR final_submission_deadline >= modification_deadline
            """,
            name="ck_academic_assignments_final_deadline",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    lecturer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(180),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    instructions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    opens_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    deadline: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    proposal_opens_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    proposal_deadline: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    modification_deadline: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    final_submission_deadline: Mapped[datetime | None] = mapped_column(
        DateTime,
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

    course = relationship(
        "Course",
        back_populates="assignments",
    )

    lecturer = relationship(
        "User",
        back_populates="academic_assignments",
    )
    teams = relationship(
        "Team",
        back_populates="assignment",
        cascade="all, delete-orphan",
    )
    generation_batches = relationship(
    "TeamGenerationBatch",
    back_populates="assignment",
    cascade="all, delete-orphan",
)
    eligible_students = relationship(
    "AssignmentEligibleStudent",
    back_populates="assignment",
    cascade="all, delete-orphan",
)
    required_skills = relationship(
    "AssignmentRequiredSkill",
    back_populates="assignment",
    cascade="all, delete-orphan",
)
