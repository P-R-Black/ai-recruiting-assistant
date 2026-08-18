from venv import logger

from sqlalchemy.orm import Session

from app.mail.mail_services.importer import import_emails

# from app.mail.providers.gmail import fetch_gmail_messages
from app.mail.models import EmailProvider
from app.mail.providers.icloud import fetch_icloud_messages
from app.mail.providers.outlook import fetch_outlook_messages


def fetch_messages(provider, settings):
    if provider == EmailProvider.ICLOUD:
        return fetch_icloud_messages(settings)

    if provider == EmailProvider.OUTLOOK:
        return fetch_outlook_messages(settings)

    # if provider == EmailProvider.GMAIL:
    #     return fetch_gmail_messages(settings)

    raise ValueError(f"Unsupported email provider: {provider}")



def normalize_message(provider, message):
    if provider == EmailProvider.ICLOUD:
        # IMAP / iCloud messages are already in the correct format
        return message  

    if provider == EmailProvider.OUTLOOK:
        from app.mail.providers.outlook import normalize_outlook_message
        return normalize_outlook_message(message)

    # if provider == EmailProvider.GMAIL:
    #     from app.mail.providers.gmail import normalize_gmail_message
    #     return normalize_gmail_message(message)

    raise ValueError(f"Unsupported email provider: {provider}")

def sync_provider(db: Session, provider: EmailProvider, settings):
    raw_messages = fetch_messages(provider, settings)

    normalized_emails = []

    for message in raw_messages:
        normalized_email = normalize_message(provider, message)
        normalized_emails.append(normalized_email)

    return import_emails(db, normalized_emails)


def sync_all_providers(db: Session, providers_settings):
    for provider, settings in providers_settings.items():
        imported = sync_provider(db, provider, settings)
        logger.info(f"Imported {len(imported)} emails from {provider.value}")
    return imported
