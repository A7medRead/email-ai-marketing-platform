import smtplib
import mimetypes

from email.message import EmailMessage
from fastapi import UploadFile


async def send_email(
    to_email: str,
    subject: str,
    body: str,
    attachment: UploadFile | None = None,
    sender_email: str = None,
    sender_password: str = None,
):
    msg = EmailMessage()

    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    msg.add_alternative(body, subtype="html")

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
            sender_email,
            sender_password,
        )

        smtp.send_message(msg)