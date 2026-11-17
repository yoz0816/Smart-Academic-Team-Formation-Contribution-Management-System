from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.dependencies import require_csrf, require_roles
from app.database.session import get_db
from app.models import User
from app.schemas.student_problem_solving import (
    StudentProblemSolvingCreate,
    StudentProblemSolvingListResponse,
    StudentProblemSolvingResponse,
    StudentProblemSolvingUpdate,
)
from app.services.student_problem_solving_service import (
    create_student_problem_solving_ability,
    delete_student_problem_solving_ability,
    get_student_problem_solving_abilities,
    get_student_problem_solving_ability,
    update_student_problem_solving_ability,
)


router = APIRouter(
    prefix="/api/student/problem-solving",
    tags=["Student Problem-Solving"],
)


@router.get("", response_model=StudentProblemSolvingListResponse)
def list_problem_solving_abilities(
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    abilities = get_student_problem_solving_abilities(db, current_user)

    return {
        "abilities": abilities,
        "total": len(abilities),
    }


@router.post(
    "",
    response_model=StudentProblemSolvingResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_csrf)],
)
def add_problem_solving_ability(
    data: StudentProblemSolvingCreate,
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    try:
        return create_student_problem_solving_ability(
            db,
            current_user,
            data,
        )
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already assessed this category.",
        ) from error


@router.put(
    "/{ability_id}",
    response_model=StudentProblemSolvingResponse,
    dependencies=[Depends(require_csrf)],
)
def edit_problem_solving_ability(
    ability_id: int,
    data: StudentProblemSolvingUpdate,
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    ability = get_student_problem_solving_ability(
        db,
        current_user,
        ability_id,
    )

    if ability is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem-solving assessment not found.",
        )

    try:
        return update_student_problem_solving_ability(db, ability, data)
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already assessed this category.",
        ) from error


@router.delete(
    "/{ability_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_csrf)],
)
def remove_problem_solving_ability(
    ability_id: int,
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    ability = get_student_problem_solving_ability(
        db,
        current_user,
        ability_id,
    )

    if ability is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem-solving assessment not found.",
        )

    delete_student_problem_solving_ability(db, ability)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
