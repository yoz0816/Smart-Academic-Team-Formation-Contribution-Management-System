from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.database.session import get_db
from app.models import User
from app.schemas.preferred_teammate import (
    PreferredStudentResponse,
    PreferredTeammateUpdate,
    PreferredTeammatesResponse,
    StudentSearchResponse,
)
from app.services.preferred_teammate_service import (
    get_preferred_teammates,
    search_students,
    update_preferred_teammates,
)


router = APIRouter(
    prefix="/api/student/preferences",
    tags=["Student Preferred Teammates"],
)


@router.get(
    "/students",
    response_model=StudentSearchResponse,
)
def find_students(
    search: str = Query(default="", max_length=100),
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    students = search_students(db, current_user, search)

    return {
        "students": students,
        "total": len(students),
    }


@router.get(
    "",
    response_model=PreferredTeammatesResponse,
)
def read_preferences(
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    students = get_preferred_teammates(db, current_user)

    return {
        "preferred_teammates": students,
        "total": len(students),
        "max_allowed": 3,
    }


@router.put(
    "",
    response_model=PreferredTeammatesResponse,
)
def save_preferences(
    data: PreferredTeammateUpdate,
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    try:
        students = update_preferred_teammates(db, current_user, data)

        return {
            "preferred_teammates": students,
            "total": len(students),
            "max_allowed": 3,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
