
from backend.app.mail.service import IMAPSettings
from app.mail.schemas import EmailProvider

# ----------------------------
# Outlook API
# ----------------------------

def create_outlook_settings(
    username: str,
    password: str,
) -> IMAPSettings:
    return IMAPSettings(
        host="outlook.office365.com",
        port=993,
        username=username,
        password=password,
        provider=EmailProvider.OUTLOOK,
        use_ssl=True,
    )

def fetch_outlook_messages():
    pass