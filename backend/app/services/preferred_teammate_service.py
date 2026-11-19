from sqlalchemy.orm import Session

from app.models import PreferredTeammate, User
from app.schemas.preferred_teammate import PreferredTeammateUpdate


MAX_PREFERRED_TEAMMATES = 3


def search_students(
    db: Session,
    current_user: User,
    search: str = "",
) -> list[User]:
    query = db.query(User).filter(
        User.role == "student",
        User.is_active.is_(True),
        User.id != current_user.id,
    )

    search = search.strip()

    if search:
        query = query.filter(User.full_name.ilike(f"%{search}%"))

    return (
        query.order_by(User.full_name.asc())
        .limit(20)
        .all()
    )


def get_preferred_teammates(
    db: Session,
    current_user: User,
) -> list[User]:
    records = (
        db.query(PreferredTeammate)
        .filter(PreferredTeammate.user_id == current_user.id)
        .all()
    )

    preferred_ids = [record.preferred_user_id for record in records]

    if not preferred_ids:
        return []

    students = (
        db.query(User)
        .filter(
            User.id.in_(preferred_ids),
            User.role == "student",
            User.is_active.is_(True),
        )
        .all()
    )

    students_by_id = {student.id: student for student in students}

    return [
        students_by_id[student_id]
        for student_id in preferred_ids
        if student_id in students_by_id
    ]


def update_preferred_teammates(
    db: Session,
    current_user: User,
    data: PreferredTeammateUpdate,
) -> list[User]:
    preferred_ids = data.preferred_user_ids

    if len(preferred_ids) > MAX_PREFERRED_TEAMMATES:
        raise ValueError("You can select a maximum of 3 preferred teammates.")

    if current_user.id in preferred_ids:
        raise ValueError("You cannot select yourself as a preferred teammate.")

    if preferred_ids:
        students = (
            db.query(User)
            .filter(
                User.id.in_(preferred_ids),
                User.role == "student",
                User.is_active.is_(True),
            )
            .all()
        )

        valid_ids = {student.id for student in students}

        if valid_ids != set(preferred_ids):
            raise ValueError(
                "One or more selected students are unavailable."
            )

    try:
        (
            db.query(PreferredTeammate)
            .filter(PreferredTeammate.user_id == current_user.id)
            .delete(synchronize_session=False)
        )

        records = [
            PreferredTeammate(
                user_id=current_user.id,
                preferred_user_id=student_id,
            )
            for student_id in preferred_ids
        ]

        db.add_all(records)
        db.commit()

    except Exception:
        db.rollback()
        raise

    return get_preferred_teammates(db, current_user)
