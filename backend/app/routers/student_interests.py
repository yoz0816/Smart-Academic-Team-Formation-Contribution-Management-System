from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.database.session import get_db
from app.models import User
from app.schemas.student_interest import (
    StudentInterestResponse,
    StudentInterestUpdate,
)
from app.services.student_interest_service import (
    get_student_interests,
    update_student_interests,
)


router = APIRouter(
    prefix="/api/student/interests",
    tags=["Student Interests"],
)


@router.get("", response_model=StudentInterestResponse)
def list_interests(
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    interests = get_student_interests(db, current_user)

    return {
        "interests": interests,
        "total": len(interests),
    }


@router.put("", response_model=StudentInterestResponse)
def save_interests(
    data: StudentInterestUpdate,
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    interests = update_student_interests(db, current_user, data)

    return {
        "interests": interests,
        "total": len(interests),
    }
