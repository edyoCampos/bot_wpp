import logging

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str) -> None:
    """
    Stub function to send email. Replace with real SMTP/third-party provider.
    """
    logger.info("Sending email to %s: %s", to, subject)
    logger.debug("Email body: %s", body)
