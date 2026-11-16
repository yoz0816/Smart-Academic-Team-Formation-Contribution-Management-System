from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.database.session import get_db
from app.models import User
from app.schemas.student_academic_experience import (
    StudentAcademicExperienceCreate,
    StudentAcademicExperienceResponse,
    StudentAcademicExperienceUpdate,
)
from app.services.student_academic_experience_service import (
    create_student_academic_experience,
    get_student_academic_experience,
    update_student_academic_experience,
)


router = APIRouter(
    prefix="/api/student/academic-experience",
    tags=["Student Academic Experience"],
)


@router.get("", response_model=StudentAcademicExperienceResponse | None)
def get_my_academic_experience(
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    return get_student_academic_experience(db, current_user)


@router.post(
    "",
    response_model=StudentAcademicExperienceResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_academic_experience(
    data: StudentAcademicExperienceCreate,
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    existing = get_student_academic_experience(db, current_user)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already submitted your CGPA. Edit your existing record instead.",
        )

    return create_student_academic_experience(db, current_user, data)


@router.put("", response_model=StudentAcademicExperienceResponse)
def edit_academic_experience(
    data: StudentAcademicExperienceUpdate,
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    record = get_student_academic_experience(db, current_user)

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submit your CGPA before trying to edit it.",
        )

    return update_student_academic_experience(db, record, data)
