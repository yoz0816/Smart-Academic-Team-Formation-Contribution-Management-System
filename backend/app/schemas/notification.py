from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


NotificationCategory = Literal[
    "team",
    "task",
    "submission",
    "evaluation",
    "assignment",
    "announcement",
    "system",
]


class NotificationResponse(BaseModel):
    id: int
    recipient_id: int
    actor_id: int | None
    category: NotificationCategory
    title: str
    message: str
    action_url: str | None
    is_read: bool
    read_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    total: int
    unread_count: int
    limit: int
    offset: int


class NotificationUnreadCountResponse(BaseModel):
    unread_count: int


class NotificationReadAllResponse(BaseModel):
    message: str
    updated_count: int
