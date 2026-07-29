from datetime import datetime, timezone

from email.message import EmailMessage
from app.mail.schemas import EmailCreate, EmailProvider
from app.mail.models import EmailProvider


from app.mail.importer import (
    import_email, import_emails
    )


def test_import_email_creates_new_email(db, email_data):
    email = import_email(db, email_data)

    assert email is not None
    assert email.message_id == email_data.message_id
    assert email.subject == email_data.subject


def test_import_email_returns_existing_email(db, email_data):
    first = import_email(db, email_data)
    second = import_email(db, email_data)

    assert first.id == second.id


def test_import_multiple_emails_with_duplicates(db, email_data):
    emails = import_emails(db, [email_data, email_data])

    assert len(emails) == 2
    assert emails[0].id == emails[1].id