import imaplib

from app.mail.mail_services.service import IMAPSettings

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


