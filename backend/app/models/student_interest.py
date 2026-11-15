from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


INTERESTS = (
    "Web Development",
    "Mobile Application Development",
    "Desktop Application Development",
    "Cybersecurity",
    "Data Science & Analytics",
    "Database Systems",
    "Cloud Computing & DevOps",
    "Computer Networking",
    "Internet of Things (IoT)",
    "UI/UX Design",
    "Software Testing & Quality Assurance",
    "Game Development",
    "Operating Systems",
    "Software Engineering & Architecture",
)


class StudentInterest(Base):
    __tablename__ = "student_interests"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "interest_name",
            name="uq_student_interests_user_interest",
        ),
        CheckConstraint(
            "interest_name IN ("
            + ", ".join(f"'{interest}'" for interest in INTERESTS)
            + ")",
            name="ck_student_interests_valid_interest",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    interest_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="interests")
