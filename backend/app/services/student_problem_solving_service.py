from sqlalchemy.orm import Session

from app.models import StudentProblemSolving, User
from app.schemas.student_problem_solving import (
    StudentProblemSolvingCreate,
    StudentProblemSolvingUpdate,
)


def get_student_problem_solving_abilities(
    db: Session,
    user: User,
) -> list[StudentProblemSolving]:
    return (
        db.query(StudentProblemSolving)
        .filter(StudentProblemSolving.user_id == user.id)
        .order_by(StudentProblemSolving.category)
        .all()
    )


def get_student_problem_solving_ability(
    db: Session,
    user: User,
    ability_id: int,
) -> StudentProblemSolving | None:
    return (
        db.query(StudentProblemSolving)
        .filter(
            StudentProblemSolving.id == ability_id,
            StudentProblemSolving.user_id == user.id,
        )
        .first()
    )


def create_student_problem_solving_ability(
    db: Session,
    user: User,
    data: StudentProblemSolvingCreate,
) -> StudentProblemSolving:
    ability = StudentProblemSolving(
        user_id=user.id,
        category=data.category,
        proficiency=data.proficiency,
    )

    db.add(ability)
    db.commit()
    db.refresh(ability)

    return ability


def update_student_problem_solving_ability(
    db: Session,
    ability: StudentProblemSolving,
    data: StudentProblemSolvingUpdate,
) -> StudentProblemSolving:
    ability.category = data.category
    ability.proficiency = data.proficiency

    db.commit()
    db.refresh(ability)

    return ability


def delete_student_problem_solving_ability(
    db: Session,
    ability: StudentProblemSolving,
) -> None:
    db.delete(ability)
    db.commit()
