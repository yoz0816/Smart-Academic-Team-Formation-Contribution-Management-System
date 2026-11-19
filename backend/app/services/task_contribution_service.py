from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    AcademicAssignment,
    ContributionEvaluation,
    Task,
    TaskAssignee,
    TaskSubmission,
    Team,
    TeamGenerationBatch,
    TeamMember,
    User,
)
from app.schemas.task_contribution import (
    ContributionEvaluationCreate,
    TaskCreate,
    TaskSubmissionCreate,
    TaskUpdate,
)
from app.services.notification_service import create_notification


def _not_found(message: str = "Resource not found.") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=message,
    )


def _forbidden(message: str = "You do not have permission to perform this action.") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=message,
    )


def _conflict(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=message,
    )



def _local_naive_datetime(value: datetime) -> datetime:
    """Normalize datetimes to the server's local timezone without tzinfo."""
    if value.tzinfo is not None:
        return value.astimezone().replace(tzinfo=None)

    return value


def _validate_task_deadline(
    db: Session,
    assignment_id: int,
    deadline: datetime,
) -> datetime:
    assignment = db.get(AcademicAssignment, assignment_id)

    if assignment is None:
        raise _not_found("Academic assignment not found.")

    deadline = _local_naive_datetime(deadline)
    assignment_limit = (
        assignment.final_submission_deadline or assignment.deadline
    )
    assignment_limit = _local_naive_datetime(assignment_limit)

    if deadline > assignment_limit:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Task deadline cannot exceed the assignment's final submission deadline.",
        )

    return deadline


def _has_task_progress(task: Task) -> bool:
    return any(
        assignee.status != "pending"
        or assignee.submission is not None
        or assignee.evaluation is not None
        for assignee in task.assignees
    )


def _get_published_team(
    db: Session,
    team_id: int,
    lecturer: User,
) -> Team:
    team = db.scalar(
        select(Team)
        .join(
            AcademicAssignment,
            Team.assignment_id == AcademicAssignment.id,
        )
        .join(
            TeamGenerationBatch,
            Team.generation_batch_id == TeamGenerationBatch.id,
        )
        .where(
            Team.id == team_id,
            Team.status == "published",
            TeamGenerationBatch.status == "published",
            AcademicAssignment.lecturer_id == lecturer.id,
            AcademicAssignment.status == "published",
        )
        .options(
            selectinload(Team.members),
        )
    )

    if team is None:
        raise _not_found(
            "Published team not found for one of your published assignments."
        )

    return team


def _get_lecturer_task(
    db: Session,
    task_id: int,
    lecturer: User,
) -> Task:
    task = db.scalar(
        select(Task)
        .join(
            AcademicAssignment,
            Task.assignment_id == AcademicAssignment.id,
        )
        .where(
            Task.id == task_id,
            AcademicAssignment.lecturer_id == lecturer.id,
        )
        .options(
            selectinload(Task.assignees)
            .selectinload(TaskAssignee.team_member)
            .selectinload(TeamMember.student),
            selectinload(Task.assignees).selectinload(TaskAssignee.submission),
            selectinload(Task.assignees).selectinload(TaskAssignee.evaluation),
        )
    )

    if task is None:
        raise _not_found("Task not found.")

    return task


def _refresh_task_status(task: Task) -> None:
    if task.status == "cancelled":
        return

    if task.assignees and all(
        assignee.status == "completed"
        for assignee in task.assignees
    ):
        task.status = "completed"
    elif any(
        assignee.status in ("in_progress", "submitted", "completed")
        for assignee in task.assignees
    ):
        task.status = "in_progress"
    else:
        task.status = "open"


def get_lecturer_tasks(
    db: Session,
    lecturer: User,
    assignment_id: int,
    team_id: int | None = None,
) -> list[Task]:
    assignment = db.scalar(
        select(AcademicAssignment).where(
            AcademicAssignment.id == assignment_id,
            AcademicAssignment.lecturer_id == lecturer.id,
        )
    )

    if assignment is None:
        raise _not_found("Assignment not found.")

    query = (
        select(Task)
        .where(Task.assignment_id == assignment_id)
        .options(
            selectinload(Task.assignees)
            .selectinload(TaskAssignee.team_member)
            .selectinload(TeamMember.student),
            selectinload(Task.assignees).selectinload(TaskAssignee.submission),
            selectinload(Task.assignees).selectinload(TaskAssignee.evaluation),
        )
        .order_by(Task.deadline.asc(), Task.created_at.desc())
    )

    if team_id is not None:
        query = query.where(Task.team_id == team_id)

    return list(db.scalars(query).all())


def get_lecturer_task(
    db: Session,
    lecturer: User,
    task_id: int,
) -> Task:
    return _get_lecturer_task(db, task_id, lecturer)


def create_task(
    db: Session,
    lecturer: User,
    team_id: int,
    data: TaskCreate,
) -> Task:
    team = _get_published_team(db, team_id, lecturer)

    members_by_user_id = {
        member.user_id: member
        for member in team.members
    }

    requested_ids = set(data.student_ids)

    if not requested_ids.issubset(members_by_user_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Every assigned student must belong to this team.",
        )

    task_deadline = _validate_task_deadline(
        db,
        team.assignment_id,
        data.deadline,
    )

    if task_deadline <= datetime.now().astimezone().replace(tzinfo=None):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A new task must have a future deadline.",
        )

    task = Task(
        team_id=team.id,
        assignment_id=team.assignment_id,
        title=data.title,
        description=data.description,
        priority=data.priority,
        deadline=task_deadline,
        created_by=lecturer.id,
        status="open",
    )

    db.add(task)
    db.flush()

    for student_id in data.student_ids:
        member = members_by_user_id[student_id]

        db.add(
            TaskAssignee(
                task_id=task.id,
                team_id=team.id,
                assignment_id=team.assignment_id,
                team_member_id=member.id,
                student_id=student_id,
                status="pending",
            )
        )

        create_notification(
            db=db,
            recipient_id=student_id,
            actor_id=lecturer.id,
            category="task",
            title="New task assigned",
            message=f'You have been assigned a new task: "{task.title}".',
            action_url="/pages/student/tasks.html",
        )

    db.commit()

    return _get_lecturer_task(db, task.id, lecturer)


def update_task(
    db: Session,
    lecturer: User,
    task_id: int,
    data: TaskUpdate,
) -> Task:
    task = _get_lecturer_task(db, task_id, lecturer)

    if task.status in ("completed", "cancelled"):
        raise _conflict("Completed or cancelled tasks cannot be edited.")

    changes = data.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide at least one field to update.",
        )

    has_progress = _has_task_progress(task)

    if has_progress and {"title", "description"} & changes.keys():
        raise _conflict(
            "Task title and description cannot be changed after a student starts working."
        )

    if "deadline" in changes:
        new_deadline = _validate_task_deadline(
            db,
            task.assignment_id,
            changes["deadline"],
        )

        if new_deadline <= datetime.now().astimezone().replace(tzinfo=None):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="The updated task deadline must be in the future.",
            )

        if has_progress and new_deadline <= task.deadline:
            raise _conflict(
                "Once students have started, the task deadline can only be extended."
            )

        changes["deadline"] = new_deadline

    for field, value in changes.items():
        if value is not None:
            setattr(task, field, value)

    db.commit()

    return _get_lecturer_task(db, task.id, lecturer)


def delete_task(
    db: Session,
    lecturer: User,
    task_id: int,
) -> None:
    task = _get_lecturer_task(db, task_id, lecturer)

    has_progress = any(
        assignee.status != "pending"
        or assignee.submission is not None
        or assignee.evaluation is not None
        for assignee in task.assignees
    )

    if has_progress:
        raise _conflict(
            "A task cannot be deleted after a student has started or submitted work."
        )

    db.delete(task)
    db.commit()


def get_student_tasks(
    db: Session,
    student: User,
) -> list[dict]:
    assignees = db.scalars(
        select(TaskAssignee)
        .join(Task, TaskAssignee.task_id == Task.id)
        .join(Team, Task.team_id == Team.id)
        .join(
            TeamGenerationBatch,
            Team.generation_batch_id == TeamGenerationBatch.id,
        )
        .where(
            TaskAssignee.student_id == student.id,
            Team.status == "published",
            TeamGenerationBatch.status == "published",
            Task.status != "cancelled",
        )
        .options(
            selectinload(TaskAssignee.task),
            selectinload(TaskAssignee.submission),
            selectinload(TaskAssignee.evaluation),
        )
        .order_by(Task.deadline.asc(), Task.created_at.desc())
    ).all()

    return [
        {
            "id": assignee.task.id,
            "assignee_id": assignee.id,
            "task_id": assignee.task.id,
            "title": assignee.task.title,
            "description": assignee.task.description,
            "priority": assignee.task.priority,
            "task_status": assignee.task.status,
            "deadline": assignee.task.deadline,
            "my_status": assignee.status,
            "assigned_at": assignee.assigned_at,
            "status_updated_at": assignee.status_updated_at,
            "submission": assignee.submission,
            "evaluation": assignee.evaluation,
        }
        for assignee in assignees
    ]


def _get_student_assignee(
    db: Session,
    student: User,
    assignee_id: int,
) -> TaskAssignee:
    assignee = db.scalar(
        select(TaskAssignee)
        .join(Task, TaskAssignee.task_id == Task.id)
        .join(Team, Task.team_id == Team.id)
        .join(
            TeamGenerationBatch,
            Team.generation_batch_id == TeamGenerationBatch.id,
        )
        .where(
            TaskAssignee.id == assignee_id,
            TaskAssignee.student_id == student.id,
            Team.status == "published",
            TeamGenerationBatch.status == "published",
        )
        .options(
            selectinload(TaskAssignee.task),
            selectinload(TaskAssignee.submission),
            selectinload(TaskAssignee.evaluation),
        )
    )

    if assignee is None:
        raise _not_found("Your assigned task was not found.")

    return assignee


def update_student_task_status(
    db: Session,
    student: User,
    assignee_id: int,
    new_status: str,
) -> TaskAssignee:
    assignee = _get_student_assignee(db, student, assignee_id)

    if assignee.task.status in ("completed", "cancelled"):
        raise _conflict("This task is no longer available for progress updates.")

    if assignee.status in ("submitted", "completed"):
        raise _conflict("Submitted or completed work cannot be moved backwards.")

    if assignee.submission is not None:
        raise _conflict("A submitted task cannot have its progress status changed.")

    assignee.status = new_status
    _refresh_task_status(assignee.task)

    db.commit()
    db.refresh(assignee)

    return assignee


def submit_student_task(
    db: Session,
    student: User,
    assignee_id: int,
    data: TaskSubmissionCreate,
) -> TaskAssignee:
    assignee = _get_student_assignee(db, student, assignee_id)

    if assignee.task.status in ("completed", "cancelled"):
        raise _conflict("This task is no longer accepting submissions.")

    current_deadline = _local_naive_datetime(assignee.task.deadline)
    current_time = datetime.now().astimezone().replace(tzinfo=None)

    if current_time > current_deadline:
        raise _conflict(
            "The task deadline has passed. Ask your lecturer to extend it before submitting."
        )

    if assignee.status == "completed" or assignee.evaluation is not None:
        raise _conflict("This contribution has already been evaluated.")

    if assignee.submission is None:
        submission = TaskSubmission(
            task_assignee_id=assignee.id,
            task_id=assignee.task_id,
            submission_text=data.submission_text,
        )
        db.add(submission)
    else:
        assignee.submission.submission_text = data.submission_text

    assignee.status = "submitted"
    _refresh_task_status(assignee.task)

    assignment = db.get(AcademicAssignment, assignee.assignment_id)

    if assignment is not None and assignment.lecturer_id is not None:
        create_notification(
            db=db,
            recipient_id=assignment.lecturer_id,
            actor_id=student.id,
            category="submission",
            title="Student submitted a task",
            message=f'{student.full_name} submitted work for "{assignee.task.title}".',
            action_url="/pages/lecturer/task-monitoring.html",
        )

    db.commit()
    db.refresh(assignee)

    return _get_student_assignee(db, student, assignee_id)


def evaluate_contribution(
    db: Session,
    lecturer: User,
    assignee_id: int,
    data: ContributionEvaluationCreate,
) -> TaskAssignee:
    assignee = db.scalar(
        select(TaskAssignee)
        .join(Task, TaskAssignee.task_id == Task.id)
        .join(
            AcademicAssignment,
            Task.assignment_id == AcademicAssignment.id,
        )
        .join(
            Team,
            Task.team_id == Team.id,
        )
        .join(
            TeamGenerationBatch,
            Team.generation_batch_id == TeamGenerationBatch.id,
        )
        .where(
            TaskAssignee.id == assignee_id,
            AcademicAssignment.lecturer_id == lecturer.id,
            AcademicAssignment.status == "published",
            Team.status == "published",
            TeamGenerationBatch.status == "published",
        )
        .options(
            selectinload(TaskAssignee.task),
            selectinload(TaskAssignee.submission),
            selectinload(TaskAssignee.evaluation),
        )
    )

    if assignee is None:
        raise _not_found("Task assignee not found.")

    if assignee.task.status == "cancelled":
        raise _conflict("Contributions for a cancelled task cannot be evaluated.")

    if assignee.submission is None:
        raise _conflict("The student must submit their work before evaluation.")

    evaluation = assignee.evaluation
    is_new_evaluation = evaluation is None

    if evaluation is None:
        evaluation = ContributionEvaluation(
            task_assignee_id=assignee.id,
            task_id=assignee.task_id,
            evaluator_id=lecturer.id,
            score=data.score,
            feedback=data.feedback,
        )
        db.add(evaluation)
    else:
        evaluation.evaluator_id = lecturer.id
        evaluation.score = data.score
        evaluation.feedback = data.feedback

    assignee.status = "completed"
    _refresh_task_status(assignee.task)

    if is_new_evaluation:
        create_notification(
            db=db,
            recipient_id=assignee.student_id,
            actor_id=lecturer.id,
            category="evaluation",
            title="Your contribution has been evaluated",
            message=f'Your contribution for "{assignee.task.title}" has been evaluated. Score: {data.score}/100.',
            action_url="/pages/student/tasks.html",
        )

    db.commit()
    db.refresh(assignee)

    return assignee
