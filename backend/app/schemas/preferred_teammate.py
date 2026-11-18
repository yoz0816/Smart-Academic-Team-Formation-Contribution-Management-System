from pydantic import BaseModel, ConfigDict, Field, field_validator

class PreferredTeammateUpdate(BaseModel):
    preferred_user_ids: list[int] = Field(max_length=3)

    @field_validator("preferred_user_ids")
    @classmethod
    def validate_unique_ids(cls, values: list[int]) -> list[int]:
        if len(values) != len(set(values)):
            raise ValueError("Duplicate preferred teammates are not allowed.")

        return values


class PreferredStudentResponse(BaseModel):
    id: int
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class PreferredTeammatesResponse(BaseModel):
    preferred_teammates: list[PreferredStudentResponse]
    total: int
    max_allowed: int = 3


class StudentSearchResponse(BaseModel):
    students: list[PreferredStudentResponse]
    total: int
