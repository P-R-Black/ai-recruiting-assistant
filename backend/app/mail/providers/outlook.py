from pathlib import Path

import httpx
import msal

from app.core.config import BASE_DIR
from app.mail.models import EmailProvider
from app.mail.schemas import EmailCreate
from app.services.service import OutlookSettings

# ----------------------------
# Outlook API
# ----------------------------

REFRESH_TOKEN_PATH = Path("refresh_token.txt")

TOKEN_DIRECTORY = BASE_DIR / ".tokens"
TOKEN_DIRECTORY.mkdir(parents=True, exist_ok=True)

REFRESH_TOKEN_PATH = TOKEN_DIRECTORY / "outlook_refresh_token.txt"

MS_GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


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


def get_outlook_access_token(
    settings: OutlookSettings,
    scopes: list[str],
    *,
    interactive: bool = True
):
    """
    Acquire an Outlook access token using a stored refresh token.
    """

    client = create_outlook_client(settings)

    refresh_token = load_refresh_token()

    if refresh_token is None:
        raise MissingRefreshTokenError(
            "No Outlook refresh token found. "
            "Run scripts/authorize_outlook.py first."
        )

    return client.acquire_token_by_refresh_token(
        refresh_token,
        scopes=scopes,
    )

    

# def get_outlook_access_token(settings: OutlookSettings, scopes: list[str]):
#     """
#     Get an access token for Microsoft Outlook using the MSAL library.

#     Args:
#         application_id (str): The application ID (client ID) of your Azure AD app.
#         client_secret (str): The client secret of your Azure AD app.
#         scopes (list): A list of scopes for which the access token is requested.

#     Returns:
#         str: The access token.
#     """
#     client = create_outlook_client(settings)

#     # check if there is a refresh token stored
#     refresh_token = load_refresh_token()

#     if refresh_token:
#         # Try to acquire a new access token using the refresh token
#         token_response = client.acquire_token_by_refresh_token(refresh_token, scopes=scopes)
#     else:
#         # No refresh token, proceed with the authorization code flow
#         auth_request_url = client.get_authorization_request_url(scopes)
#         webbrowser.open(auth_request_url)
#         authorization_code = input("Enter the authorization code: ")

#         if not authorization_code:
#             raise ValueError("Authorization code is empty")

#         token_response = client.acquire_token_by_authorization_code(
#             code=authorization_code,
#             scopes=scopes
#         )


#     if "refresh_token" in token_response:
#         save_refresh_token(token_response["refresh_token"])

#     if 'access_token' in token_response:
#         return token_response['access_token']
#     else:
#         raise Exception('Failed to acquire access token: ' + str(token_response))




def graph_headers(access_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {access_token}",
    }


def connect_outlook(
        settings: OutlookSettings,
        *,
        interactive: bool = True,
    ) -> str:
    token_response = get_outlook_access_token(
        settings=settings,
        scopes=["User.Read", "Mail.ReadWrite", "Mail.Send"],
        interactive=interactive,
    )

    if "refresh_token" in token_response:
        save_refresh_token(token_response["refresh_token"])

    access_token = token_response.get("access_token")

    if not access_token:
        raise RuntimeError(
            f"Failed to acquire Outlook access token: {token_response}"
        )

    return access_token

# def connect_outlook(settings: OutlookSettings) -> str:
#     return get_outlook_access_token(
#         settings=settings, 
        # scopes=[
        #     "User.Read", 
        #     "Mail.ReadWrite", 
        #     "Mail.Send",
        #     ],
#         )
    


def fetch_outlook_messages(
        settings: OutlookSettings,
        fields: str = "*",
        folder_id: str | None = None,
        top: int = 50,
        order_by: str = "receivedDateTime",
        order_by_desc: bool = True,
        max_results: int = 100
    ):
    """
    Fetch messages from Microsoft Outlook using the Microsoft Graph API.

    Returns the raw Microsoft Graph API response containing the messages.
    """

    if folder_id is None:
        endpoint = f"{MS_GRAPH_BASE_URL}/me/messages"
    else:
        endpoint = f"{MS_GRAPH_BASE_URL}/me/mailFolders/{folder_id}/messages"

    # endpoint = f"
    # {MS_GRAPH_BASE_URL}/me/mailFolders/{folder_id}/messages" 
    # if folder_id else f"{MS_GRAPH_BASE_URL}/me/messages"

    headers = graph_headers(settings)

    params = {
        "$select": fields,
        "$top": top,
        "$orderby": f"{order_by} {'desc' if order_by_desc else 'asc'}",

    }

    messages = []
    next_url = endpoint

    while next_url and len(messages) < max_results:

        response = httpx.get(
            next_url,
            headers=headers,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        payload = response.json()

        messages.extend(payload.get("value", []))

        next_url = payload.get("@odata.nextLink")

        params = None  # Clear params for subsequent requests


    return messages[:max_results]




def search_folder(headers, folder_name='drafts'):
    endpoint = f"{MS_GRAPH_BASE_URL}/me/mailFolders"
    response = httpx.get(endpoint, headers=headers)
    response.raise_for_status()
    folders = response.json().get('value', [])
    for folder in folders:
        if folder['displayName'].lower() == folder_name.lower():
            return folder
    return None


def get_sub_folders(headers, folder_id):
    endpoint = f"{MS_GRAPH_BASE_URL}/me/mailFolders/{folder_id}/childFolders"
    response = httpx.get(endpoint, headers=headers)
    response.raise_for_status()
    return response.json().get('value', [])




def normalize_outlook_message(message: dict) -> EmailCreate:
    """
    Convert a Microsoft Graph message into the application's EmailCreate model.
    """

    sender = (
        message.get("from", {})
        .get("emailAddress", {})
        .get("address", "")
    )

    recipients = [
        r.get("emailAddress", {}).get("address", "")
        for r in message.get("toRecipients", [])
    ]

    return EmailCreate(
        provider=EmailProvider.OUTLOOK,
        message_id=message.get("id", ""),
        subject=message.get("subject", ""),
        sender=sender,
        recipient=recipients[0] if recipients else "",
        raw_body=message.get("bodyPreview", ""),
        received_at=message.get("receivedDateTime"),
    )




# def _create_outlook_settings(
#     username: str,
#     password: str,
# ) -> IMAPSettings:
#     return IMAPSettings(
#         host="outlook.office365.com",
#         port=993,
#         username=username,
#         password=password,
#         provider=EmailProvider.OUTLOOK,
#         use_ssl=True,
#     )



# import os
# import httpx
# from dotenv import load_dotenv
# from ms_graph import get_access_token, MS_GRAPH_BASE_URL

# def main():
#     load_dotenv()
#     APPLICATION_ID = os.getenv('APPLICATION_ID')
#     CLIENT_SECRET = os.getenv('CLIENT_SECRET')
#     SCOPES = ['User.Read', 'Mail.ReadWrite']

#     endpoint = f"{MS_GRAPH_BASE_URL}/me/messages"

#     try:
#         access_token = get_access_token(
#             application_id=APPLICATION_ID,
#             client_secret=CLIENT_SECRET,
#             scopes=SCOPES
#         )
#         headers = {
#             'Authorization': 'Bearer ' + access_token
#         }

#         for i in range(0, 4, 2):
#             params = {
#                 '$top': 2,
#                 '$select': '*',
#                 '$skip': 1,
#                 '$orderby': 'receivedDateTime desc'
#             }

#             # to retrieve the emails
#             response = httpx.get(endpoint, headers=headers, params=params)

#             json_response = response.json()

#             for mail_message in json_response.get('value', []):
#                 if mail_message['isDraft']:
#                     print("Subject:", mail_message['subject'])
#                     print("To:", mail_message['toRecipients'])
#                     print("Is Read:", mail_message['isRead'])
#                     print("Received Date Time:", mail_message['receivedDateTime'])
#                     print()
#                 else:
                    # print("Subject:", mail_message['subject'])
                    # print("To:", mail_message['toRecipients'])
                    # print(
                    #     "From", mail_message['from']['emailAddress']['name'], 
                    #     f"({mail_message['from']['emailAddress']['address']})"
                    #     )
                    # print("Is Read:", mail_message['isRead'])
                    # print("Received Date Time:", mail_message['receivedDateTime'])
#                     print()
#                 print('-' * 150)
#     except httpx.HTTPStatusError as e:
#         print(f"HTTP Error: {e}")
#     except Exception as e:
#         print(f"Error: {e}")



# main()



# import base64
# import mimetypes
# from pathlib import Path

# def search_folder(headers, folder_name='drafts'):
#     endpoint = f"{MS_GRAPH_BASE_URL}/me/mailFolders"
#     response = httpx.get(endpoint, headers=headers)
#     response.raise_for_status()
#     folders = response.json().get('value', [])
#     for folder in folders:
#         if folder['displayName'].lower() == folder_name.lower():
#             return folder
#     return None




# def get_messages(
#         headers, 
#         folder_id=None, 
#         fields='*', 
#         top=5, 
#         order_by='receivedDateTime', 
#         order_by_desc=True, 
#         max_results=20
#     ):
#     if folder_id is None:
#         endpoint = f"{MS_GRAPH_BASE_URL}/me/messages"
#     else:
#         endpoint = f"{MS_GRAPH_BASE_URL}/me/mailFolders/{folder_id}/messages"
    
#     params = {
#         '$select': fields,
#         '$top': min(top, max_results),
#         '$orderby': f'{order_by} {"desc" if order_by_desc else "asc"}'
#     }

#     messages = []
#     next_link = endpoint
#     while next_link and len(messages) < max_results:
#         response = httpx.get(next_link, headers=headers, params=params)

#         if response.status_code != 200:
#             raise Exception(f"Failed to retrieve emails: {response.json()}")

#         json_response = response.json()
#         messages.extend(json_response.get('value', []))
#         next_link = json_response.get('@odata.nextLink', None)
#         params = None # clear params for subsequent requests

#         if next_link and len(messages) + top > max_results:
#             params = {
#                 "$top": max_results - len(messages)
#             }
    
#     return messages[:max_results]


# def main():
#     try:
        
#         load_dotenv()
#         APPLICATION_ID = os.getenv('APPLICATION_ID')
#         CLIENT_SECRET = os.getenv('CLIENT_SECRET')
#         SCOPES = ['User.Read', 'Mail.ReadWrite']

#         access_token = get_access_token(
#                 application_id=APPLICATION_ID,
#                 client_secret=CLIENT_SECRET,
#                 scopes=SCOPES)
        
#         headers = {
#                 'Authorization': 'Bearer ' + access_token
#             }
        
        
#         folder_name = 'Inbox'
#         target_folder = search_folder(headers, folder_name)
#         folder_id = target_folder['id']


#         messages = get_messages(headers, folder_id)
        
#         print('DEBU got messages')

        # for message in messages:
        #     print('Subject:', message['subject'])
        #     print('-' * 50)
        
        # # get messages from subfolders
        # sub_folders = get_sub_folders(headers, folder_id)
        # for sub_folder in sub_folders:
        #     if sub_folder['displayName'].lower() == 'sub folder':
        #         sub_folder_id = sub_folder['id']
        #         messages = get_messages(headers, sub_folder_id)
        #         for message in messages:
        #             print(f'Sub Folder Name: {sub_folder["displayName"]}')
        #             print('Subject:', message['subject'])
        #             print('-' * 50)
    
#     except httpx.HTTPStatusError as e:
#         print(f"HTTP Error: {e}")
#     except Exception as e:
#         print(f"Error: {e}")



# main()

