import os
import sys

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Path,
    Query,
    Security,
    BackgroundTasks,
    Request,
    Response,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from FAST_API.src.database.db import get_db
from FAST_API.src.repository import contacts as repositories_contacts
from FAST_API.src.repository import users as repositories_users
from FAST_API.src.schemas.user import (
    UserSchema,
    TokenSchema,
    UserResponse,
    RequestEmail,
)
from FAST_API.src.services.auth import auth_service
from FAST_API.src.services.email import send_email

router = APIRouter(prefix="/auth", tags=["auth"])
get_refresh_token = HTTPBearer()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserSchema,
    bt: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    The signup function handles user registration by creating a new user account.
    It checks if the user already exists, hashes the password, and sends a confirmation email.

    :param body: UserSchema: Specify the user details to create
    :param bt: BackgroundTasks: Handle background tasks like sending emails
    :param request: Request: Access request details such as the base URL
    :param db: AsyncSession: Database session for executing queries
    :return: The newly created user
    :raise HTTPException: If the user already exists (409 Conflict)
    :doc-author: Trelent
    """
    exist_user = await repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.create_user(body, db)
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    The login function authenticates the user by verifying their email and password,
    generates JWT tokens, and updates the user's refresh token in the database.

    :param body: OAuth2PasswordRequestForm: Contains the login credentials (username and password)
    :param db: AsyncSession: Database session for executing queries
    :return: A dictionary containing the access and refresh tokens
    :raise HTTPException: If the email is invalid, the email is not confirmed, or the password is incorrect (401 Unauthorized)
    :doc-author: Trelent
    """
    user = await repositories_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed"
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repositories_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh_token")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(),
    db: AsyncSession = Depends(get_db),
):
    """
    The refresh_token function generates a new access and refresh token pair using a valid refresh token.
    It checks the validity of the provided refresh token and updates the database with the new token.

    :param credentials: HTTPAuthorizationCredentials: Contains the refresh token
    :param db: AsyncSession: Database session for executing queries
    :return: A dictionary containing the new access and refresh tokens
    :raise HTTPException: If the refresh token is invalid (401 Unauthorized)
    :doc-author: Trelent
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repositories_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repositories_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    The confirmed_email function confirms the user's email by validating the token sent via email.
    It updates the user's status to confirmed in the database.

    :param token: str: The token sent to the user's email for confirmation
    :param db: AsyncSession: Database session for executing queries
    :return: A message indicating the email confirmation status
    :raise HTTPException: If the token is invalid or the user is not found (400 Bad Request)
    :doc-author: Trelent
    """
    email = await auth_service.get_email_from_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repositories_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    The request_email function sends a confirmation email to the user if their email is not yet confirmed.

    :param body: RequestEmail: Contains the user's email
    :param background_tasks: BackgroundTasks: Handle background tasks like sending emails
    :param request: Request: Access request details such as the base URL
    :param db: AsyncSession: Database session for executing queries
    :return: A message indicating that a confirmation email has been sent
    :doc-author: Trelent
    """
    user = await repositories_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, str(request.base_url)
        )
    return {"message": "Check your email for confirmation."}


@router.get("/{username}}")
async def request_email(
    username: str, response: Response, db: AsyncSession = Depends(get_db)
):
    """
    The request_email function logs a message when a user checks a specific URL and returns an image.

    :param username: str: The username of the person checking the URL
    :param response: Response: Customize the response, such as adding headers
    :param db: AsyncSession: Database session for executing queries
    :return: An image file response
    :doc-author: Trelent
    """
    print("--------------------------------------------------------")
    print(f"{username}, He checked this message ")
    print("--------------------------------------------------------")
    return FileResponse(
        "FAST_API/src/static/open_check.png",
        media_type="image/png",
        content_disposition_type="inline",
    )
