from __future__ import annotations

from datetime import datetime

from sqlalchemy import Enum, ForeignKey, Index, String, Text, TIMESTAMP, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Course(Base):
    __tablename__ = "courses"

    __table_args__ = (
        Index("idx_courses_status", "status"),
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )

    course_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    course_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    academic_year: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    semester: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        Enum("active", "inactive", name="course_status"),
        nullable=False,
        default="active",
        server_default="active",
    )

    created_by: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        server_default=func.current_timestamp(),
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    creator: Mapped["User"] = relationship(
        "User",
        back_populates="courses_created",
    )

    requirement: Mapped["CourseRequirement | None"] = relationship(
        "CourseRequirement",
        back_populates="course",
        uselist=False,
        cascade="all, delete-orphan",
    )

    required_skills: Mapped[list["CourseRequiredSkill"]] = relationship(
        "CourseRequiredSkill",
        back_populates="course",
        cascade="all, delete-orphan",
    )
    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment",
        back_populates="course",
        cascade="all, delete-orphan",
    )

    team_generations: Mapped[list["TeamGeneration"]] = relationship(
        "TeamGeneration",
        back_populates="course",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Course(id={self.id}, "
            f"course_code={self.course_code!r}, "
            f"course_name={self.course_name!r})>"
        )