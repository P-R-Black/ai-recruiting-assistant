from uuid import UUID

from sqlalchemy.orm import Session

from app.mail.models import Email
from app.mail.schemas import EmailCreate, EmailFilter, EmailUpdate


def create_email(db: Session, email: EmailCreate) -> Email:
    db_email = Email(**email.model_dump(mode="json"))

    db.add(db_email)
    db.commit()
    db.refresh(db_email)

    return db_email


def get_email(db: Session, email_id: UUID) -> Email | None:
    return _get_email_or_none(db, email_id)

def list_emails(
        db: Session, 
        skip: int = 0, 
        limit: int = 20,
        filters: EmailFilter | None = None
    ) -> list[Email]:
    
    query = db.query(Email)
    if filters:
        if filters.provider is not None:
            query = query.filter(Email.provider == filters.provider)

        if filters.sender is not None:
            query = query.filter(Email.sender.ilike(f"%{filters.sender}%"))

        if filters.recipient is not None:
            query = query.filter(Email.recipient.ilike(f"%{filters.recipient}%"))

        if filters.processed is not None:
            query = query.filter(Email.processed == filters.processed)

        if filters.is_job_email is not None:
            query = query.filter(Email.is_job_email == filters.is_job_email)

    return query.order_by(Email.received_at.desc()).offset(skip).limit(limit).all()


def update_email(db: Session, email_id: UUID, email_data: EmailUpdate) -> Email | None:
    db_email = _get_email_or_none(db, email_id)

    if not db_email:
        return None

    for field, value in email_data.model_dump(exclude_unset=True).items():
        setattr(db_email, field, value)

    db.commit()
    db.refresh(db_email)

    return db_email


def delete_email(db: Session, email_id: UUID) -> bool:
    db_email = _get_email_or_none(db, email_id)

    if not db_email:
        return False

    db.delete(db_email)
    db.commit()

    return True


def get_email_by_message_id(db: Session, message_id: str) -> Email | None:
    return (
        db.query(Email)
        .filter(Email.message_id == message_id)
        .first()
    )

def mark_email_processed(db: Session, email_id: UUID) -> Email | None:
    db_email = _get_email_or_none(db, email_id)

    if not db_email:
        return None
    
    db_email.processed = True

    db.commit()
    db.refresh(db_email)

    return db_email


""" Helper Func """
def _get_email_or_none(db: Session, email_id:UUID) -> Email | None:
    return (db.query(Email).filter(Email.id == email_id).first())