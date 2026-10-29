import imaplib
import logging

from sqlalchemy.orm import Session

from app.mail.connectors.imap_connector import connect_imap
from app.mail.mail_services.importers.importer import import_email
from app.mail.mail_services.parsers.parser import parse_email
from app.mail.mail_services.service import IMAPSettings
from app.mail.models import Email, EmailProvider

logger = logging.getLogger(__name__)

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


def search_imap_messages(
        client: imaplib.IMAP4_SSL,
        mailbox: str = "INBOX",
        criteria: str = "ALL",
    ) -> list[bytes]:
    """
    Search an IMAP mailbox and return matching message IDs.
    """

    status, _ = client.select(mailbox)

    if status != "OK":
        raise RuntimeError(f"Unable to open mailbox: {mailbox}")

    # status, data = client.search(None, criteria)
    # status, data = client.uid("SEARCH", None, criteria) <- currently workin code

    status, data = client.uid("SEARCH", None, criteria)
    # status, data = client.uid("SEARCH", None, "All")

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
    # status, data = client.fetch(message_id, "(BODY[])")
    status, data = client.uid("FETCH", message_id, "(BODY.PEEK[])")

    if status != "OK":
        raise RuntimeError(f"Failed to fetch message {message_id!r}: {status}")

    for item in data or []:
        if isinstance(item, tuple) and len(item) >= 2 and item[1]:
            return item[1]

    logger.error("Message %r fetch status=%r data=%r", message_id, status, repr(data)[:500])
    raise RuntimeError(f"No message body in FETCH response for {message_id!r}")


    # if not data or data[0] is None:
    #     raise RuntimeError(f"Empty response for message {message_id!r}")

    # response = data[0]

    # if not isinstance(response, tuple) or len(response) < 2:
    #     logger.error("Message_id %r fetch status=%r data=%r", message_id, status, data)
    #     raise RuntimeError("Unexpected IMAP fetch response") 
    
    # return response[1]


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

    caps = get_capabilities(connection)
    can_uid_expunge = "UIDPLUS" in caps

    if not can_uid_expunge:
        raise RuntimeError("Server lacks UIDPLUS; refusing to flag without selective expunge")

    status, _ = connection.uid("STORE", uid, "+FLAGS", r"(\Deleted)")
    if status != "OK":
        raise RuntimeError(f"Failed to mark UID {uid!r} as deleted")

    status, _ = connection.uid("EXPUNGE", uid)
    if status != "OK":
        raise RuntimeError(f"Failed to expunge UID {uid!r}")
    
    # status, _ = connection.uid("STORE", uid, "+FLAGS", r"(\Deleted)")
    # if status != "OK":
    #     raise RuntimeError(f"Failed to mark message UID {uid!r} as deleted")

    # capabilities = {
    #     capability.upper()
    #     for capability in connection.capabilities
    # }

    # if b"UIDPLUS" not in capabilities:
    #     print('connection.capabilities:', connection.capabilities)
    #     logger.info(
    #         "IMAP server does not support UIDPLUS; "
    #         "message was marked deleted but was not selectively expunged."
    #     )
    #     raise RuntimeError(
    #         "IMAP server does not support UIDPLUS; "
    #         "message was marked deleted but was not selectively expunged."
    #     )

    # status, _ = connection.uid("EXPUNGE", uid)

    # if status != "OK":
    #     raise RuntimeError(f"Failed to expunge message UID {uid!r}")
    
    # connection.uid("STORE", uid, "+FLAGS", r"(\Deleted)")
    # connection.expunge()


def get_capabilities(connection: imaplib.IMAP4_SSL) -> set[str]:
    typ, data = connection.capability()
    if typ != "OK" or not data or not data[0]:
        return set()
    return set(data[0].decode().upper().split())


def require_uidplus(connection: imaplib.IMAP4_SSL) -> None:
    if "UIDPLUS" not in get_capabilities(connection):
        raise RuntimeError(
            "IMAP server does not support UIDPLUS; cannot selectively expunge"
        )