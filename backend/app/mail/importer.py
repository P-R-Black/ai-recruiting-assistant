from sqlalchemy.orm import Session

from app.mail import crud
from app.mail.providers.outlook import (
    OutlookSettings,
    fetch_outlook_messages,
    graph_headers,
    normalize_outlook_message,
    search_folder,
)
from app.mail.schemas import EmailCreate

# ----------------------------
# Import helpers
# ----------------------------

def import_email(db: Session, email: EmailCreate):
    """
    Imports a single email if it doesn't already exist.
    """

    existing = crud.get_email_by_message_id(db, email.message_id)

    if existing:
        return existing

    return crud.create_email(db, email)


def import_emails(db: Session, emails: list[EmailCreate]):
    imported = []

    for email in emails:
        imported.append(import_email(db, email))

    return imported


def import_outlook_messages(
    db: Session,
    settings: OutlookSettings,
    folder_name: str = "Inbox",
):
    headers = graph_headers(settings)

    folder = search_folder(headers, folder_name)

    if folder is None:
        return []

    messages = fetch_outlook_messages(
        settings=settings,
        folder_id=folder["id"],
    )

    emails = [
        normalize_outlook_message(message)
        for message in messages
    ]

    return import_emails(db, emails)