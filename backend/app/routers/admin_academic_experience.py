from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.database.session import get_db
from app.models import StudentAcademicExperience, User
from app.schemas.student_academic_experience import (
    AcademicExperienceReview,
    AcademicExperienceReviewItem,
    AcademicExperienceReviewList,
    StudentAcademicExperienceResponse,
)
from app.services.student_academic_experience_service import (
    review_student_academic_experience,
)


router = APIRouter(
    prefix="/api/admin/academic-experience",
    tags=["Admin - CGPA Verification"],
)


@router.get("", response_model=AcademicExperienceReviewList)
def list_academic_experience_records(
    record_status: Literal["Pending", "Approved", "Rejected"] | None = Query(
        default=None,
        alias="status",
    ),
    current_admin: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    query = (
        db.query(StudentAcademicExperience, User)
        .join(User, StudentAcademicExperience.user_id == User.id)
    )

    if record_status:
        query = query.filter(StudentAcademicExperience.status == record_status)

    results = query.order_by(
        StudentAcademicExperience.created_at.desc()
    ).all()

    records = [
        AcademicExperienceReviewItem(
            id=record.id,
            student_id=student.id,
            student_name=student.full_name,
            student_email=student.email,
            cgpa=record.cgpa,
            status=record.status,
            rejection_reason=record.rejection_reason,
            created_at=record.created_at,
            updated_at=record.updated_at,
            verified_at=record.verified_at,
        )
        for record, student in results
    ]

    return {"records": records, "total": len(records)}


@router.patch(
    "/{record_id}/review",
    response_model=StudentAcademicExperienceResponse,
)
def review_academic_experience(
    record_id: int,
    data: AcademicExperienceReview,
    current_admin: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    record = db.query(StudentAcademicExperience).filter(
        StudentAcademicExperience.id == record_id
    ).first()

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Academic experience record not found.",
        )
    if record.status != "Pending":
        raise HTTPException(
            status_code=409,
            detail="Only pending CGPA records can be reviewed.",
        )

    if data.decision == "Rejected" and not data.rejection_reason:
        raise HTTPException(
            status_code=422,
            detail="A rejection reason is required.",
        )

    if data.decision == "Approved" and data.rejection_reason:
        raise HTTPException(
            status_code=422,
            detail="A rejection reason is only allowed when rejecting a record.",
        )

    return review_student_academic_experience(
        db=db,
        record=record,
        administrator=current_admin,
        decision=data.decision,
        rejection_reason=data.rejection_reason,
    )
