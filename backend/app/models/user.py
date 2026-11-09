
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Enum, Index, String, TIMESTAMP, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        Index("idx_users_role_status", "role", "account_status"),
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        Enum("student", "admin", name="user_role"),
        nullable=False,
        default="student",
        server_default="student",
    )

    account_status: Mapped[str] = mapped_column(
        Enum(
            "active",
            "inactive",
            "suspended",
            name="account_status",
        ),
        nullable=False,
        default="active",
        server_default="active",
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

    student_profile: Mapped["StudentProfile | None"] = relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
    )
    courses_created: Mapped[list["Course"]] = relationship(
        "Course",
        back_populates="creator",
    )
    eligibility_checks_performed: Mapped[list["EligibilityCheck"]] = relationship(
        "EligibilityCheck",
        back_populates="checked_by_user",
        foreign_keys="EligibilityCheck.checked_by",
    )

    team_generations_created: Mapped[list["TeamGeneration"]] = relationship(
        "TeamGeneration",
        back_populates="generated_by_user",
        foreign_keys="TeamGeneration.generated_by",
    )

    team_generations_approved: Mapped[list["TeamGeneration"]] = relationship(
        "TeamGeneration",
        back_populates="approved_by_user",
        foreign_keys="TeamGeneration.approved_by",
    )
    contributions_reviewed: Mapped[list["Contribution"]] = relationship(
        "Contribution",
        back_populates="reviewer",
        foreign_keys="Contribution.reviewed_by",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email!r}, role={self.role!r})>"
