from __future__ import annotations

from sqlalchemy import (
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Skill(Base):
    __tablename__ = "skills"

    __table_args__ = (
        UniqueConstraint(
            "name",
            "category",
            name="uq_skill_name_category",
        ),
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        Enum("technical", "soft", name="skill_category"),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    student_skills: Mapped[list["StudentSkill"]] = relationship(
        "StudentSkill",
        back_populates="skill",
        cascade="all, delete-orphan",
    )
    course_requirements: Mapped[list["CourseRequiredSkill"]] = relationship(
        "CourseRequiredSkill",
        back_populates="skill",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Skill(id={self.id}, name={self.name!r}, "
            f"category={self.category!r})>"
        )


class StudentSkill(Base):
    __tablename__ = "student_skills"

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "skill_id",
            name="uq_student_skill",
        ),
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )

    student_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("student_profiles.id"),
        nullable=False,
    )

    skill_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("skills.id"),
        nullable=False,
    )

    proficiency_level: Mapped[str] = mapped_column(
        Enum(
            "beginner",
            "intermediate",
            "advanced",
            "expert",
            name="skill_proficiency",
        ),
        nullable=False,
    )

    student: Mapped["StudentProfile"] = relationship(
        "StudentProfile",
        back_populates="skills",
    )

    skill: Mapped["Skill"] = relationship(
        "Skill",
        back_populates="student_skills",
    )

    def __repr__(self) -> str:
        return (
            f"<StudentSkill(id={self.id}, "
            f"student_id={self.student_id}, "
            f"skill_id={self.skill_id}, "
            f"proficiency={self.proficiency_level!r})>"
        )