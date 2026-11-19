from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models import Notification, User


def create_notification(
    db: Session,
    recipient_id: int,
    category: str,
    title: str,
    message: str,
    actor_id: int | None = None,
    action_url: str | None = None,
) -> Notification:
    notification = Notification(
        recipient_id=recipient_id,
        actor_id=actor_id,
        category=category,
        title=title,
        message=message,
        action_url=action_url,
    )

    db.add(notification)
    db.flush()

    return notification


def get_student_notifications(
    db: Session,
    student: User,
    limit: int = 20,
    offset: int = 0,
    unread_only: bool = False,
) -> dict:
    filters = [
        Notification.recipient_id == student.id,
    ]

    if unread_only:
        filters.append(Notification.is_read.is_(False))

    total = db.scalar(
        select(func.count(Notification.id)).where(*filters)
    ) or 0

    unread_count = get_unread_count(db, student)

    notifications = db.scalars(
        select(Notification)
        .where(*filters)
        .order_by(
            Notification.created_at.desc(),
            Notification.id.desc(),
        )
        .offset(offset)
        .limit(limit)
    ).all()

    return {
        "notifications": notifications,
        "total": total,
        "unread_count": unread_count,
        "limit": limit,
        "offset": offset,
    }


def get_unread_count(
    db: Session,
    student: User,
) -> int:
    return db.scalar(
        select(func.count(Notification.id)).where(
            Notification.recipient_id == student.id,
            Notification.is_read.is_(False),
        )
    ) or 0


def mark_notification_as_read(
    db: Session,
    student: User,
    notification_id: int,
) -> Notification | None:
    notification = db.scalar(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.recipient_id == student.id,
        )
    )

    if notification is None:
        return None

    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now()
        db.commit()
        db.refresh(notification)

    return notification


def mark_all_notifications_as_read(
    db: Session,
    student: User,
) -> int:
    result = db.execute(
        update(Notification)
        .where(
            Notification.recipient_id == student.id,
            Notification.is_read.is_(False),
        )
        .values(
            is_read=True,
            read_at=datetime.now(),
        )
    )

    db.commit()

    return result.rowcount or 0
