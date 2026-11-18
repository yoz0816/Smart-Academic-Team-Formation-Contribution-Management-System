from pydantic import BaseModel, ConfigDict, Field


class AcademicProfileUpdate(BaseModel):
    student_id: str | None = Field(default=None, max_length=50)
    university: str | None = Field(default=None, max_length=150)
    faculty: str | None = Field(default=None, max_length=150)
    department: str | None = Field(default=None, max_length=150)
    degree_program: str | None = Field(default=None, max_length=150)
    year_of_study: int | None = Field(default=None, ge=1, le=5)


class AcademicProfileResponse(BaseModel):
    student_id: str | None = None
    university: str | None = None
    faculty: str | None = None
    department: str | None = None
    degree_program: str | None = None
    year_of_study: int | None = None
    completion_percentage: int = 0

    model_config = ConfigDict(from_attributes=True)
