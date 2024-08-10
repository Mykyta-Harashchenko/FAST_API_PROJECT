from fastapi import APIRouter, HTTPException, Depends, status, Path, Query, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from FAST_API.src.database.db import get_db
from FAST_API.src.repository import contacts as repositories_contacts
from FAST_API.src.repository import users as repositories_users
from FAST_API.src.schemas.user import UserSchema, TokenSchema, UserResponse
from FAST_API.src.services.auth import auth_service

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, db: AsyncSession = Depends(get_db)):
    exist_user = await repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, details='Account already exists')
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.create_user(body, db)
    return new_user


@router.post("/login")
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    pass
    return {}


@router.get('/refresh_token')
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(), db: AsyncSession = Depends(get_db)):
    pass
    return {}