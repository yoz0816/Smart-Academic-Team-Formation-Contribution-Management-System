from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_csrf, require_roles
from app.database.session import get_db
from app.models import User
from app.schemas.task_contribution import (
    StudentTaskListResponse,
    StudentTaskResponse,
    StudentTaskStatusUpdate,
    TaskAssigneeResponse,
    TaskSubmissionCreate,
    TaskSubmissionResponse,
)
from app.services.task_contribution_service import (
    get_student_tasks,
    submit_student_task,
    update_student_task_status,
)


router = APIRouter(
    prefix="/api/student/tasks",
    tags=["Student - Tasks and Contributions"],
)


@router.get(
    "",
    response_model=StudentTaskListResponse,
)
def list_my_tasks(
    current_student: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    tasks = get_student_tasks(db, current_student)

    return {
        "tasks": tasks,
        "total": len(tasks),
    }


@router.patch(
    "/assignments/{assignee_id}/status",
    response_model=TaskAssigneeResponse,
    dependencies=[Depends(require_csrf)],
)
def update_my_task_status(
    assignee_id: int,
    data: StudentTaskStatusUpdate,
    current_student: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    return update_student_task_status(
        db,
        current_student,
        assignee_id,
        data.status,
    )


@router.post(
    "/assignments/{assignee_id}/submission",
    response_model=TaskSubmissionResponse,
    dependencies=[Depends(require_csrf)],
)
def submit_my_task(
    assignee_id: int,
    data: TaskSubmissionCreate,
    current_student: User = Depends(require_roles("student")),
    db: Session = Depends(get_db),
):
    assignee = submit_student_task(
        db,
        current_student,
        assignee_id,
        data,
    )

    return assignee.submission
