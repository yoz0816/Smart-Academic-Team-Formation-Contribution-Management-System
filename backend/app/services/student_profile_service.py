from sqlalchemy.orm import Session

from app.models import StudentProfile, User
from app.schemas.student_profile import AcademicProfileUpdate


PROFILE_FIELDS = (
    "student_id",
    "university",
    "faculty",
    "department",
    "degree_program",
    "year_of_study",
)


def get_academic_profile(db: Session, user: User) -> StudentProfile | None:
    return (
        db.query(StudentProfile)
        .filter(StudentProfile.user_id == user.id)
        .first()
    )


def calculate_completion(profile: StudentProfile | None) -> int:
    if profile is None:
        return 0

    completed = sum(
        1 for field in PROFILE_FIELDS
        if getattr(profile, field) is not None
        and getattr(profile, field) != ""
    )

    return round((completed / len(PROFILE_FIELDS)) * 100)


def save_academic_profile(
    db: Session,
    user: User,
    data: AcademicProfileUpdate,
) -> StudentProfile:
    profile = get_academic_profile(db, user)

    if profile is None:
        profile = StudentProfile(user_id=user.id)
        db.add(profile)

    values = data.model_dump()

    for field, value in values.items():
        if isinstance(value, str):
            value = value.strip() or None

        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return profile
