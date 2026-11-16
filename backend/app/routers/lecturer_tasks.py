from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.database.session import get_db
from app.models import User
from app.schemas.task_contribution import (
    ContributionEvaluationCreate,
    ContributionEvaluationResponse,
    TaskCreate,
    TaskDetailResponse,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from app.services.task_contribution_service import (
    create_task,
    delete_task,
    evaluate_contribution,
    get_lecturer_task,
    get_lecturer_tasks,
    update_task,
)


router = APIRouter(
    prefix="/api/lecturer",
    tags=["Lecturer - Tasks and Contributions"],
)


def serialize_task_detail(task):
    return {
        "id": task.id,
        "team_id": task.team_id,
        "assignment_id": task.assignment_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "status": task.status,
        "deadline": task.deadline,
        "created_by": task.created_by,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "assignees": [
            {
                "id": assignee.id,
                "task_id": assignee.task_id,
                "team_member_id": assignee.team_member_id,
                "student_id": assignee.student_id,
                "status": assignee.status,
                "assigned_at": assignee.assigned_at,
                "status_updated_at": assignee.status_updated_at,
                "student_full_name": assignee.student.full_name,
                "student_email": assignee.student.email,
                "submission": assignee.submission,
                "evaluation": assignee.evaluation,
            }
            for assignee in task.assignees
        ],
    }


@router.get(
    "/assignments/{assignment_id}/tasks",
    response_model=TaskListResponse,
)
def list_assignment_tasks(
    assignment_id: int,
    team_id: int | None = None,
    current_user: User = Depends(require_roles("lecturer")),
    db: Session = Depends(get_db),
):
    tasks = get_lecturer_tasks(
        db,
        current_user,
        assignment_id,
        team_id,
    )

    return {
        "tasks": tasks,
        "total": len(tasks),
    }


@router.get(
    "/tasks/{task_id}",
    response_model=TaskDetailResponse,
)
def get_task_details(
    task_id: int,
    current_user: User = Depends(require_roles("lecturer")),
    db: Session = Depends(get_db),
):
    task = get_lecturer_task(db, current_user, task_id)
    return serialize_task_detail(task)


@router.post(
    "/teams/{team_id}/tasks",
    response_model=TaskDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_task(
    team_id: int,
    data: TaskCreate,
    current_user: User = Depends(require_roles("lecturer")),
    db: Session = Depends(get_db),
):
    try:
        task = create_task(db, current_user, team_id, data)
        return serialize_task_detail(task)
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The task could not be created because of a database conflict.",
        ) from error


@router.put(
    "/tasks/{task_id}",
    response_model=TaskDetailResponse,
)
def edit_task(
    task_id: int,
    data: TaskUpdate,
    current_user: User = Depends(require_roles("lecturer")),
    db: Session = Depends(get_db),
):
    task = update_task(db, current_user, task_id, data)
    return serialize_task_detail(task)


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_task(
    task_id: int,
    current_user: User = Depends(require_roles("lecturer")),
    db: Session = Depends(get_db),
):
    delete_task(db, current_user, task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put(
    "/task-assignees/{assignee_id}/evaluation",
    response_model=ContributionEvaluationResponse,
)
def review_contribution(
    assignee_id: int,
    data: ContributionEvaluationCreate,
    current_user: User = Depends(require_roles("lecturer")),
    db: Session = Depends(get_db),
):
    assignee = evaluate_contribution(
        db,
        current_user,
        assignee_id,
        data,
    )

    return assignee.evaluation
