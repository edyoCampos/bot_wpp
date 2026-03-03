import logging
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate

from pydantic import BaseModel

from robbot.config.settings import settings

logger = logging.getLogger(__name__)


def filter_none_values(pydantic_model: BaseModel) -> dict:
    """
    Remove None values from Pydantic model dump for partial updates.

    Args:
        pydantic_model: Pydantic model instance

    Returns:
        Dict with only non-None values
    """
    return {k: v for k, v in pydantic_model.model_dump().items() if v is not None}


def send_email(to: str, subject: str, body: str) -> None:
    """
    Send email using SMTP settings.

    In desenvolvimento, usa Maildev (host maildev, porta 1025) por padrão.
    Em produção, configure SMTP_HOST/PORT/USERNAME/PASSWORD/TLS via .env.
    """
    if not to:
        logger.warning("[WARNING] send_email called without recipient")
        return

    host = settings.SMTP_HOST
    port = settings.SMTP_PORT or 25
    user = settings.SMTP_USERNAME
    password = settings.SMTP_PASSWORD
    use_tls = bool(settings.SMTP_TLS)
    sender = settings.SMTP_SENDER or "no-reply@example.local"

    if not host:
        logger.info("[INFO] SMTP not configured (SMTP_HOST missing); skipping email to %s", to)
        return

    # Detecta se o corpo parece HTML (simples heurística)
    if "<html" in body.lower() or "<body" in body.lower() or "<table" in body.lower():
        msg = MIMEText(body, "html", _charset="utf-8")
    else:
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
                    logger.warning("[WARNING] SMTP STARTTLS failed; continuing without TLS")
            if user and password:
                server.login(user, password)
            server.sendmail(sender, [to], msg.as_string())
        logger.info("[SUCCESS] Email sent to %s: %s", to, subject)
    except Exception as exc:  # noqa: BLE001 (blind exception)  # pylint: disable=broad-exception-caught
        logger.exception("[ERROR] Failed to send email to %s: %s", to, exc)


def extract_device_name(user_agent: str | None) -> str:
    """Extract friendly device name from user-agent string.

    Args:
        user_agent: User-Agent header string

    Returns:
        Human-readable device name (e.g., "Chrome 120 on Windows 10")
        Returns "Unknown Device" if parsing fails

    Examples:
        >>> extract_device_name("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        "Chrome on Windows 10"
        >>> extract_device_name("Mozilla/5.0 (iPhone; CPU iPhone OS 15_0)")
        "Safari on iPhone"
    """
    if not user_agent:
        return "Unknown Device"

    user_agent_lower = user_agent.lower()

    # Detect OS
    os_name = "Unknown OS"
    if "windows nt 10.0" in user_agent_lower:
        os_name = "Windows 10"
    elif "windows nt 11.0" in user_agent_lower or "windows nt 10.0; win64" in user_agent_lower:
        os_name = "Windows 11"
    elif "mac os x" in user_agent_lower:
        os_name = "macOS"
    elif "iphone" in user_agent_lower:
        os_name = "iPhone"
    elif "ipad" in user_agent_lower:
        os_name = "iPad"
    elif "android" in user_agent_lower:
        os_name = "Android"
    elif "linux" in user_agent_lower:
        os_name = "Linux"

    # Detect Browser
    browser_name = "Unknown Browser"
    if "edg/" in user_agent_lower or "edge" in user_agent_lower:
        browser_name = "Edge"
    elif "chrome/" in user_agent_lower and "edg/" not in user_agent_lower:
        browser_name = "Chrome"
    elif "firefox/" in user_agent_lower:
        browser_name = "Firefox"
    elif "safari/" in user_agent_lower and "chrome/" not in user_agent_lower:
        browser_name = "Safari"
    elif "opera" in user_agent_lower or "opr/" in user_agent_lower:
        browser_name = "Opera"

    return f"{browser_name} on {os_name}"
