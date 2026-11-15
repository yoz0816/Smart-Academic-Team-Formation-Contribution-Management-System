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


class StudentSkill(Base):
    __tablename__ = "student_skills"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "skill_name",
            name="uq_student_skills_user_skill",
        ),
        CheckConstraint(
            "category IN ('Programming Languages', 'Frameworks & Tools', "
            "'Databases', 'Mobile Development', 'UI/UX Design', "
            "'Testing & QA', 'Other')",
            name="ck_student_skills_category",
        ),
        CheckConstraint(
            "proficiency IN ('Beginner', 'Intermediate', 'Advanced', 'Expert')",
            name="ck_student_skills_proficiency",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    skill_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
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

    user = relationship("User", back_populates="skills")
