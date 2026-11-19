from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    AssignmentEligibleStudent,
    AssignmentRequiredSkill,
    PreferredTeammate,
    StudentAcademicExperience,
    StudentInterest,
    StudentProblemSolving,
    StudentSkill,
    StudentSoftSkill,
    User,
)

from app.services.team_scoring_service import (
    RequiredSkill,
    StudentScoringProfile,
)


def load_assignment_scoring_data(
    db: Session,
    assignment_id: int,
    student_ids: list[int],
) -> tuple[list[StudentScoringProfile], list[RequiredSkill]]:
    """
    Load eligible students' scoring data for an academic assignment.

    Returns:
        A list of student scoring profiles and assignment-required skills.
    """

    if not student_ids:
        raise ValueError("No students were provided for scoring.")

    if len(student_ids) != len(set(student_ids)):
        raise ValueError("Duplicate student IDs were provided.")

    eligible_ids = set(
        db.scalars(
            select(AssignmentEligibleStudent.student_id).where(
                AssignmentEligibleStudent.assignment_id == assignment_id,
                AssignmentEligibleStudent.student_id.in_(student_ids),
            )
        ).all()
    )

    if eligible_ids != set(student_ids):
        raise ValueError(
            "One or more students are not eligible for this assignment."
        )
    
    users = db.scalars(
        select(User).where(
            User.id.in_(student_ids),
            User.role == "student",
            User.is_active.is_(True),
        )
    ).all()

    if len(users) != len(student_ids):
        raise ValueError(
            "One or more selected accounts are inactive or are not students."
        )

    profiles = {
        user.id: StudentScoringProfile(user_id=user.id)
        for user in users
    }

    skills = db.scalars(
        select(StudentSkill).where(
            StudentSkill.user_id.in_(student_ids)
        )
    ).all()

    for skill in skills:
        profiles[skill.user_id].technical_skills[
            skill.skill_name
        ] = skill.proficiency


    experiences = db.scalars(
        select(StudentAcademicExperience).where(
            StudentAcademicExperience.user_id.in_(student_ids),
            StudentAcademicExperience.status == "Approved",
        )
    ).all()

    for experience in experiences:
        profiles[experience.user_id].approved_cgpa = experience.cgpa

    interests = db.scalars(
        select(StudentInterest).where(
            StudentInterest.user_id.in_(student_ids)
        )
    ).all()

    for interest in interests:
        profiles[interest.user_id].interests.add(
            interest.interest_name
        )

    preferences = db.scalars(
        select(PreferredTeammate).where(
            PreferredTeammate.user_id.in_(student_ids)
        )
    ).all()

    for preference in preferences:
        profiles[preference.user_id].preferred_teammate_ids.add(
            preference.preferred_user_id
        )

    soft_skills = db.scalars(
        select(StudentSoftSkill).where(
            StudentSoftSkill.user_id.in_(student_ids)
        )
    ).all()

    for skill in soft_skills:
        profiles[skill.user_id].soft_skills[
            skill.skill_name
        ] = skill.proficiency

    problem_solving = db.scalars(
        select(StudentProblemSolving).where(
            StudentProblemSolving.user_id.in_(student_ids)
        )
    ).all()

    for ability in problem_solving:
        profiles[ability.user_id].problem_solving[
            ability.category
        ] = ability.proficiency

    assignment_skills = db.scalars(
        select(AssignmentRequiredSkill).where(
            AssignmentRequiredSkill.assignment_id == assignment_id
        )
    ).all()

    required_skills = [
        RequiredSkill(
            skill_name=skill.skill_name,
            required_proficiency=skill.required_proficiency,
        )
        for skill in assignment_skills
    ]

    ordered_profiles = [
        profiles[user_id]
        for user_id in sorted(profiles)
    ]

    return ordered_profiles, required_skills