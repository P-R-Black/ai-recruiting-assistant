from sqlalchemy.orm import Session

from app.mail import crud
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
