import hmac
from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Request,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import (
    SESSION_COOKIE_NAME,
    get_current_user,
)
from app.database.session import get_db
from app.models import User
from app.schemas.auth import (
    AuthResponse,
    CSRFResponse,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    UserResponse,
)
from app.services.auth_service import (
    SESSION_DURATION_DAYS,
    authenticate_user,
    create_user_session,
    get_valid_session,
    normalize_email,
    register_student,
    revoke_session,
    validate_csrf_token,
)
from app.core.security import generate_secure_token, hash_token


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)

CSRF_COOKIE_NAME = "joz_csrf"
CSRF_HEADER_NAME = "X-CSRF-Token"


def verify_request_origin(request: Request) -> None:
    origin = request.headers.get("origin")

    if origin not in settings.CORS_ORIGINS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid request origin.",
        )


def set_auth_cookies(
    response: Response,
    session_token: str,
    csrf_token: str,
) -> None:
    secure = not settings.DEBUG

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=SESSION_DURATION_DAYS * 24 * 60 * 60,
        path="/",
    )

    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=csrf_token,
        httponly=False,
        secure=secure,
        samesite="lax",
        max_age=SESSION_DURATION_DAYS * 24 * 60 * 60,
        path="/",
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
    )

    response.delete_cookie(
        key=CSRF_COOKIE_NAME,
        path="/",
        httponly=False,
        secure=not settings.DEBUG,
        samesite="lax",
    )


def get_request_session(
    request: Request,
    db: Session,
):
    session_token = request.cookies.get(SESSION_COOKIE_NAME)

    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    user_session = get_valid_session(db, session_token)

    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session.",
        )

    return session_token, user_session


def verify_csrf(
    request: Request,
    user_session,
    csrf_header: str | None,
) -> None:
    csrf_cookie = request.cookies.get(CSRF_COOKIE_NAME)

    if not csrf_cookie or not csrf_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing.",
        )

    if not hmac.compare_digest(csrf_cookie, csrf_header):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token mismatch.",
        )

    if not validate_csrf_token(user_session, csrf_header):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token.",
        )


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    verify_request_origin(request)

    try:
        user = register_student(
            db=db,
            full_name=data.full_name,
            email=normalize_email(str(data.email)),
            password=data.password,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )

    return AuthResponse(
        message="Student account created successfully.",
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=AuthResponse,
)
def login(
    data: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    verify_request_origin(request)

    try:
        user = authenticate_user(
            db=db,
            email=normalize_email(str(data.email)),
            password=data.password,
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    session_token, csrf_token, _ = create_user_session(db, user)

    set_auth_cookies(
        response,
        session_token,
        csrf_token,
    )

    return AuthResponse(
        message="Login successful.",
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
)
def logout(
    request: Request,
    response: Response,
    csrf_token: str | None = Header(
        default=None,
        alias=CSRF_HEADER_NAME,
    ),
    db: Session = Depends(get_db),
):
    verify_request_origin(request)

    session_token, user_session = get_request_session(request, db)

    verify_csrf(
        request,
        user_session,
        csrf_token,
    )

    revoke_session(db, session_token)
    clear_auth_cookies(response)

    return MessageResponse(
        message="Logout successful."
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get(
    "/csrf",
    response_model=CSRFResponse,
)
def get_csrf_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    _, user_session = get_request_session(request, db)

    csrf_token = generate_secure_token()

    user_session.csrf_token_hash = hash_token(csrf_token)
    db.commit()

    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=csrf_token,
        httponly=False,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=SESSION_DURATION_DAYS * 24 * 60 * 60,
        path="/",
    )

    return CSRFResponse(csrf_token=csrf_token)
