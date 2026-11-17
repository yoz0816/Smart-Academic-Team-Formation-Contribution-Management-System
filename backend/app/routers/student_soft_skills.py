from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.dependencies import require_csrf, require_roles
from app.database.session import get_db
from app.models import User
from app.schemas.student_soft_skill import (
    StudentSoftSkillCreate,
    StudentSoftSkillListResponse,
    StudentSoftSkillResponse,
    StudentSoftSkillUpdate,
)
from app.services.student_soft_skill_service import (
    create_student_soft_skill,
    delete_student_soft_skill,
    get_student_soft_skill,
    get_student_soft_skills,
    update_student_soft_skill,
)


router = APIRouter(
    prefix="/api/student/soft-skills",
    tags=["Student Soft Skills"],
)


@router.get("", response_model=StudentSoftSkillListResponse)
def list_soft_skills(
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    skills = get_student_soft_skills(db, current_user)

    return {
        "soft_skills": skills,
        "total": len(skills),
    }


@router.post(
    "",
    response_model=StudentSoftSkillResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_csrf)],
)
def add_soft_skill(
    data: StudentSoftSkillCreate,
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    try:
        return create_student_soft_skill(db, current_user, data)
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already added this soft skill.",
        ) from error


@router.put("/{skill_id}", response_model=StudentSoftSkillResponse, dependencies=[Depends(require_csrf)])
def edit_soft_skill(
    skill_id: int,
    data: StudentSoftSkillUpdate,
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    skill = get_student_soft_skill(db, current_user, skill_id)

    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Soft skill not found.",
        )

    try:
        return update_student_soft_skill(db, skill, data)
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already added this soft skill.",
        ) from error


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_csrf)])
def remove_soft_skill(
    skill_id: int,
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    skill = get_student_soft_skill(db, current_user, skill_id)

    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Soft skill not found.",
        )

    delete_student_soft_skill(db, skill)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
