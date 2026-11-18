from typing import Literal

from pydantic import BaseModel, ConfigDict


SoftSkillName = Literal[
    "Communication",
    "Leadership",
    "Teamwork",
    "Time Management",
    "Adaptability",
    "Responsibility",
]

SoftSkillProficiency = Literal[
    "Beginner",
    "Intermediate",
    "Advanced",
    "Expert",
]


class StudentSoftSkillCreate(BaseModel):
    skill_name: SoftSkillName
    proficiency: SoftSkillProficiency


class StudentSoftSkillUpdate(StudentSoftSkillCreate):
    pass


class StudentSoftSkillResponse(BaseModel):
    id: int
    skill_name: str
    proficiency: str

    model_config = ConfigDict(from_attributes=True)


class StudentSoftSkillListResponse(BaseModel):
    soft_skills: list[StudentSoftSkillResponse]
    total: int
