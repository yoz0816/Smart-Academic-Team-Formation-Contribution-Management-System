from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKeyConstraint,
    Integer,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class TaskSubmission(Base):
    __tablename__ = "task_submissions"

    __table_args__ = (
        UniqueConstraint(
            "task_assignee_id",
            name="uq_task_submissions_assignee",
        ),
        ForeignKeyConstraint(
            ["task_assignee_id", "task_id"],
            ["task_assignees.id", "task_assignees.task_id"],
            ondelete="CASCADE",
            name="fk_task_submissions_assignee_task",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    task_assignee_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    task_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    submission_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    task_assignee = relationship(
        "TaskAssignee",
        back_populates="submission",
    )