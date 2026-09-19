from pathlib import Path
import requests

import msal

from app.core.config import BASE_DIR
from app.mail.models import EmailProvider
from app.mail.mail_services.service import OutlookSettings

REFRESH_TOKEN_PATH = Path("refresh_token.txt")

TOKEN_DIRECTORY = BASE_DIR / ".tokens"
TOKEN_DIRECTORY.mkdir(parents=True, exist_ok=True)

REFRESH_TOKEN_PATH = TOKEN_DIRECTORY / "outlook_refresh_token.txt"

MS_GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"

# ----------------------------
# OUTLOOK
# ----------------------------

class MissingRefreshTokenError(RuntimeError):
    """
    Raised when an Outlook refresh token cannot be found.

    This exception indicates that Outlook authentication cannot continue
    without interactive user authorization. Callers may catch this
    exception to skip Outlook-related operations in non-interactive
    environments such as automated tests or CI.
    """

    def __init__(
        self,
        message: str = (
            "No Outlook refresh token was found. "
            "Interactive authentication is required."
        ),
    ):
        super().__init__(message)


def create_outlook_settings(application_id, client_secret) -> OutlookSettings:
    return OutlookSettings(
        application_id=application_id,
        client_secret=client_secret,
        tenant_id="consumers",
        authority="https://login.microsoftonline.com/consumers/",
        provider=EmailProvider.OUTLOOK

    )

def create_outlook_client(settings: OutlookSettings):

    client = msal.ConfidentialClientApplication(
        client_id=settings.application_id,
        client_credential=settings.client_secret,
        authority="https://login.microsoftonline.com/consumers/",

    )

    return client


def load_refresh_token():
    """
    Load a previously saved Outlook refresh token.

    Returns:
        The refresh token if it exists, otherwise None.
    """
    if not REFRESH_TOKEN_PATH.exists():
        return None

    token = REFRESH_TOKEN_PATH.read_text().strip()

    return token or None


def save_refresh_token(refresh_token):
    """
    Save the Outlook refresh token to a file.

    Args:
        refresh_token (str): The refresh token to save.
    """
    REFRESH_TOKEN_PATH.write_text(refresh_token)


