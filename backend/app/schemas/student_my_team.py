from datetime import datetime

from pydantic import BaseModel, ConfigDict

class MyTeamMemberResponse(BaseModel):
    user_id: int
    full_name: str
    email: str


class MyTeamCourseResponse(BaseModel):
    id: int
    course_code: str
    course_name: str


class MyTeamLecturerResponse(BaseModel):
    id: int
    full_name: str


class MyTeamAssignmentResponse(BaseModel):
    id: int
    title: str
    description: str | None
    instructions: str | None
    opens_at: datetime
    deadline: datetime
    proposal_opens_at: datetime | None
    proposal_deadline: datetime | None
    modification_deadline: datetime | None
    final_submission_deadline: datetime | None
    course: MyTeamCourseResponse
    lecturer: MyTeamLecturerResponse


class MyTeamItemResponse(BaseModel):
    id: int
    team_number: int
    team_name: str
    assigned_at: datetime
    members: list[MyTeamMemberResponse]
    assignment: MyTeamAssignmentResponse


class MyTeamsListResponse(BaseModel):
    teams: list[MyTeamItemResponse]
    total: int