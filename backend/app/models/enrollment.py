from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    TIMESTAMP,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Enrollment(Base):
    __tablename__ = "enrollments"

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "course_id",
            name="uq_student_course",
        ),
        Index(
            "idx_enrollment_course_status",
            "course_id",
            "enrollment_status",
            "eligibility_status",
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

    course_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("courses.id"),
        nullable=False,
    )

    enrollment_status: Mapped[str] = mapped_column(
        Enum(
            "enrolled",
            "withdrawn",
            "completed",
            name="enrollment_status",
        ),
        nullable=False,
        default="enrolled",
        server_default="enrolled",
    )

    eligibility_status: Mapped[str] = mapped_column(
        Enum(
            "pending",
            "eligible",
            "not_eligible",
            name="eligibility_status",
        ),
        nullable=False,
        default="pending",
        server_default="pending",
    )

    enrolled_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        server_default=func.current_timestamp(),
    )

    student: Mapped["StudentProfile"] = relationship(
        "StudentProfile",
        back_populates="enrollments",
    )

    course: Mapped["Course"] = relationship(
        "Course",
        back_populates="enrollments",
    )

    eligibility_checks: Mapped[list["EligibilityCheck"]] = relationship(
        "EligibilityCheck",
        back_populates="enrollment",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Enrollment(id={self.id}, "
            f"student_id={self.student_id}, "
            f"course_id={self.course_id}, "
            f"status={self.enrollment_status!r})>"
        )


class EligibilityCheck(Base):
    __tablename__ = "eligibility_checks"

    __table_args__ = (
        Index(
            "idx_eligibility_enrollment",
            "enrollment_id",
            "checked_at",
        ),
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )

    enrollment_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("enrollments.id"),
        nullable=False,
    )

    result: Mapped[str] = mapped_column(
        Enum(
            "eligible",
            "not_eligible",
            name="eligibility_result",
        ),
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    checked_by: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    checked_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP,
        nullable=True,
        server_default=func.current_timestamp(),
    )

    enrollment: Mapped["Enrollment"] = relationship(
        "Enrollment",
        back_populates="eligibility_checks",
    )

    checked_by_user: Mapped["User | None"] = relationship(
        "User",
        back_populates="eligibility_checks_performed",
        foreign_keys=[checked_by],
    )

    def __repr__(self) -> str:
        return (
            f"<EligibilityCheck(id={self.id}, "
            f"enrollment_id={self.enrollment_id}, "
            f"result={self.result!r})>"
        )