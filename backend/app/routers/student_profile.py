from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.database.session import get_db
from app.models import User
from app.schemas.student_profile import (
    AcademicProfileResponse,
    AcademicProfileUpdate,
)
from app.services.student_profile_service import (
    calculate_completion,
    get_academic_profile,
    save_academic_profile,
)


router = APIRouter(
    prefix="/api/student/academic-profile",
    tags=["Student Academic Profile"],
)


def make_response(profile) -> AcademicProfileResponse:
    if profile is None:
        return AcademicProfileResponse()

    return AcademicProfileResponse(
        student_id=profile.student_id,
        university=profile.university,
        faculty=profile.faculty,
        department=profile.department,
        degree_program=profile.degree_program,
        year_of_study=profile.year_of_study,
        completion_percentage=calculate_completion(profile),
    )


@router.get(
    "",
    response_model=AcademicProfileResponse,
)
def read_academic_profile(
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    profile = get_academic_profile(db, current_user)
    return make_response(profile)


@router.put(
    "",
    response_model=AcademicProfileResponse,
)
def update_academic_profile(
    data: AcademicProfileUpdate,
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    try:
        profile = save_academic_profile(db, current_user, data)
        return make_response(profile)

    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="That student ID is already registered.",
        ) from error
