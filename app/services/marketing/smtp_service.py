import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.encryption import decrypt


GMAIL_SMTP_SERVER = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587


def _connect_to_gmail(
    email: str,
    encrypted_password: str,
):
    """
    Create authenticated Gmail SMTP connection.
    """

    try:
        password = decrypt(encrypted_password).replace(" ", "")

        server = smtplib.SMTP(
            GMAIL_SMTP_SERVER,
            GMAIL_SMTP_PORT,
            timeout=20,
        )

        server.set_debuglevel(0)

        server.ehlo()

        server.starttls()

        server.ehlo()

        server.login(
            email,
            password,
        )

        return server


    except Exception as e:

        raise Exception(
            f"Gmail SMTP connection failed: {repr(e)}"
        )



def verify_gmail_account(
    email: str,
    encrypted_password: str,
):
    """
    Verify Gmail SMTP credentials.

    Returns:
        tuple(bool, str)
    """

    try:

        server = _connect_to_gmail(
            email=email,
            encrypted_password=encrypted_password,
        )

        server.quit()


        return (
            True,
            "Account verified successfully.",
        )


    except Exception as e:

        error = str(e)

        print(
            "SMTP VERIFY ERROR:",
            error,
        )


        return (
            False,
            error,
        )



def send_test_email(
    sender_email: str,
    encrypted_password: str,
    recipient_email: str,
):
    """
    Send test email.

    Returns:
        tuple(bool, str)
    """

    server = None

    try:

        server = _connect_to_gmail(
            email=sender_email,
            encrypted_password=encrypted_password,
        )


        message = MIMEMultipart()


        message["From"] = sender_email

        message["To"] = recipient_email

        message["Subject"] = (
            "AI Email Marketing Platform - Test Email"
        )


        body = """
Hello!

This is a test email sent from
AI Email Marketing Platform.

Your sender account is configured correctly.

Have a great day!
"""


        message.attach(
            MIMEText(
                body,
                "plain",
            )
        )


        server.sendmail(
            sender_email,
            recipient_email,
            message.as_string(),
        )


        server.quit()


        return (
            True,
            "Test email sent successfully.",
        )


    except Exception as e:

        error = str(e)

        print(
            "SMTP SEND ERROR:",
            error,
        )


        return (
            False,
            error,
        )


    finally:

        if server:

            try:
                server.quit()

            except Exception:
                pass