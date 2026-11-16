from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.database.session import get_db
from app.models import User
from app.schemas.student_skill import (
    StudentSkillCreate,
    StudentSkillListResponse,
    StudentSkillResponse,
    StudentSkillUpdate,
)
from app.services.student_skill_service import (
    create_student_skill,
    delete_student_skill,
    get_student_skill,
    get_student_skills,
    update_student_skill,
)


router = APIRouter(
    prefix="/api/student/skills",
    tags=["Student Technical Skills"],
)


@router.get("", response_model=StudentSkillListResponse)
def list_skills(
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    skills = get_student_skills(db, current_user)

    return {
        "skills": skills,
        "total": len(skills),
    }


@router.post(
    "",
    response_model=StudentSkillResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_skill(
    data: StudentSkillCreate,
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    try:
        return create_student_skill(db, current_user, data)
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already added this skill.",
        ) from error


@router.put("/{skill_id}", response_model=StudentSkillResponse)
def edit_skill(
    skill_id: int,
    data: StudentSkillUpdate,
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    skill = get_student_skill(db, current_user, skill_id)

    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found.",
        )

    try:
        return update_student_skill(db, skill, data)
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already added this skill.",
        ) from error


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_skill(
    skill_id: int,
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    skill = get_student_skill(db, current_user, skill_id)

    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found.",
        )

    delete_student_skill(db, skill)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
