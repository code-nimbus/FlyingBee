from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
import os

from dotenv import load_dotenv

load_dotenv()

conf = ConnectionConfig(
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


async def send_email_async(subject: str, recipient: list[EmailStr], body: str):
    html = f"""
        <h2>{subject}</h2>
        <br/>
        <p>{body}</p>
        <br/>
        <br/>
        <br/>
        <p>Best regards</p>
        <p>FlyingBee Team</p>
    """
    message = MessageSchema(
        subject=subject, recipients=recipient, body=html, subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)
