from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


TASK_ASSIGNEE_STATUSES = (
    "pending",
    "in_progress",
    "submitted",
    "completed",
)


class TaskAssignee(Base):
    __tablename__ = "task_assignees"

    __table_args__ = (
        UniqueConstraint(
            "id",
            "task_id",
            name="uq_task_assignees_id_task",
        ),
        UniqueConstraint(
            "task_id",
            "team_member_id",
            name="uq_task_assignees_task_member",
        ),
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'submitted', 'completed')",
            name="ck_task_assignees_status",
        ),
        ForeignKeyConstraint(
            ["task_id", "team_id", "assignment_id"],
            ["tasks.id", "tasks.team_id", "tasks.assignment_id"],
            ondelete="CASCADE",
            name="fk_task_assignees_task_team_assignment",
        ),
        ForeignKeyConstraint(
            ["team_member_id", "team_id", "assignment_id", "student_id"],
            [
                "team_members.id",
                "team_members.team_id",
                "team_members.assignment_id",
                "team_members.user_id",
            ],
            ondelete="CASCADE",
            name="fk_task_assignees_team_member",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    task_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    team_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    assignment_id: Mapped[int] = mapped_column(Integer, nullable=False)
    team_member_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    student_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        server_default="pending",
        nullable=False,
        index=True,
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    status_updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    task = relationship(
        "Task",
        back_populates="assignees",
        overlaps="task_assignments",
    )

    team_member = relationship(
        "TeamMember",
        back_populates="task_assignments",
        foreign_keys=[
            team_member_id,
            team_id,
            assignment_id,
            student_id,
        ],
        overlaps="task,assignees",
    )

    @property
    def student(self):
        return self.team_member.student

    submission = relationship(
        "TaskSubmission",
        back_populates="task_assignee",
        uselist=False,
        cascade="all, delete-orphan",
    )

    evaluation = relationship(
        "ContributionEvaluation",
        back_populates="task_assignee",
        uselist=False,
        cascade="all, delete-orphan",
    )