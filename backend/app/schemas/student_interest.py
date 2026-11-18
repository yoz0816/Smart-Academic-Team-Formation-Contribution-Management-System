from pydantic import BaseModel, Field, field_validator

from app.models.student_interest import INTERESTS

class StudentInterestUpdate(BaseModel):
    interests: list[str] = Field(max_length=14)

    @field_validator("interests")
    @classmethod
    def validate_interests(cls, values: list[str]) -> list[str]:
        if len(values) != len(set(values)):
            raise ValueError("Duplicate interests are not allowed.")

        invalid = set(values) - set(INTERESTS)

        if invalid:
            raise ValueError("One or more selected interests are invalid.")

        return values


class StudentInterestResponse(BaseModel):
    interests: list[str]
    total: int
