from sqlalchemy.orm import Session

from app.models import StudentInterest, User
from app.schemas.student_interest import StudentInterestUpdate


def get_student_interests(db: Session, user: User) -> list[str]:
    records = (
        db.query(StudentInterest)
        .filter(StudentInterest.user_id == user.id)
        .order_by(StudentInterest.interest_name)
        .all()
    )

    return [record.interest_name for record in records]


def update_student_interests(
    db: Session,
    user: User,
    data: StudentInterestUpdate,
) -> list[str]:
    db.query(StudentInterest).filter(
        StudentInterest.user_id == user.id
    ).delete(synchronize_session=False)

    records = [
        StudentInterest(
            user_id=user.id,
            interest_name=interest,
        )
        for interest in data.interests
    ]

    db.add_all(records)
    db.commit()

    return get_student_interests(db, user)
