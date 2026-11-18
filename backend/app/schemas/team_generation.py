from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field
from typing import Literal
from pydantic import BaseModel, Field, field_validator


BatchStatus = Literal[
    "generated",
    "pending_review",
    "approved",
    "published",
    "rejected",
    "superseded",
]


class TeamGenerationRequest(BaseModel):
    number_of_teams: int = Field(ge=1, le=500)


class TeamScoreBreakdown(BaseModel):
    criteria: dict[str, float]
    weighted_contributions: dict[str, float]
    total_score: float


class GeneratedTeamResponse(BaseModel):
    team_number: int
    member_ids: list[int]
    member_count: int
    score: TeamScoreBreakdown


class TeamGenerationResponse(BaseModel):
    message: str
    batch_id: int
    assignment_id: int
    batch_number: int
    status: BatchStatus
    total_students: int
    total_teams: int
    average_formation_score: float
    initial_average_score: float
    improvement: float
    iterations: int
    teams: list[GeneratedTeamResponse]


class TeamGenerationBatchResponse(BaseModel):
    id: int
    assignment_id: int
    generated_by: int
    batch_number: int
    total_students: int
    total_teams: int
    average_formation_score: Decimal | None
    status: BatchStatus
    review_notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TeamGenerationBatchListResponse(BaseModel):
    batches: list[TeamGenerationBatchResponse]
    total: int

class TeamMemberReviewResponse(BaseModel):
    user_id: int
    full_name: str
    email: str


class TeamReviewResponse(BaseModel):
    id: int
    team_number: int
    team_name: str
    formation_score: Decimal | None
    score_breakdown: TeamScoreBreakdown | None
    status: Literal[
        "draft",
        "pending_review",
        "approved",
        "published",
    ]
    members: list[TeamMemberReviewResponse]


class TeamGenerationBatchDetailResponse(BaseModel):
    id: int
    assignment_id: int
    generated_by: int
    batch_number: int
    total_students: int
    total_teams: int
    average_formation_score: Decimal | None
    status: BatchStatus
    review_notes: str | None
    created_at: datetime
    updated_at: datetime
    teams: list[TeamReviewResponse]

class TeamGenerationReviewRequest(BaseModel):
    decision: Literal["approved", "rejected"]
    review_notes: str | None = Field(default=None, max_length=2000)

    @field_validator("review_notes")
    @classmethod
    def validate_review_notes(cls, value):
        if value is not None:
            value = value.strip()
            if not value:
                return None
        return value


class TeamGenerationActionResponse(BaseModel):
    message: str
    batch_id: int
    assignment_id: int
    status: BatchStatus