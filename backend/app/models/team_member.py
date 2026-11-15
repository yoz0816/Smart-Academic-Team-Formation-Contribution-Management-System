from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class TeamMember(Base):
    __tablename__ = "team_members"

    __table_args__ = (
        UniqueConstraint(
            "assignment_id",
            "user_id",
            name="uq_team_members_assignment_user",
        ),
        ForeignKeyConstraint(
            ["team_id", "assignment_id"],
            ["teams.id", "teams.assignment_id"],
            ondelete="CASCADE",
            name="fk_team_members_team_assignment",
        ),
        UniqueConstraint(
            "id",
            "team_id",
            "assignment_id",
            "user_id",
            name="uq_team_members_id_team_assignment_user",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    team_id: Mapped[int] = mapped_column(
        nullable=False,
        index=True,
    )

    assignment_id: Mapped[int] = mapped_column(
        nullable=False,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    team = relationship(
        "Team",
        back_populates="members",
    )

    student = relationship(
        "User",
        back_populates="team_memberships",
        foreign_keys=[user_id],
    )
    task_assignments = relationship(
    "TaskAssignee",
    back_populates="team_member",
    cascade="all, delete-orphan",
    overlaps="student,task_assignments",
)