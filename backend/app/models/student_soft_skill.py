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


SOFT_SKILLS = (
    "Communication",
    "Leadership",
    "Teamwork",
    "Time Management",
    "Adaptability",
    "Responsibility",
)

SOFT_SKILL_PROFICIENCIES = (
    "Beginner",
    "Intermediate",
    "Advanced",
    "Expert",
)


class StudentSoftSkill(Base):
    __tablename__ = "student_soft_skills"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "skill_name",
            name="uq_student_soft_skills_user_skill",
        ),
        CheckConstraint(
            "skill_name IN ('Communication', 'Leadership', 'Teamwork', "
            "'Time Management', 'Adaptability', 'Responsibility')",
            name="ck_student_soft_skills_name",
        ),
        CheckConstraint(
            "proficiency IN ('Beginner', 'Intermediate', 'Advanced', 'Expert')",
            name="ck_student_soft_skills_proficiency",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    skill_name: Mapped[str] = mapped_column(
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

    user = relationship("User", back_populates="soft_skills")
