import smtplib
import re
from urllib.parse import quote
import jwt

from email.mime.text import MIMEText
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart

from app.core.encryption import decrypt
from app.core.config import TRACKING_URL
from app.core.config import SECRET_KEY, ALGORITHM


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

        password = decrypt(
            encrypted_password
        ).replace(" ", "")


        server = smtplib.SMTP(
            GMAIL_SMTP_SERVER,
            GMAIL_SMTP_PORT,
            timeout=20,
        )


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
            f"Gmail SMTP connection failed: {str(e)}"
        )



def verify_gmail_account(
    email: str,
    encrypted_password: str,
):
    """
    Verify Gmail SMTP credentials.
    """

    server = None

    try:

        server = _connect_to_gmail(
            email=email,
            encrypted_password=encrypted_password,
        )


        return (
            True,
            "Account verified successfully."
        )



    except Exception as e:

        error = str(e)


        print(
            "SMTP VERIFY ERROR:",
            error
        )


        return (
            False,
            error
        )



    finally:

        if server:

            try:
                server.quit()

            except Exception:
                pass




def send_test_email(
    sender_email: str,
    encrypted_password: str,
    recipient_email: str,
):
    """
    Send test email.
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

This is a test email from
AI Email Marketing Platform.

Your sender account is working correctly.

Regards,
AI Email Marketing Platform
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



        return {
            "success": True,
            "message": "Test email sent successfully."
        }



    except Exception as e:

        error = str(e)


        print(
            "SMTP SEND ERROR:",
            error
        )


        return {
            "success": False,
            "message": error
        }



    finally:

        if server:

            try:
                server.quit()

            except Exception:
                pass

# A bare URL also ends at an HTML-escaped delimiter (&lt; &gt; &quot; &#x27;), which escaped text
# bodies (e.g. TEXT variants) can place right after a URL.
_TAG_OR_BARE_URL = re.compile(
    r"<[^>]*>|https?://(?:(?!&(?:lt|gt|quot|#x27);)[^\s<>\"'])+"
)
_HREF_HTTP = re.compile(r"""(\bhref\s*=\s*)(["'])(https?://[^"']*)\2""", re.IGNORECASE)


def track_links(html: str, delivery_id: int) -> str:
    """Route http(s) links through the click-tracking endpoint.

    Inside tags only complete quoted href values are rewritten (mailto:, tel:,
    #anchors, src= etc. are left alone); outside tags bare URLs in text are
    rewritten. The destination is carried whole in a signed token.
    """

    def tracked(url: str) -> str:
        token = jwt.encode(
            {"delivery_id": delivery_id, "url": url, "purpose": "click"},
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
        return f"{TRACKING_URL}/track/click?token={quote(token)}"

    def rewrite_href(match):
        # &amp; is HTML escaping of the attribute, not part of the real URL.
        url = match.group(3).replace("&amp;", "&")
        return f"{match.group(1)}{match.group(2)}{tracked(url)}{match.group(2)}"

    def replace(match):
        text = match.group(0)
        if text.startswith("<"):
            return _HREF_HTTP.sub(rewrite_href, text)
        # &amp; is HTML escaping of the text, as for href values.
        return tracked(text.replace("&amp;", "&"))

    return _TAG_OR_BARE_URL.sub(replace, html)


def send_campaign_email(
    sender_email: str,
    sender_name: str,
    encrypted_password: str,
    recipient_email: str,
    subject: str,
    body: str,
    delivery_id: int,
    contact_id: int,
):

    server = None

    try:

        server = _connect_to_gmail(
            email=sender_email,
            encrypted_password=encrypted_password,
        )


        message = MIMEMultipart()

        message["From"] = formataddr(
            (sender_name, sender_email)
        )
        message["To"] = recipient_email
        message["Subject"] = subject


        tracking_pixel = f"""
        <img
        src="{TRACKING_URL}/track/open/{delivery_id}"
        width="1"
        height="1"
        style="display:none"
        />
        """


        html_body = body

        if not (
            "<html" in body.lower()
            or "<body" in body.lower()
            or "<table" in body.lower()
        ):
            html_body = body.replace(
                "\n",
                "<br>"
            )


        html_body = track_links(html_body, delivery_id)


        html_body += tracking_pixel

        unsubscribe_token = jwt.encode(
            {"contact_id": contact_id, "purpose": "unsubscribe"},
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
        html_body += (
            f'<p><a href="{TRACKING_URL}/track/unsubscribe/'
            f'{unsubscribe_token}">Unsubscribe</a></p>'
        )


        message.attach(
            MIMEText(
                html_body,
                "html",
                "utf-8",
            )
        )


        server.sendmail(
            sender_email,
            recipient_email,
            message.as_string(),
        )


        return {
            "success": True,
            "message": "Campaign email sent successfully."
        }


    except Exception as e:

        error = str(e)

        print(
            "CAMPAIGN SMTP ERROR:",
            error
        )

        return {
            "success": False,
            "message": error
        }


    finally:

        if server:

            try:
                server.quit()

            except Exception:
                pass
