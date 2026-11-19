import hmac
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import (
    generate_secure_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models import User, UserSession


SESSION_DURATION_DAYS = 7


def normalize_email(email: str) -> str:
    return email.strip().lower()


def register_student(
    db: Session,
    full_name: str,
    email: str,
    password: str,
) -> User:
    normalized_email = normalize_email(email)

    existing_user = db.scalar(
        select(User).where(User.email == normalized_email)
    )

    if existing_user:
        raise ValueError("An account with this email already exists.")

    user = User(
        full_name=full_name.strip(),
        email=normalized_email,
        password_hash=hash_password(password),
        role="student",
        is_active=True,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()
        raise ValueError("An account with this email already exists.")

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User:
    normalized_email = normalize_email(email)

    user = db.scalar(
        select(User).where(User.email == normalized_email)
    )

    if not user or not verify_password(password, user.password_hash):
        raise ValueError("Invalid email or password.")

    if not user.is_active:
        raise ValueError("Invalid email or password.")

    return user


def create_user_session(
    db: Session,
    user: User,
) -> tuple[str, str, UserSession]:
    session_token = generate_secure_token()
    csrf_token = generate_secure_token()

    expires_at = datetime.utcnow() + timedelta(
        days=SESSION_DURATION_DAYS
    )

    user_session = UserSession(
        user_id=user.id,
        session_token_hash=hash_token(session_token),
        csrf_token_hash=hash_token(csrf_token),
        expires_at=expires_at,
    )

    db.add(user_session)
    db.commit()
    db.refresh(user_session)

    return session_token, csrf_token, user_session


def get_valid_session(
    db: Session,
    session_token: str,
) -> UserSession | None:
    token_hash = hash_token(session_token)

    user_session = db.scalar(
        select(UserSession).where(
            UserSession.session_token_hash == token_hash
        )
    )

    if not user_session:
        return None

    if user_session.revoked_at is not None:
        return None

    if user_session.expires_at <= datetime.utcnow():
        return None

    if not user_session.user.is_active:
        return None

    return user_session


def revoke_session(
    db: Session,
    session_token: str,
) -> bool:
    user_session = db.scalar(
        select(UserSession).where(
            UserSession.session_token_hash == hash_token(session_token)
        )
    )

    if not user_session or user_session.revoked_at is not None:
        return False

    user_session.revoked_at = datetime.utcnow()

    db.commit()

    return True


def validate_csrf_token(
    user_session: UserSession,
    csrf_token: str,
) -> bool:
    supplied_hash = hash_token(csrf_token)

    return hmac.compare_digest(
        user_session.csrf_token_hash,
        supplied_hash,
    )
