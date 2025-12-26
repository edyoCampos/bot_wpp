import logging
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate

from robbot.config.settings import settings

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str) -> None:
    """
    Send email using SMTP settings.

    In desenvolvimento, usa Maildev (host maildev, porta 1025) por padrão.
    Em produção, configure SMTP_HOST/PORT/USERNAME/PASSWORD/TLS via .env.
    """
    if not to:
        logger.warning("send_email called without recipient")
        return

    host = settings.SMTP_HOST
    port = settings.SMTP_PORT or 25
    user = settings.SMTP_USERNAME
    password = settings.SMTP_PASSWORD
    use_tls = bool(settings.SMTP_TLS)
    sender = settings.SMTP_SENDER or "no-reply@example.local"

    if not host:
        logger.info("SMTP not configured (SMTP_HOST missing); skipping email to %s", to)
        return

    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to
    msg["Date"] = formatdate(localtime=True)

    try:
        with smtplib.SMTP(host, port, timeout=10) as server:
            server.ehlo()
            if use_tls:
                try:
                    server.starttls()
                    server.ehlo()
                except smtplib.SMTPException:
                    logger.warning("SMTP STARTTLS failed; continuing without TLS")
            if user and password:
                server.login(user, password)
            server.sendmail(sender, [to], msg.as_string())
        logger.info("Email sent to %s: %s", to, subject)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to send email to %s: %s", to, exc)
