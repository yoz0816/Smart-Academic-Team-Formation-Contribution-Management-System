from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

VerificationStatus = Literal["Pending", "Approved", "Rejected"]

class StudentAcademicExperienceCreate(BaseModel):
    cgpa: Decimal = Field(
        ge=Decimal("0.00"),
        le=Decimal("4.00"),
        max_digits=3,
        decimal_places=2,
    )


class StudentAcademicExperienceUpdate(StudentAcademicExperienceCreate):
    pass


class StudentAcademicExperienceResponse(BaseModel):
    id: int
    cgpa: Decimal
    status: VerificationStatus
    rejection_reason: str | None
    verified_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AcademicExperienceReviewItem(BaseModel):
    id: int
    student_id: int
    student_name: str
    student_email: str
    cgpa: Decimal
    status: VerificationStatus
    rejection_reason: str | None
    created_at: datetime
    updated_at: datetime
    verified_at: datetime | None


class AcademicExperienceReviewList(BaseModel):
    records: list[AcademicExperienceReviewItem]
    total: int


class AcademicExperienceReview(BaseModel):
    decision: Literal["Approved", "Rejected"]
    rejection_reason: str | None = Field(default=None, max_length=1000)

    @field_validator("rejection_reason")
    @classmethod
    def clean_rejection_reason(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None
