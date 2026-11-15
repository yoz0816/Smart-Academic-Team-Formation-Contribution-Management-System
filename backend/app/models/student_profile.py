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


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_student_profiles_user_id"),
        UniqueConstraint("student_id", name="uq_student_profiles_student_id"),
        CheckConstraint(
            "year_of_study IS NULL OR year_of_study BETWEEN 1 AND 5",
            name="ck_student_profiles_year_of_study",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    student_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    university: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    faculty: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    department: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    degree_program: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    year_of_study: Mapped[int | None] = mapped_column(
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

    user = relationship("User", back_populates="academic_profile")
