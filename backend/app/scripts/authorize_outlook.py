import webbrowser

from app.core.config import settings
from app.mail.providers.outlook import (
    create_outlook_client,
    create_outlook_settings,
    save_refresh_token,
)
from app.services.service import OutlookSettings


def authorize_outlook(settings: OutlookSettings):
    client = create_outlook_client(settings)

    scopes = [
        "User.Read",
        "Mail.ReadWrite",
        "Mail.Send",
    ]

    auth_url = client.get_authorization_request_url(scopes)

    webbrowser.open(auth_url)

    code = input("Authorization code: ")

    token_response = client.acquire_token_by_authorization_code(
        code=code,
        scopes=scopes,
    )

    if "refresh_token" not in token_response:
        raise RuntimeError(token_response)

    save_refresh_token(token_response["refresh_token"])



def main():
    settings_obj = create_outlook_settings(
            application_id=settings.application_id,
            client_secret=settings.client_secret,
        )
    
    authorize_outlook(settings_obj)


if __name__ == "__main__":
    main()