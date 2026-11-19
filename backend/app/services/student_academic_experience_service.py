from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import StudentAcademicExperience, User
from app.schemas.student_academic_experience import (
    StudentAcademicExperienceCreate,
    StudentAcademicExperienceUpdate,
)


def get_student_academic_experience(
    db: Session,
    user: User,
) -> StudentAcademicExperience | None:
    return (
        db.query(StudentAcademicExperience)
        .filter(StudentAcademicExperience.user_id == user.id)
        .first()
    )


def create_student_academic_experience(
    db: Session,
    user: User,
    data: StudentAcademicExperienceCreate,
) -> StudentAcademicExperience:
    record = StudentAcademicExperience(
        user_id=user.id,
        cgpa=data.cgpa,
        status="Pending",
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def update_student_academic_experience(
    db: Session,
    record: StudentAcademicExperience,
    data: StudentAcademicExperienceUpdate,
) -> StudentAcademicExperience:
    record.cgpa = data.cgpa
    record.status = "Pending"
    record.rejection_reason = None
    record.verified_by = None
    record.verified_at = None

    db.commit()
    db.refresh(record)

    return record


def review_student_academic_experience(
    db: Session,
    record: StudentAcademicExperience,
    administrator: User,
    decision: str,
    rejection_reason: str | None,
) -> StudentAcademicExperience:
    record.status = decision
    record.verified_by = administrator.id
    record.verified_at = datetime.now(timezone.utc).replace(tzinfo=None)

    if decision == "Rejected":
        record.rejection_reason = rejection_reason
    else:
        record.rejection_reason = None

    db.commit()
    db.refresh(record)

    return record
