from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    AcademicAssignment,
    AssignmentEligibleStudent,
    Team,
    TeamGenerationBatch,
    TeamMember,
    User,
)

from app.services.team_formation_algorithm import generate_team_proposal
from app.services.team_scoring_data_service import (
    load_assignment_scoring_data,
)


def generate_and_save_team_proposal(
    db: Session,
    assignment_id: int,
    number_of_teams: int,
    admin_id: int,
) -> dict:
    """
    Generate and save a team proposal for administrator review.

    Generated batches remain unpublished.
    Teams are saved with draft status.
    """

    try:
        admin = db.scalar(
            select(User).where(
                User.id == admin_id,
                User.role == "admin",
                User.is_active.is_(True),
            )
        )

        if admin is None:
            raise ValueError("An active administrator account is required.")

        assignment = db.scalar(
            select(AcademicAssignment).where(
                AcademicAssignment.id == assignment_id
            )
        )

        if assignment is None:
            raise ValueError("Academic assignment not found.")

        if assignment.status != "published":
            raise ValueError(
                "Teams can only be generated for published assignments."
            )

        student_ids = db.scalars(
            select(AssignmentEligibleStudent.student_id)
            .where(
                AssignmentEligibleStudent.assignment_id == assignment_id
            )
            .order_by(AssignmentEligibleStudent.student_id)
        ).all()

        if not student_ids:
            raise ValueError(
                "No eligible students have been selected for this assignment."
            )

        members, required_skills = load_assignment_scoring_data(
            db=db,
            assignment_id=assignment_id,
            student_ids=list(student_ids),
        )

        proposal = generate_team_proposal(
            members=members,
            required_skills=required_skills,
            number_of_teams=number_of_teams,
        )

        latest_batch_number = db.scalar(
            select(func.max(TeamGenerationBatch.batch_number)).where(
                TeamGenerationBatch.assignment_id == assignment_id
            )
        )

        batch_number = (latest_batch_number or 0) + 1

        batch = TeamGenerationBatch(
            assignment_id=assignment_id,
            generated_by=admin_id,
            batch_number=batch_number,
            total_students=proposal["total_students"],
            total_teams=proposal["number_of_teams"],
            average_formation_score=Decimal(
                str(proposal["final_average_score"])
            ),
            status="generated",
        )

        db.add(batch)
        db.flush()

        profiles_by_id = {
            member.user_id: member
            for member in members
        }

        for team_result in proposal["teams"]:
            team = Team(
                assignment_id=assignment_id,
                generation_batch_id=batch.id,
                team_number=team_result["team_number"],
                team_name=f"Team {team_result['team_number']}",
                formation_score=Decimal(
                    str(team_result["score"]["total_score"])
                ),
                score_breakdown=team_result["score"],
                status="draft",
            )

            db.add(team)
            db.flush()

            for student_id in team_result["member_ids"]:
                if student_id not in profiles_by_id:
                    raise RuntimeError(
                        "Generated team contains an unknown student."
                    )

                db.add(
                    TeamMember(
                        team_id=team.id,
                        assignment_id=assignment_id,
                        user_id=student_id,
                    )
                )

        db.commit()
        db.refresh(batch)

        return {
            "message": "Team proposal generated successfully.",
            "batch_id": batch.id,
            "assignment_id": assignment_id,
            "batch_number": batch.batch_number,
            "status": batch.status,
            "total_students": batch.total_students,
            "total_teams": batch.total_teams,
            "average_formation_score": float(
                batch.average_formation_score
            ),
            "initial_average_score": proposal["initial_average_score"],
            "improvement": proposal["improvement"],
            "iterations": proposal["iterations"],
            "teams": proposal["teams"],
        }

    except Exception:
        db.rollback()
        raise