
from app.mail.mail_services.service import IMAPSettings
from app.mail.models import EmailProvider

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


def fetch_icloud_messages():
    pass
