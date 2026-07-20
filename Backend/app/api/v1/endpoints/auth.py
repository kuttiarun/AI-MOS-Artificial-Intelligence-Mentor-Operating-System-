"""
AI-MOS Backend — Authentication Endpoints (Phase 1 Stub)
=========================================================
Provides placeholder route structure for the JWT-based authentication
system described in Roadmap.md Day 3.

PHASE 1 STATUS: Structural stubs only.
  - Routes are registered and return informative placeholder responses.
  - No real password hashing or JWT issuance is performed yet.

TODO (Phase 3 — Day 3):
  - Implement POST /signup: Hash password with bcrypt, insert into `users` table
  - Implement POST /login: Verify bcrypt hash, issue signed JWT
  - Add `get_current_user` dependency used by gateway.py to verify sessions
  - Add token refresh endpoint (POST /refresh)
"""

import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Request/Response Schemas (auth-specific, defined inline for Phase 1 clarity)
# TODO (Phase 3): Move these to app/schemas/auth.py
# =============================================================================


class SignupRequest(BaseModel):
    email: EmailStr = Field(..., description="User's primary email address.")
    password: str = Field(..., min_length=8, description="Plain-text password (will be bcrypt hashed).")
    target_role: str = Field(default="Generalist", description="e.g., 'Java Developer (Zoho)'")
    operating_system: str = Field(..., description="e.g., 'Windows', 'Ubuntu', 'macOS'")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    message: str


class GoogleAuthRequest(BaseModel):
    email: EmailStr
    name: str | None = None
    picture: str | None = None


class GoogleAuthResponse(BaseModel):
    user_id: str
    email: str
    onboarding_complete: bool
    message: str


# =============================================================================
# POST /signup
# =============================================================================
@router.post(
    "/signup",
    summary="Register New User Account",
    tags=["Authentication"],
    response_model=TokenResponse,
)
async def signup(request: SignupRequest) -> TokenResponse:
    """
    [PHASE 1 STUB] Registers a new user account.

    TODO (Phase 3 implementation):
      1. Check if `email` already exists in `users` table (return 409 if so)
      2. Hash `request.password` using passlib bcrypt:
             hashed = bcrypt_context.hash(request.password)
      3. Insert new row into `users` table via SQLAlchemy async session
      4. Generate JWT: jose.jwt.encode({"sub": str(user.id), "exp": ...}, SECRET_KEY)
      5. Return TokenResponse with the signed JWT
    """
    logger.info("STUB: Signup called for email: [REDACTED]")
    return TokenResponse(
        access_token="STUB_TOKEN_PHASE_1",
        token_type="bearer",
        message=(
            "⚠️ Phase 1 stub: Authentication not yet implemented. "
            "This endpoint will issue real JWT tokens in Phase 3."
        ),
    )


# =============================================================================
# POST /login
# =============================================================================
@router.post(
    "/login",
    summary="Authenticate User & Issue JWT",
    tags=["Authentication"],
    response_model=TokenResponse,
)
async def login(request: LoginRequest) -> TokenResponse:
    """
    [PHASE 1 STUB] Authenticates a user and issues a JWT session token.

    TODO (Phase 3 implementation):
      1. Fetch user from `users` table by `email` (return 404 if not found)
      2. Verify password: bcrypt_context.verify(request.password, user.password_hash)
         (return 401 on mismatch)
      3. Generate JWT with user ID as subject and expiry from settings
      4. Return signed TokenResponse
    """
    logger.info("STUB: Login called")
    return TokenResponse(
        access_token="STUB_TOKEN_PHASE_1",
        token_type="bearer",
        message=(
            "⚠️ Phase 1 stub: Authentication not yet implemented. "
            "This endpoint will issue real JWT tokens in Phase 3."
        ),
    )


# =============================================================================
# POST /google
# =============================================================================
@router.post(
    "/google",
    summary="Google Authentication Sign-In",
    tags=["Authentication"],
    response_model=GoogleAuthResponse,
)
async def google_auth(
    request: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db),
) -> GoogleAuthResponse:
    """
    Authenticates a user via Google OAuth (direct sandbox/mock flow).
    """
    from app.services.progress import User
    from sqlalchemy import select
    import uuid

    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalars().first()

    if not user:
        # Create new user for this Google account
        user = User(
            id=uuid.uuid4(),
            email=request.email,
            password_hash="pbkdf2:sha256:google_oauth_bypass",
            target_role="Java Developer (Zoho)",
            operating_system="Windows",
            onboarding_complete=False,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        message = f"New user registered via Google: {request.email}"
    else:
        message = f"Existing user authenticated via Google: {request.email}"

    return GoogleAuthResponse(
        user_id=str(user.id),
        email=user.email,
        onboarding_complete=user.onboarding_complete,
        message=message,
    )
