from sqlalchemy.orm import Session

from app.models import StudentSoftSkill, User
from app.schemas.student_soft_skill import (
    StudentSoftSkillCreate,
    StudentSoftSkillUpdate,
)


def get_student_soft_skills(
    db: Session,
    user: User,
) -> list[StudentSoftSkill]:
    return (
        db.query(StudentSoftSkill)
        .filter(StudentSoftSkill.user_id == user.id)
        .order_by(StudentSoftSkill.skill_name)
        .all()
    )


def get_student_soft_skill(
    db: Session,
    user: User,
    skill_id: int,
) -> StudentSoftSkill | None:
    return (
        db.query(StudentSoftSkill)
        .filter(
            StudentSoftSkill.id == skill_id,
            StudentSoftSkill.user_id == user.id,
        )
        .first()
    )


def create_student_soft_skill(
    db: Session,
    user: User,
    data: StudentSoftSkillCreate,
) -> StudentSoftSkill:
    skill = StudentSoftSkill(
        user_id=user.id,
        skill_name=data.skill_name,
        proficiency=data.proficiency,
    )

    db.add(skill)
    db.commit()
    db.refresh(skill)

    return skill


def update_student_soft_skill(
    db: Session,
    skill: StudentSoftSkill,
    data: StudentSoftSkillUpdate,
) -> StudentSoftSkill:
    skill.skill_name = data.skill_name
    skill.proficiency = data.proficiency

    db.commit()
    db.refresh(skill)

    return skill


def delete_student_soft_skill(
    db: Session,
    skill: StudentSoftSkill,
) -> None:
    db.delete(skill)
    db.commit()
