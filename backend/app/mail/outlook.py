

from app.mail.service import OutlookSettings

# ----------------------------
# IMAP
# ----------------------------

def connect_outlook(settings: OutlookSettings):
    """
    Connects to Microsoft Outlook server.

    Raises:
            ?
    """

    print('DEBU settings', settings)
    # if settings.use_ssl:
    #     client = imaplib.IMAP4_SSL(settings.host, settings.port)
    # else:
    #     client = imaplib.IMAP4(settings.host, settings.port)

    # client.login(settings.username, settings.password)

    # return client