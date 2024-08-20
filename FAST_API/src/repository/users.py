from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from FAST_API.src.database.db import get_db
from FAST_API.src.entity.models import User
from FAST_API.src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    The get_user_by_email function retrieves a user from the database by their email address.

    :param email: str: Specify the email of the user to retrieve
    :param db: AsyncSession: Database session for executing the query
    :return: The user object if found, otherwise None
    :doc-author: Trelent
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    The create_user function adds a new user to the database based on the provided user schema.

    :param body: UserSchema: Specify the user details to be added
    :param db: AsyncSession: Database session for executing the query
    :return: The newly created user
    :doc-author: Trelent
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    The update_token function updates the refresh token of a specific user in the database.

    :param user: User: Specify the user whose token needs to be updated
    :param token: str | None: Specify the new token value, or None to clear the token
    :param db: AsyncSession: Database session for executing the query
    :return: None
    :doc-author: Trelent
    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    The confirmed_email function marks a user's email as confirmed in the database.

    :param email: str: Specify the email address of the user to confirm
    :param db: AsyncSession: Database session for executing the query
    :return: None
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    """
    The update_avatar_url function updates the avatar URL of a specific user in the database.

    :param email: str: Specify the email of the user whose avatar URL needs to be updated
    :param url: str | None: Specify the new avatar URL, or None to clear the avatar
    :param db: AsyncSession: Database session for executing the query
    :return: The updated user object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user
