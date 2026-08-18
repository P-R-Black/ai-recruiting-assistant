import email
from datetime import datetime, timezone
from email import policy
from email.utils import parseaddr, parsedate_to_datetime

from app.mail.models import EmailProvider
from app.mail.normalizer.base import ParsedEmail


def parse_raw_email(raw_bytes: bytes) -> email.message.Message:
    """Parse raw RFC822 bytes into a Message object. Provider-agnostic -
    MIME format doesn't change based on job board or mailbox provider.
    """
    return email.message_from_bytes(raw_bytes, policy=policy.default)


def _extract_bodies(msg: email.message.Message) -> tuple[str, str | None]:
    """Walk the MIME tree and pull out plain text + html bodies.
    Handles both single-part and (possibly nested) multipart messages."""
    text_body = ""
    html_body = None

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue  # container, not actual content
            if "attachment" in part.get("Content-Disposition", ""):
                continue  # skip file attachments

            charset = part.get_content_charset() or "utf-8"
            payload = part.get_payload(decode=True)
            if payload is None:
                continue

            content_type = part.get_content_type()
            if content_type == "text/plain" and not text_body:
                text_body = payload.decode(charset, errors="replace")
            elif content_type == "text/html" and html_body is None:
                html_body = payload.decode(charset, errors="replace")
    else:
        charset = msg.get_content_charset() or "utf-8"
        payload = msg.get_payload(decode=True)
        decoded = payload.decode(charset, errors="replace") if payload else ""
        if msg.get_content_type() == "text/html":
            html_body = decoded
        else:
            text_body = decoded

    return text_body, html_body


def build_parsed_email(raw_bytes: bytes, provider: EmailProvider) -> ParsedEmail:
    msg = parse_raw_email(raw_bytes)
    text_body, html_body = _extract_bodies(msg)

    _, sender = parseaddr(msg.get("From", ""))
    _, recipient = parseaddr(msg.get("To", ""))

    date_header = msg.get("Date")
    try:
        received_at = parsedate_to_datetime(
            date_header) if date_header else datetime.now(timezone.utc)
    except (TypeError, ValueError):
        # malformed Date header fallback
        received_at = datetime.now(timezone.utc)

    return ParsedEmail(
        message_id=msg.get("Message-ID", "").strip("<>"),
        provider=provider,
        subject=msg.get("Subject"),
        sender=sender,
        recipient=recipient,
        received_at=received_at,
        text_body=text_body,
        html_body=html_body,
    )



def get_html_from_raw_email(raw_bytes: bytes) -> str | None:
    """Handles multipart or single-part MIME, quoted-printable or base64 —
    the email module figures out the transfer encoding for you."""
    print('get_html_from_raw_email CALLED!!')
    msg = email.message_from_bytes(raw_bytes)
    """msg: Return-path: <bounces+361267-3930-ramoneblack=me.com@mail9.glassdoor.com>"""
    

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                charset = part.get_content_charset() or "utf-8"
                return part.get_payload(decode=True).decode(charset, errors="replace")
        return None
    else:
        if msg.get_content_type() == "text/html":
            charset = msg.get_content_charset() or "utf-8"
            return msg.get_payload(decode=True).decode(charset, errors="replace")
        return None