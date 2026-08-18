import imaplib

from sqlalchemy.orm import Session

from app.mail.mail_services.importer import import_email
from app.mail.mail_services.parser import parse_email
from app.mail.mail_services.service import IMAPSettings
from app.mail.models import Email

# ----------------------------
# IMAP
# ----------------------------

def connect_imap(settings: IMAPSettings):
    """
    Connects and authenticates with an IMAP server.

    Raises:
        imaplib.IMAP4.error
            If authentication fails.
    """

    if settings.use_ssl:
        client = imaplib.IMAP4_SSL(settings.host, settings.port)
    else:
        client = imaplib.IMAP4(settings.host, settings.port)

    client.login(settings.username, settings.password)

    return client


def search_messages(client: imaplib.IMAP4_SSL,
        mailbox: str = "INBOX",
        criteria: str = "ALL",
    ) -> list[bytes]:
    """
    Search an IMAP mailbox and return matching message IDs.
    """

    status, _ = client.select(mailbox)

    if status != "OK":
        raise RuntimeError(f"Unable to open mailbox: {mailbox}")

    status, data = client.search(None, criteria)

    if status != "OK":
        raise RuntimeError(f"Search failed: {criteria}")

    if not data or not data[0]:
        return []

    return data[0].split()


def fetch_message(
        client: imaplib.IMAP4_SSL,
        message_id: bytes,
    ) -> bytes:
    """
    Fetch a single email from IMAP.

    Returns the raw RFC 5322 bytes.
    """

    status, data = client.fetch(message_id, "(BODY[])")



    if status != "OK":
        raise RuntimeError(f"Failed to fetch message {message_id!r}")

    if not data or data[0] is None:
        raise RuntimeError(f"Empty response for message {message_id!r}")

    response = data[0]

    if not isinstance(response, tuple) or len(response) < 2:
        raise RuntimeError("Unexpected IMAP fetch response") 
    
    return response[1]


def fetch_imap_messages(
        db: Session,
        settings: IMAPSettings,
    ) -> list[Email]:

    connection = connect_imap(settings)

    imported = []

    try:
        ids = search_messages(connection)

        for message_id in ids:
            raw_email = fetch_message(connection, message_id)

            email = parse_email(
                raw_email,
                settings.provider,
            )

            imported_email = import_email(
                db,
                email,
            )

            imported.append(imported_email)

    finally:
        connection.logout()

    return imported

