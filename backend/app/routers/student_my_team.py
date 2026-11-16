from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.dependencies import require_roles
from app.database.session import get_db
from app.models import (
    AcademicAssignment,
    Course,
    Team,
    TeamGenerationBatch,
    TeamMember,
    User,
)
from app.schemas.student_my_team import MyTeamsListResponse

router = APIRouter(
    prefix="/api/student/my-team",
    tags=["Student - My Team"],
)


@router.get(
    "",
    response_model=MyTeamsListResponse,
)
def get_my_teams(
    current_student: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    memberships = db.scalars(
        select(TeamMember)
        .join(
            Team,
            TeamMember.team_id == Team.id,
        )
        .join(
            TeamGenerationBatch,
            Team.generation_batch_id == TeamGenerationBatch.id,
        )
        .where(
            TeamMember.user_id == current_student.id,
            Team.status == "published",
            TeamGenerationBatch.status == "published",
        )
        .options(
            selectinload(TeamMember.team)
            .selectinload(Team.assignment)
            .selectinload(AcademicAssignment.course),
            selectinload(TeamMember.team)
            .selectinload(Team.assignment)
            .selectinload(AcademicAssignment.lecturer),
            selectinload(TeamMember.team)
            .selectinload(Team.members)
            .selectinload(TeamMember.student),
        )
        .order_by(TeamMember.assigned_at.desc())
    ).all()

    teams = []

    for membership in memberships:
        team = membership.team
        assignment = team.assignment
        course = assignment.course
        lecturer = assignment.lecturer

        members = [
            {
                "user_id": member.student.id,
                "full_name": member.student.full_name,
                "email": member.student.email,
            }
            for member in sorted(
                team.members,
                key=lambda item: item.student.full_name.casefold(),
            )
        ]

        teams.append(
            {
                "id": team.id,
                "team_number": team.team_number,
                "team_name": team.team_name,
                "assigned_at": membership.assigned_at,
                "members": members,
                "assignment": {
                    "id": assignment.id,
                    "title": assignment.title,
                    "description": assignment.description,
                    "instructions": assignment.instructions,
                    "opens_at": assignment.opens_at,
                    "deadline": assignment.deadline,
                    "proposal_opens_at": assignment.proposal_opens_at,
                    "proposal_deadline": assignment.proposal_deadline,
                    "modification_deadline": assignment.modification_deadline,
                    "final_submission_deadline": assignment.final_submission_deadline,
                    "course": {
                        "id": course.id,
                        "course_code": course.course_code,
                        "course_name": course.course_name,
                    },
                    "lecturer": {
                        "id": lecturer.id,
                        "full_name": lecturer.full_name,
                    },
                },
            }
        )

    return {
        "teams": teams,
        "total": len(teams),
    }