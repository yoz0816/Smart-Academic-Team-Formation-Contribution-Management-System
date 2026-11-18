from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


SkillCategory = Literal[
    "Programming Languages",
    "Frameworks & Tools",
    "Databases",
    "Mobile Development",
    "UI/UX Design",
    "Testing & QA",
    "Other",
]

SkillProficiency = Literal[
    "Beginner",
    "Intermediate",
    "Advanced",
    "Expert",
]


class StudentSkillCreate(BaseModel):
    skill_name: str = Field(min_length=1, max_length=100)
    category: SkillCategory
    proficiency: SkillProficiency

    @field_validator("skill_name")
    @classmethod
    def clean_skill_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Skill name cannot be empty.")

        return value


class StudentSkillUpdate(StudentSkillCreate):
    pass


class StudentSkillResponse(BaseModel):
    id: int
    skill_name: str
    category: str
    proficiency: str

    model_config = ConfigDict(from_attributes=True)


class StudentSkillListResponse(BaseModel):
    skills: list[StudentSkillResponse]
    total: int
