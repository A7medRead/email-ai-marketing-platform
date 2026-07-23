import os
import smtplib
import mimetypes

from pathlib import Path
from email.message import EmailMessage
from dotenv import load_dotenv
from fastapi import UploadFile

# Load .env
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


async def send_email(
    to_email: str,
    subject: str,
    body: str,
    attachment: UploadFile | None = None,
):
    msg = EmailMessage()

    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    msg.set_content(body)

    # إضافة المرفق إذا وجد
    if attachment is not None:
        file_data = await attachment.read()

        content_type, _ = mimetypes.guess_type(
            attachment.filename
        )

        if content_type:
            maintype, subtype = content_type.split("/", 1)
        else:
            maintype, subtype = (
                "application",
                "octet-stream",
            )

        msg.add_attachment(
            file_data,
            maintype=maintype,
            subtype=subtype,
            filename=attachment.filename,
        )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
    ) as smtp:

        smtp.login(
            EMAIL_ADDRESS,
            EMAIL_PASSWORD,
        )

        smtp.send_message(msg)