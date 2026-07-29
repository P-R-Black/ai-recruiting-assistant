from datetime import datetime, timezone
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime

from app.mail.models import EmailProvider
from app.mail.schemas import EmailCreate

# ----------------------------
# Parsing
# ----------------------------

def parse_email(raw_email: bytes, provider: EmailProvider) -> EmailCreate:


    message = BytesParser(policy=policy.default).parsebytes(raw_email)
    message_id = message.get("Message-ID", "")
    subject = message.get("Subject","")
    sender = message.get("From", "")
    recipient = message.get("To", "")


    date = message.get("Date")

    if date:
        received_at = parsedate_to_datetime(date)

        # Ensure the datetime is timezone-aware
        if received_at.tzinfo is None:
            received_at = received_at.replace(tzinfo=timezone.utc)
    else:
        received_at = datetime.now(timezone.utc)

    raw_body = extract_message_body(message)
    print('raw_body:', raw_body)

    return EmailCreate(
        provider=provider,
        message_id=message_id,
        subject=subject,
        sender=sender,
        recipient=recipient,
        received_at=received_at,
        raw_body=raw_body,
    )


def extract_plain_text(message) -> str | None:
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                return part.get_content()
    elif message.get_content_type() == "text/plain":
        return message.get_content()

    return None


def extract_html(message) -> str | None:
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/html":
                return part.get_content()
    elif message.get_content_type() == "text/html":
        return message.get_content()

    return None


def extract_message_body(message):
    text = extract_plain_text(message)

    if text:
        return text

    html = extract_html(message)

    if html:
        return html

    return ""
