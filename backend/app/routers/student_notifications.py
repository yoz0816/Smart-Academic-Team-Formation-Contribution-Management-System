from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_csrf, require_roles
from app.database.session import get_db
from app.models import User
from app.schemas.notification import (
    NotificationListResponse,
    NotificationReadAllResponse,
    NotificationResponse,
    NotificationUnreadCountResponse,
)
from app.services.notification_service import (
    get_student_notifications,
    get_unread_count,
    mark_all_notifications_as_read,
    mark_notification_as_read,
)


router = APIRouter(
    prefix="/api/student/notifications",
    tags=["Student Notifications"],
)


@router.get(
    "",
    response_model=NotificationListResponse,
)
def read_notifications(
    unread_only: bool = False,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    return get_student_notifications(
        db=db,
        student=current_user,
        limit=limit,
        offset=offset,
        unread_only=unread_only,
    )


@router.get(
    "/unread-count",
    response_model=NotificationUnreadCountResponse,
)
def read_unread_count(
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    return {
        "unread_count": get_unread_count(db, current_user),
    }


@router.patch(
    "/read-all",
    response_model=NotificationReadAllResponse,
    dependencies=[Depends(require_csrf)],
)
def read_all_notifications(
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    updated_count = mark_all_notifications_as_read(
        db=db,
        student=current_user,
    )

    return {
        "message": "Notifications marked as read.",
        "updated_count": updated_count,
    }


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    dependencies=[Depends(require_csrf)],
)
def read_single_notification(
    notification_id: int,
    current_user: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    notification = mark_notification_as_read(
        db=db,
        student=current_user,
        notification_id=notification_id,
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        )

    return notification
