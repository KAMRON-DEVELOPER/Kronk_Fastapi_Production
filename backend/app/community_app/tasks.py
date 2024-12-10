import asyncio
from email.message import EmailMessage
from time import sleep

from aiosmtplib import SMTP
from app.core.celery import celery_app
from app.core.config import settings


@celery_app.task
def dummy_tast_for_community(name="Bob") -> str:
    sleep(5)
    return f"Hello {name}!"


@celery_app.task
def send_email_task_for_community(to_email: str, subject: str, body: str) -> dict[str, str]:
    return asyncio.run(_send_email_async(to_email, subject, body))


async def _send_email_async(to_email: str, subject: str, body: str) -> dict[str, str]:
    message = EmailMessage()
    message["From"] = settings.EMAIL_HOST_USER
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        smtp_client = SMTP(
            hostname=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            use_tls=settings.EMAIL_USE_TLS,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
        )
        async with smtp_client:
            await smtp_client.send_message(message)

        return {"status": "succeed", "message": "Email sent successfully"}
    except Exception as e:
        print(f"🌋 Exception in _send_email_async: {e}")
        return {"status": "failed", "message": f"{e}"}
