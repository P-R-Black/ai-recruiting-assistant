from datetime import datetime, timezone

import pytest

from app.core.config import settings
from app.mail.models import EmailProvider

# from app.mail.outlook import connect_outlook
from app.mail.providers.outlook import (
    connect_outlook,
    create_outlook_settings,
    fetch_outlook_messages,
    graph_headers,
    normalize_outlook_message,
    search_folder,
)


@pytest.fixture
def outlook_token():
    settings_obj = create_outlook_settings(
        application_id=settings.application_id,
        client_secret=settings.client_secret,
    )

    token = connect_outlook(settings_obj)
    yield token


    
def test_connect_to_real_outlook(outlook_token):

    assert outlook_token is not None



def test_graph_headers(outlook_token):

    headers = graph_headers(outlook_token)

    assert headers is not None
    assert headers["Authorization"].startswith("Bearer ")


def test_fetch_outlook_messages(outlook_token):

    # Fetch messages from the inbox
 
    # messages = fetch_outlook_messages(outlook_token, top=5, max_results=5)
    # print('DEBUG fetched messages:', messages, '\n')

    headers = graph_headers(outlook_token)
    folder_name = 'Inbox'
    target_folder = search_folder(headers, folder_name)
    print('DEBUG target_folder:', target_folder, '\n')
    folder_id = target_folder['id']
    print('DEBUG folder_id:', folder_id, '\n')

    messages = fetch_outlook_messages(outlook_token, folder_id=folder_id, top=5, max_results=5)
    # for message in messages:
    #     print('Subject:', message['subject'])
    #     print("To:", message['toRecipients'])
    #     print(
    #         "From", message['from']['emailAddress']['name'], 
    #         f"({message['from']['emailAddress']['address']})"
    #         )
    #     print("Is Read:", message['isRead'])
    #     # Print first 100 characters of the body
    #     # print("Body:", message['body']['content'][:100], '...') 
    #     print("Body Preview:", message['bodyPreview'][:400], '...')  #
    #     print("Received Date Time:", message['receivedDateTime'])
    #     print('-' * 50)


    assert messages is not None
    assert len(messages) > 0


def test_normalize_outlook_message():
    graph_message = {
        "id": "abc123",
        "subject": "Junior Frontend Developer",
        "from": {
            "emailAddress": {
                "name": "OpenAI Recruiting",
                "address": "jobs@openai.com",
            }
        },
        "toRecipients": [
            {
                "emailAddress": {
                    "name": "Paul Black",
                    "address": "paul@example.com",
                }
            }
        ],
        "receivedDateTime": "2026-08-02T03:15:22Z",
        "bodyPreview": (
            "Hi Paul,\n\n"
            "We're excited to invite you to apply for our "
            "Junior Frontend Developer position."
        ),
    }

    email = normalize_outlook_message(graph_message)
    print('DEBUG normalized email:', email, '\n')

    assert email.provider == EmailProvider.OUTLOOK
    assert email.message_id == "abc123"
    assert email.subject == "Junior Frontend Developer"
    assert email.sender == "jobs@openai.com"
    assert email.recipient == "paul@example.com"
    assert email.raw_body.startswith("Hi Paul")
    assert email.received_at == datetime.strptime(
        "2026-08-02T03:15:22Z", "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def test_normalize_outlook_message_missing_fields():
    graph_message = {
        "id": "abc123",
        "receivedDateTime": "2026-08-02T03:15:22Z",
    }
    email = normalize_outlook_message(graph_message)

    assert email.provider == EmailProvider.OUTLOOK
    assert email.message_id == "abc123"
    assert email.subject == ""
    assert email.sender == ""
    assert email.recipient == ""
    assert email.raw_body == ""


"""
Run individual tests
uv run pytest tests/test_jobs_api.py
make test TEST=tests/test_jobs_api.py
uv run pytest -s (to show print statements for passing tests)
uv run pytest -s tests/test_jobs_api.py (to show print statements for passing tests)
uv run pytest tests/test_mail_service.py::test_detect_job_email_true (to run specific test)
"""