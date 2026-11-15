from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class ContributionEvaluation(Base):
    __tablename__ = "contribution_evaluations"

    __table_args__ = (
        UniqueConstraint(
            "task_assignee_id",
            name="uq_contribution_evaluations_assignee",
        ),
        CheckConstraint(
            "score BETWEEN 0 AND 100",
            name="ck_contribution_evaluations_score",
        ),
        ForeignKeyConstraint(
            ["task_assignee_id", "task_id"],
            ["task_assignees.id", "task_assignees.task_id"],
            ondelete="CASCADE",
            name="fk_contribution_evaluations_assignee_task",
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

    evaluator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    task_assignee = relationship(
        "TaskAssignee",
        back_populates="evaluation",
    )

    evaluator = relationship(
        "User",
        back_populates="contribution_evaluations",
        foreign_keys=[evaluator_id],
    )