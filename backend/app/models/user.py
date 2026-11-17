from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
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

    sessions = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    academic_profile = relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    skills = relationship(
        "StudentSkill",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    interests = relationship(
        "StudentInterest",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    sent_preferences = relationship(
        "PreferredTeammate",
        foreign_keys="PreferredTeammate.user_id",
        back_populates="student",
        cascade="all, delete-orphan",
    )

    received_preferences = relationship(
        "PreferredTeammate",
        foreign_keys="PreferredTeammate.preferred_user_id",
        back_populates="preferred_student",
        passive_deletes=True,
    )

    soft_skills = relationship(
        "StudentSoftSkill",
        back_populates="user",
        cascade="all, delete-orphan",
    )


    problem_solving_abilities = relationship(
        "StudentProblemSolving",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    courses = relationship(
        "Course",
        back_populates="lecturer",
    )
    academic_assignments = relationship(
        "AcademicAssignment",
        back_populates="lecturer",
    )
    team_memberships = relationship(
        "TeamMember",
        back_populates="student",
        foreign_keys="TeamMember.user_id",
        cascade="all, delete-orphan",
    )
    generated_team_batches = relationship(
    "TeamGenerationBatch",
    back_populates="admin",
    foreign_keys="TeamGenerationBatch.generated_by",
)
    assignment_eligibility_entries = relationship(
    "AssignmentEligibleStudent",
    back_populates="student",
    foreign_keys="AssignmentEligibleStudent.student_id",
    cascade="all, delete-orphan",
)
    created_tasks = relationship(
    "Task",
    back_populates="creator",
    foreign_keys="Task.created_by",
)
    contribution_evaluations = relationship(
        "ContributionEvaluation",
        back_populates="evaluator",
        foreign_keys="ContributionEvaluation.evaluator_id",
    )
    notifications_received = relationship(
        "Notification",
        foreign_keys="Notification.recipient_id",
        back_populates="recipient",
        cascade="all, delete-orphan",
    )

    notifications_sent = relationship(
        "Notification",
        foreign_keys="Notification.actor_id",
        back_populates="actor",
    )
