from sqlalchemy.orm import Session

from app.models import StudentSkill, User
from app.schemas.student_skill import StudentSkillCreate, StudentSkillUpdate


def get_student_skills(db: Session, user: User) -> list[StudentSkill]:
    return (
        db.query(StudentSkill)
        .filter(StudentSkill.user_id == user.id)
        .order_by(StudentSkill.category, StudentSkill.skill_name)
        .all()
    )


def get_student_skill(
    db: Session,
    user: User,
    skill_id: int,
) -> StudentSkill | None:
    return (
        db.query(StudentSkill)
        .filter(
            StudentSkill.id == skill_id,
            StudentSkill.user_id == user.id,
        )
        .first()
    )


def create_student_skill(
    db: Session,
    user: User,
    data: StudentSkillCreate,
) -> StudentSkill:
    skill = StudentSkill(
        user_id=user.id,
        skill_name=data.skill_name,
        category=data.category,
        proficiency=data.proficiency,
    )

    db.add(skill)
    db.commit()
    db.refresh(skill)

    return skill


def update_student_skill(
    db: Session,
    skill: StudentSkill,
    data: StudentSkillUpdate,
) -> StudentSkill:
    skill.skill_name = data.skill_name
    skill.category = data.category
    skill.proficiency = data.proficiency

    db.commit()
    db.refresh(skill)

    return skill


def delete_student_skill(db: Session, skill: StudentSkill) -> None:
    db.delete(skill)
    db.commit()
