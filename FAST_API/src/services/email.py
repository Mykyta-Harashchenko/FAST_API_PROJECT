from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from FAST_API.src.services.auth import auth_service
from FAST_API.src.conf.config import config

conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_USERNAME,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME="CONTACT SYSTEM",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Sends an email to the user with a verification link.

    :param email: The user's email address
    :param username: The user's username
    :param host: The base URL of the host server
    :return: None
    """
    try:
        # Create an email token for verification
        token_verification = auth_service.create_email_token({"sub": email})

        # Create the message schema for the email
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        # Send the email using FastMail
        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")

    except ConnectionErrors as err:
        # Handle connection errors
        print(err)
