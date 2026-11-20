from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.database.session import engine
from app.routers.auth import router as auth_router
from app.routers.student_profile import router as student_profile_router
from app.routers.student_skills import router as student_skills_router
from app.routers.admin_academic_experience import router as admin_academic_experience_router
from app.routers.student_academic_experience import router as student_academic_experience_router
from app.routers.student_interests import router as student_interests_router
from app.routers.preferred_teammates import router as preferred_teammates_router
from app.routers.student_soft_skills import router as student_soft_skills_router
from app.routers.student_problem_solving import router as student_problem_solving_router
from app.routers.admin_team_generation import router as admin_team_generation_router
from app.routers.student_my_team import router as student_my_team_router
from app.routers.lecturer_tasks import router as lecturer_tasks_router
from app.routers.student_tasks import router as student_tasks_router
from app.routers.student_notifications import router as student_notifications_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for the JOZ academic team formation system.",
    debug=settings.DEBUG,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(student_profile_router)
app.include_router(student_skills_router)
app.include_router(admin_academic_experience_router)
app.include_router(student_academic_experience_router)
app.include_router(student_interests_router)
app.include_router(preferred_teammates_router)
app.include_router(student_soft_skills_router)
app.include_router(student_problem_solving_router)
app.include_router(admin_team_generation_router)
app.include_router(student_my_team_router)
app.include_router(lecturer_tasks_router)
app.include_router(student_tasks_router)
app.include_router(student_notifications_router)


@app.get("/", tags=["General"])
def root():
    return {
        "message": "Welcome to the JOZ API",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "application": "JOZ API",
    }


@app.get("/health/database", tags=["Health"])
def database_health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": settings.DATABASE_NAME,
            "connection": "successful",
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed.",
        )