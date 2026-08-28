from app.mail.normalizer.base import NormalizedJob
from app.mail.schemas import EmailCreate


def build_email_create_from_normalized(
          normalized: NormalizedJob,
    
    ) -> EmailCreate:

    return EmailCreate(
        provider=normalized.provider,
        message_id=normalized.message_id,
        subject=normalized.subject,
        sender=normalized.sender,
        recipient=normalized.recipient,
        received_at=normalized.received_at,
        raw_body="",
    )


