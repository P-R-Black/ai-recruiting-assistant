# import os
# import webbrowser

# import msal
# from dotenv import load_dotenv

# MS_GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"

# def get_access_token(application_id, client_secret, scopes):
#     client = msal.ConfidentialClientApplication(
#         client_id=application_id,
#         client_credential=client_secret,
#         authority="https://login.microsoftonline.com/consumers/"
#     )

#     print('get_access_token called client', client)

#     # check if there is a refresh token stored
#     refresh_token = None
#     if os.path.exists('refresh_token.txt'):
#         with open('refresh_token.txt', 'r') as file:
#             refresh_token = file.read().strip()
        
#     if refresh_token:
#         # Try to acquire a new access token usin the refresh token
#         token_response = client.acquire_token_by_refresh_token(refresh_token, scopes=scopes)
#     else:
#         # No refresh token, proceed with the authoriztion code flow
#         auth_request_url = client.get_authorization_request_url(scopes)
#         webbrowser.open(auth_request_url)
#         authorization_code = input("Enter the authorization code ")

#         if not authorization_code:
#             raise ValueError("Authorization code is empty")
        
#         token_response = client.acquire_token_by_authorization_code(
#             code=authorization_code,
#             scopes=scopes
#         )
    
#     if 'access_token' in token_response:
#         # Store the refresh token security
#         if 'refresh_token' in token_response:
#             with open('refresh_token.txt', 'w') as file:
#                 file.write(token_response['refresh_token'])
        
#         return token_response['access_token']
#     else:
#         raise Exception('failed to acquire access token: ', + str(token_response))



# def main():
#     load_dotenv()
#     APPLICATION_ID = os.getenv('APPLICATION_ID')
#     CLIENT_SECRET = os.getenv('CLIENT_SECRET')
#     SCOPES = ['User.Read', 'Mail.ReadWrite', 'Mail.Send']

#     try:
#         access_token = get_access_token(
#             application_id=APPLICATION_ID,
#             client_secret=CLIENT_SECRET,
#             scopes=SCOPES)
#         headers = {
#             'Authorization': 'Bearer ' + access_token
#         }
#         print('headers:', headers)
#     except Exception as e:
#         print('Error:', {e})

# main()

import email
from email import policy

from bs4 import BeautifulSoup


def extract_html_from_email(email_file_path):
    # 1. Read the email file using the standard policy rules
    with open(email_file_path, 'rb') as f:
        msg = email.message_from_bytes(f.read(), policy=policy.default)
    
    # 2. Extract the HTML payload from the email structure
    html_content = None
    if msg.is_multipart():
        # Iterate through email parts to locate the HTML section
        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                html_content = part.get_payload(
                    decode=True
                    ).decode(part.get_content_charset() or 'utf-8')
                break
    else:
        # Handle non-multipart emails
        if msg.get_content_type() == 'text/html':
            html_content = msg.get_payload(
                decode=True).decode(
                    msg.get_content_charset() or 'utf-8')
            
    return html_content

def parse_html_content(html_str):
    print('parse_html_content called')
    if not html_str:
        return "No HTML content found in this email."
        
    # 3. Parse the HTML using Beautiful Soup
    soup = BeautifulSoup(html_str, 'html.parser')
    print('DEBUG soup:', soup)
    
    
    # Example A: Extract all visible plain text cleanly
    plain_text = soup.get_text(separator=' ', strip=True)
    
    # Example B: Extract specific elements (like all hyperlinks)
    links = [a['href'] for a in soup.find_all('a', href=True)]
    
    return {
        "text": plain_text,
        "links": links
    }

# --- Execution ---
file_path = "example_email.eml" # Replace with your email file path
# raw_html = extract_html_from_email(file_path)
# parsed_data = parse_html_content(raw_html)

# print("--- Cleaned Text Body ---")
# print(parsed_data["text"])

# print("\n--- Extracted Links ---")
# print(parsed_data["links"])
