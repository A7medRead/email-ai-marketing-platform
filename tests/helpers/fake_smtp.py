"""Test-only SMTP transport.

`FakeSMTP` replaces `smtplib.SMTP` inside `app.infrastructure.email.smtp`, so the
real message-building code runs but nothing ever touches the network.
"""
import email
import smtplib
from dataclasses import dataclass, field
from email import policy


@dataclass
class SentMessage:
    sender: str
    recipient: str
    raw: str
    subject: str
    from_header: str
    html: str
    delivery_id: int | None = None


@dataclass
class FakeSMTPController:
    """Records activity and lets a test script failures."""

    connections: list = field(default_factory=list)
    logins: list = field(default_factory=list)
    sent: list = field(default_factory=list)
    send_attempts: list = field(default_factory=list)  # recipients, incl. failed
    connect_error: Exception | None = None
    login_error: Exception | None = None
    # recipient -> exception raised from sendmail
    recipient_errors: dict = field(default_factory=dict)
    # called as hook(recipient) before sendmail records anything
    on_sendmail: object = None

    def fail_connect(self, exc: Exception | None = None):
        self.connect_error = exc or ConnectionRefusedError("connection refused")

    def fail_timeout(self):
        self.connect_error = TimeoutError("timed out")

    def fail_auth(self):
        self.login_error = smtplib.SMTPAuthenticationError(
            535, b"5.7.8 Username and Password not accepted"
        )

    def fail_recipient(self, recipient: str, exc: Exception):
        self.recipient_errors[recipient] = exc

    def smtp_4xx(self, recipient: str, code: int = 451):
        self.fail_recipient(
            recipient, smtplib.SMTPResponseException(code, b"try again later")
        )

    def smtp_5xx(self, recipient: str, code: int = 550):
        self.fail_recipient(
            recipient,
            smtplib.SMTPRecipientsRefused({recipient: (code, b"mailbox unavailable")}),
        )

    def recipients(self) -> list:
        return [m.recipient for m in self.sent]

    def to(self, recipient: str) -> list:
        return [m for m in self.sent if m.recipient == recipient]


def _parse(raw: str, sender: str, recipient: str) -> SentMessage:
    msg = email.message_from_string(raw, policy=policy.default)
    html = ""
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            html = part.get_content()
    return SentMessage(
        sender=sender,
        recipient=recipient,
        raw=raw,
        subject=str(msg["Subject"]),
        from_header=str(msg["From"]),
        html=html,
    )


def make_fake_smtp_class(ctl: FakeSMTPController):
    class FakeSMTP:
        def __init__(self, host, port, timeout=None, **kwargs):
            if ctl.connect_error:
                raise ctl.connect_error
            self.host, self.port = host, port
            ctl.connections.append((host, port))

        def ehlo(self):
            return (250, b"ok")

        def starttls(self):
            return (220, b"ready")

        def login(self, user, password):
            if ctl.login_error:
                raise ctl.login_error
            ctl.logins.append((user, password))

        def sendmail(self, sender, recipient, raw):
            ctl.send_attempts.append(recipient)
            if ctl.on_sendmail:
                ctl.on_sendmail(recipient)
            if recipient in ctl.recipient_errors:
                raise ctl.recipient_errors[recipient]
            ctl.sent.append(_parse(raw, sender, recipient))
            return {}

        def quit(self):
            return (221, b"bye")

    return FakeSMTP
