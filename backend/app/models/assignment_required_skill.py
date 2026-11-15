from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class AssignmentRequiredSkill(Base):
    __tablename__ = "assignment_required_skills"

    __table_args__ = (
        UniqueConstraint(
            "assignment_id",
            "skill_name",
            name="uq_assignment_required_skill",
        ),
        CheckConstraint(
            "required_proficiency IN "
            "('Beginner', 'Intermediate', 'Advanced', 'Expert')",
            name="ck_assignment_required_skill_proficiency",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    assignment_id: Mapped[int] = mapped_column(
        ForeignKey("academic_assignments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    skill_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    required_proficiency: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    assignment = relationship(
        "AcademicAssignment",
        back_populates="required_skills",
    )