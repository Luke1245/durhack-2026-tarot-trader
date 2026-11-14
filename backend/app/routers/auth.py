from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import User
from ..schemas import LoginRequest, RegisterRequest, UserResponse
from ..services.auth import (
    create_session,
    destroy_session,
    get_current_user,
    register_user,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    payload: RegisterRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> User:
    user = await register_user(session, payload)
    await create_session(session, user.id, response)
    await session.commit()
    return user


@router.post("/login", response_model=UserResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> User:
    user = await session.scalar(select(User).where(User.email == payload.email.lower()))
    if user is None or not verify_password(user, payload.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    await create_session(session, user.id, response)
    await session.commit()
    return user


@router.post("/logout", status_code=204)
async def logout(request: Request, response: Response, session: AsyncSession = Depends(get_session)) -> None:
    await destroy_session(session, request, response)


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)) -> User:
    return user
