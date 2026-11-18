from typing import Literal

from pydantic import BaseModel, ConfigDict


ProblemSolvingCategory = Literal[
    "Logical Thinking",
    "Analytical Thinking",
    "Critical Thinking",
    "Creativity",
    "Decision-Making",
    "Technical Problem-Solving",
]

ProblemSolvingProficiency = Literal[
    "Beginner",
    "Intermediate",
    "Advanced",
    "Expert",
]


class StudentProblemSolvingCreate(BaseModel):
    category: ProblemSolvingCategory
    proficiency: ProblemSolvingProficiency


class StudentProblemSolvingUpdate(StudentProblemSolvingCreate):
    pass


class StudentProblemSolvingResponse(BaseModel):
    id: int
    category: str
    proficiency: str

    model_config = ConfigDict(from_attributes=True)


class StudentProblemSolvingListResponse(BaseModel):
    abilities: list[StudentProblemSolvingResponse]
    total: int
