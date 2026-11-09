from __future__ import annotations

from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.mysql import BIGINT, TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class CourseRequirement(Base):
    __tablename__ = "course_requirements"

    __table_args__ = (
        CheckConstraint(
            "minimum_cgpa IS NULL OR "
            "(minimum_cgpa >= 0 AND minimum_cgpa <= cgpa_scale)",
            name="chk_course_minimum_cgpa",
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
        unique=True,
    )

    minimum_cgpa: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    cgpa_scale: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("4.00"),
        server_default="4.00",
    )

    minimum_year: Mapped[int | None] = mapped_column(
        TINYINT(unsigned=True),
        nullable=True,
    )

    additional_requirements: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="requirement",
    )

    def __repr__(self) -> str:
        return (
            f"<CourseRequirement(id={self.id}, "
            f"course_id={self.course_id})>"
        )


class CourseRequiredSkill(Base):
    __tablename__ = "course_required_skills"

    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "skill_id",
            name="uq_course_required_skill",
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

    skill_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("skills.id"),
        nullable=False,
    )

    minimum_proficiency: Mapped[str] = mapped_column(
        Enum(
            "beginner",
            "intermediate",
            "advanced",
            "expert",
            name="required_skill_proficiency",
        ),
        nullable=False,
        default="beginner",
        server_default="beginner",
    )

    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="required_skills",
    )

    skill: Mapped["Skill"] = relationship(
        "Skill",
        back_populates="course_requirements",
    )

    def __repr__(self) -> str:
        return (
            f"<CourseRequiredSkill(id={self.id}, "
            f"course_id={self.course_id}, "
            f"skill_id={self.skill_id})>"
        )