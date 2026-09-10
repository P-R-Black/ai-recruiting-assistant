from datetime import datetime, timezone

from app.mail.models import EmailProvider
from app.mail.normalizer.base import ParsedEmail



def build_parsed_email_from_graph_message(
    message: dict,
    provider: EmailProvider,
) -> ParsedEmail:
    """Build a ParsedEmail from a Microsoft Graph API message dict.
    Unlike IMAP-fetched providers, Outlook mail arrives as JSON, not
    raw RFC822 bytes - so this bypasses build_parsed_email/email.message_from_bytes
    entirely and reads Graph's own field names instead."""

    from_email = message.get("from", {}).get("emailAddress", {}).get("address", "")

    to_recipients = message.get("toRecipients", [])
    recipient = (
        to_recipients[0]["emailAddress"]["address"] if to_recipients else ""
    )

    received_at = None
    received_at_str = message.get("receivedDateTime")
    if received_at_str:
        # Graph returns ISO8601 with a trailing 'Z' - fromisoformat needs
        # explicit +00:00 instead on Python versions before 3.11
        received_at = datetime.fromisoformat(received_at_str.replace("Z", "+00:00"))

    body = message.get("body", {})
    content_type = (body.get("contentType") or "").lower()
    content = body.get("content", "")

    html_body = content if content_type == "html" else None

    text_body = content if content_type == "text" else ""

    return ParsedEmail(
        message_id=message.get("internetMessageId") or message.get("id", ""),
        provider=provider,
        subject=message.get("subject"),
        sender=from_email,
        recipient=recipient,
        received_at=received_at,
        text_body=text_body,
        html_body=html_body,
    )