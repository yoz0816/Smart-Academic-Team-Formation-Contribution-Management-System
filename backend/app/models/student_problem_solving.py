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


PROBLEM_SOLVING_CATEGORIES = (
    "Logical Thinking",
    "Analytical Thinking",
    "Critical Thinking",
    "Creativity",
    "Decision-Making",
    "Technical Problem-Solving",
)

PROBLEM_SOLVING_PROFICIENCIES = (
    "Beginner",
    "Intermediate",
    "Advanced",
    "Expert",
)


class StudentProblemSolving(Base):
    __tablename__ = "student_problem_solving_abilities"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "category",
            name="uq_student_problem_solving_user_category",
        ),
        CheckConstraint(
            "category IN ('Logical Thinking', 'Analytical Thinking', "
            "'Critical Thinking', 'Creativity', 'Decision-Making', "
            "'Technical Problem-Solving')",
            name="ck_student_problem_solving_category",
        ),
        CheckConstraint(
            "proficiency IN ('Beginner', 'Intermediate', 'Advanced', 'Expert')",
            name="ck_student_problem_solving_proficiency",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    proficiency: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
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

    user = relationship("User", back_populates="problem_solving_abilities")
