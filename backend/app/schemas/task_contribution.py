
from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


TaskPriority = Literal["low", "medium", "high", "urgent"]

TaskStatus = Literal[
    "open",
    "in_progress",
    "completed",
    "cancelled",
]

TaskAssigneeStatus = Literal[
    "pending",
    "in_progress",
    "submitted",
    "completed",
]

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    description: str = Field(min_length=1)
    priority: TaskPriority = "medium"
    deadline: datetime
    student_ids: list[int] = Field(min_length=1)

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Task title cannot be empty.")

        return value

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Task description cannot be empty.")

        return value

    @field_validator("student_ids")
    @classmethod
    def validate_student_ids(cls, value: list[int]) -> list[int]:
        if any(student_id <= 0 for student_id in value):
            raise ValueError("Student IDs must be positive integers.")

        if len(value) != len(set(value)):
            raise ValueError("Duplicate student IDs are not allowed.")

        return value


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    description: str | None = Field(default=None, min_length=1)
    priority: TaskPriority | None = None
    deadline: datetime | None = None

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Task title cannot be empty.")

        return value

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Task description cannot be empty.")

        return value



class StudentTaskStatusUpdate(BaseModel):
    status: Literal["pending", "in_progress"]


class TaskSubmissionCreate(BaseModel):
    submission_text: str = Field(min_length=1)

    @field_validator("submission_text")
    @classmethod
    def clean_submission_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Submission cannot be empty.")

        return value


class TaskSubmissionResponse(BaseModel):
    id: int
    task_assignee_id: int
    task_id: int
    submission_text: str
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContributionEvaluationCreate(BaseModel):
    score: float = Field(ge=0, le=100)
    feedback: str | None = None

    @field_validator("feedback")
    @classmethod
    def clean_feedback(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        return value or None


class ContributionEvaluationResponse(BaseModel):
    id: int
    task_assignee_id: int
    task_id: int
    evaluator_id: int
    score: float
    feedback: str | None
    evaluated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskAssigneeResponse(BaseModel):
    id: int
    task_id: int
    team_member_id: int
    student_id: int
    status: str
    assigned_at: datetime
    status_updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TaskResponse(BaseModel):
    id: int
    team_id: int
    assignment_id: int
    title: str
    description: str
    priority: str
    status: str
    deadline: datetime
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskAssigneeDetailResponse(TaskAssigneeResponse):
    student_full_name: str
    student_email: str
    submission: TaskSubmissionResponse | None = None
    evaluation: ContributionEvaluationResponse | None = None


class TaskDetailResponse(TaskResponse):
    assignees: list[TaskAssigneeDetailResponse] = Field(default_factory=list)


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    total: int


class StudentTaskResponse(BaseModel):
    id: int
    assignee_id: int
    task_id: int
    title: str
    description: str
    priority: str
    task_status: str
    deadline: datetime
    my_status: str
    assigned_at: datetime
    status_updated_at: datetime
    submission: TaskSubmissionResponse | None = None
    evaluation: ContributionEvaluationResponse | None = None


class StudentTaskListResponse(BaseModel):
    tasks: list[StudentTaskResponse]
    total: int
