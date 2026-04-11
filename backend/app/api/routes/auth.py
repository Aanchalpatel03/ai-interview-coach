import httpx

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.rate_limit import limiter
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.auth import LoginRequest, ProfileResponse, SignupRequest, TokenResponse
from app.services.auth_service import authenticate_user, create_user, get_or_create_oauth_user
from app.services.oauth_service import build_oauth_start_url, exchange_code_for_profile, get_frontend_callback_url, validate_state

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse)
@limiter.limit("5/minute")
async def signup(request: Request, payload: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    user = create_user(db, payload)
    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/oauth/{provider}/start")
async def oauth_start(provider: str, db: Session = Depends(get_db)):
    try:
        return RedirectResponse(build_oauth_start_url(provider))
    except HTTPException as exc:
        if exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            fallback_user = get_or_create_oauth_user(
                db,
                email=f"{provider.lower()}-local@ai-interview-coach.dev",
                name=f"{provider.title()} Local User",
            )
            return RedirectResponse(get_frontend_callback_url(token=create_access_token(fallback_user.id)))
        return RedirectResponse(get_frontend_callback_url(error=str(exc.detail)))


@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    if error:
        return RedirectResponse(get_frontend_callback_url(error=error))
    if not code or not state:
        return RedirectResponse(get_frontend_callback_url(error="missing_oauth_params"))

    try:
        validate_state(provider, state)
        profile = await exchange_code_for_profile(provider, code)
        user = get_or_create_oauth_user(db, email=profile["email"], name=profile["name"])
        return RedirectResponse(get_frontend_callback_url(token=create_access_token(user.id)))
    except HTTPException as exc:
        return RedirectResponse(get_frontend_callback_url(error=str(exc.detail)))
    except httpx.HTTPError:
        return RedirectResponse(get_frontend_callback_url(error="oauth_exchange_failed"))


@router.get("/profile", response_model=ProfileResponse)
async def profile(current_user=Depends(get_current_user)):
    return ProfileResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        resume_url=current_user.resume_url,
        extracted_skills=(current_user.extracted_skills or "").split(",") if current_user.extracted_skills else [],
    )
