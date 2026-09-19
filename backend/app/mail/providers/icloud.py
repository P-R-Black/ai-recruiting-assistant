import imaplib

from sqlalchemy.orm import Session

from app.mail.mail_services.importers.importer import import_email
from app.mail.mail_services.parsers.parser import parse_email
from app.mail.connectors.imap_connector import connect_imap

from app.mail.mail_services.service import IMAPSettings
from app.mail.models import EmailProvider, Email

# ----------------------------
# iCloud API
# ----------------------------

def create_icloud_settings(
    username: str,
    password: str,
) -> IMAPSettings:
  
    return IMAPSettings(
        host="imap.mail.me.com",
        port=993,
        username=username,
        password=password,
        provider=EmailProvider.ICLOUD,
        use_ssl=True,
    )


def search_imap_messages(client: imaplib.IMAP4_SSL,
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
    # status, data = client.search("SEARCH", None, criteria)

    if status != "OK":
        raise RuntimeError(f"Search failed: {criteria}")

    if not data or not data[0]:
        return []

    return data[0].split()


def fetch_imap_message(
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
        ids = search_imap_messages(connection)
        
        for message_id in ids:
            raw_email = fetch_imap_message(connection, message_id)
            

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


def delete_imap_message(
    connection: imaplib.IMAP4_SSL,
    uid: bytes,
    ) -> None:

    connection.uid("STORE", uid, "+FLAGS", r"(\Deleted)")
    connection.expunge()

