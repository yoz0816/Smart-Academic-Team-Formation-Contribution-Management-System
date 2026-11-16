from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.dependencies import require_roles
from app.database.session import get_db
from app.models import (
    AcademicAssignment,
    Team,
    TeamGenerationBatch,
    TeamMember,
    User,
)
from app.schemas.team_generation import (
    TeamGenerationActionResponse,
    TeamGenerationBatchDetailResponse,
    TeamGenerationBatchListResponse,
    TeamGenerationRequest,
    TeamGenerationResponse,
    TeamGenerationReviewRequest,
)
from app.services.team_generation_service import (
    generate_and_save_team_proposal,
)


router = APIRouter(
    prefix="/api/admin/team-generation",
    tags=["Admin - Team Generation"],
)


@router.post(
    "/assignments/{assignment_id}/generate",
    response_model=TeamGenerationResponse,
    status_code=201,
)
def generate_assignment_teams(
    assignment_id: int,
    data: TeamGenerationRequest,
    current_admin: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    assignment = db.scalar(
        select(AcademicAssignment).where(
            AcademicAssignment.id == assignment_id
        )
    )

    if assignment is None:
        raise HTTPException(
            status_code=404,
            detail="Academic assignment not found.",
        )

    if assignment.status != "published":
        raise HTTPException(
            status_code=409,
            detail="Teams can only be generated for published assignments.",
        )

    try:
        return generate_and_save_team_proposal(
            db=db,
            assignment_id=assignment_id,
            number_of_teams=data.number_of_teams,
            admin_id=current_admin.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@router.get(
    "/assignments/{assignment_id}/batches",
    response_model=TeamGenerationBatchListResponse,
)
def list_assignment_generation_batches(
    assignment_id: int,
    current_admin: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    assignment = db.scalar(
        select(AcademicAssignment.id).where(
            AcademicAssignment.id == assignment_id
        )
    )

    if assignment is None:
        raise HTTPException(
            status_code=404,
            detail="Academic assignment not found.",
        )

    batches = db.scalars(
        select(TeamGenerationBatch)
        .where(TeamGenerationBatch.assignment_id == assignment_id)
        .order_by(TeamGenerationBatch.batch_number.desc())
    ).all()

    return {
        "batches": batches,
        "total": len(batches),
    }

@router.get(
    "/batches/{batch_id}",
    response_model=TeamGenerationBatchDetailResponse,
)
def get_generation_batch_details(
    batch_id: int,
    current_admin: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    batch = db.scalar(
        select(TeamGenerationBatch)
        .where(TeamGenerationBatch.id == batch_id)
        .options(
            selectinload(TeamGenerationBatch.teams)
            .selectinload(Team.members)
            .selectinload(TeamMember.student)
        )
    )

    if batch is None:
        raise HTTPException(404, "Team generation batch not found.")

    teams = []

    for team in sorted(batch.teams, key=lambda item: item.team_number):
        members = [
            {
                "user_id": member.student.id,
                "full_name": member.student.full_name,
                "email": member.student.email,
            }
            for member in team.members
        ]

        teams.append(
            {
                "id": team.id,
                "team_number": team.team_number,
                "team_name": team.team_name,
                "formation_score": team.formation_score,
                "score_breakdown": team.score_breakdown,
                "status": team.status,
                "members": members,
            }
        )

    return {
        "id": batch.id,
        "assignment_id": batch.assignment_id,
        "generated_by": batch.generated_by,
        "batch_number": batch.batch_number,
        "total_students": batch.total_students,
        "total_teams": batch.total_teams,
        "average_formation_score": batch.average_formation_score,
        "status": batch.status,
        "review_notes": batch.review_notes,
        "created_at": batch.created_at,
        "updated_at": batch.updated_at,
        "teams": teams,
    }

@router.patch(
    "/batches/{batch_id}/review",
    response_model=TeamGenerationActionResponse,
)
def review_generation_batch(
    batch_id: int,
    data: TeamGenerationReviewRequest,
    current_admin: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    batch = db.scalar(
        select(TeamGenerationBatch)
        .where(TeamGenerationBatch.id == batch_id)
        .with_for_update()
    )

    if batch is None:
        raise HTTPException(404, "Team generation batch not found.")

    if batch.status not in {"generated", "pending_review"}:
        raise HTTPException(
            409,
            "Only generated or pending-review batches can be reviewed.",
        )

    teams = db.scalars(
        select(Team)
        .where(Team.generation_batch_id == batch.id)
        .with_for_update()
    ).all()

    if not teams:
        raise HTTPException(409, "This batch contains no teams.")

    if data.decision == "approved":
        batch.status = "approved"

        for team in teams:
            team.status = "approved"

        message = "Team generation batch approved successfully."

    else:
        batch.status = "rejected"

        for team in teams:
            team.status = "draft"

        message = "Team generation batch rejected."

    batch.review_notes = data.review_notes

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {
        "message": message,
        "batch_id": batch.id,
        "assignment_id": batch.assignment_id,
        "status": batch.status,
    }

@router.post(
    "/batches/{batch_id}/publish",
    response_model=TeamGenerationActionResponse,
)
def publish_generation_batch(
    batch_id: int,
    current_admin: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    batch = db.scalar(
        select(TeamGenerationBatch)
        .where(TeamGenerationBatch.id == batch_id)
        .with_for_update()
    )

    if batch is None:
        raise HTTPException(404, "Team generation batch not found.")

    if batch.status != "approved":
        raise HTTPException(
            409,
            "Only approved team generation batches can be published.",
        )

    teams = db.scalars(
        select(Team)
        .where(Team.generation_batch_id == batch.id)
        .with_for_update()
    ).all()

    if not teams:
        raise HTTPException(409, "This batch contains no teams.")

    if any(team.status != "approved" for team in teams):
        raise HTTPException(
            409,
            "Every team in the batch must be approved before publication.",
        )

    try:
        previous_batches = db.scalars(
            select(TeamGenerationBatch)
            .where(
                TeamGenerationBatch.assignment_id == batch.assignment_id,
                TeamGenerationBatch.status == "published",
                TeamGenerationBatch.id != batch.id,
            )
            .with_for_update()
        ).all()

        for previous_batch in previous_batches:
            previous_batch.status = "superseded"

            previous_teams = db.scalars(
                select(Team).where(
                    Team.generation_batch_id == previous_batch.id
                )
            ).all()

            for previous_team in previous_teams:
                previous_team.status = "draft"

        batch.status = "published"

        for team in teams:
            team.status = "published"

        db.commit()

    except Exception:
        db.rollback()
        raise

    return {
        "message": "Team generation batch published successfully. Students can now view their teams.",
        "batch_id": batch.id,
        "assignment_id": batch.assignment_id,
        "status": batch.status,
    }