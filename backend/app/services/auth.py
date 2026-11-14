import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import Depends, HTTPException, Request, Response
from pwdlib import PasswordHash
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import Session, User
from ..schemas import RegisterRequest

password_hash = PasswordHash.recommended()
SESSION_COOKIE = "session"
SESSION_DAYS = 7


async def register_user(session: AsyncSession, payload: RegisterRequest) -> User:
    email = payload.email.lower()
    if await session.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        email=email,
        name=payload.name,
        password_hash=password_hash.hash(payload.password),
    )
    session.add(user)
    await session.flush()
    return user


def verify_password(user: User, password: str) -> bool:
    return password_hash.verify(password, user.password_hash)


async def create_session(session: AsyncSession, user_id: UUID, response: Response) -> None:
    token = secrets.token_urlsafe(32)
    session.add(
        Session(
            user_id=user_id,
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            expires_at=datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS),
        )
    )
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=SESSION_DAYS * 86400,
        httponly=True,
        samesite="lax",
    )


async def destroy_session(session: AsyncSession, request: Request, response: Response) -> None:
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        await session.execute(
            delete(Session).where(Session.token_hash == hashlib.sha256(token.encode()).hexdigest())
        )
        await session.commit()
    response.delete_cookie(SESSION_COOKIE)


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> User:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    row = await session.scalar(
        select(Session).where(Session.token_hash == hashlib.sha256(token.encode()).hexdigest())
    )
    if row is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    expires_at = row.expires_at
    if expires_at.tzinfo is None:  # SQLite returns naive datetimes
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    user = await session.get(User, row.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
