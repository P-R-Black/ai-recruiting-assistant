

from unittest.mock import patch

import pytest

from app.core.config import settings
from app.mail.mail_services.importer import import_email, import_emails, import_outlook_messages
from app.mail.models import EmailProvider
from app.mail.providers.outlook import (
    connect_outlook, 
    create_outlook_settings,
    MissingRefreshTokenError
)


@pytest.fixture
def outlook_token():
    settings_obj = create_outlook_settings(
        application_id=settings.application_id,
        client_secret=settings.client_secret,
    )

    # token = connect_outlook(settings_obj)
    # yield token

    try:
        yield connect_outlook(settings_obj, interactive=False)
    except MissingRefreshTokenError:
        pytest.skip("Outlook refresh toke not available")

# def outlook_token():
#     settings_obj = create_outlook_settings(
#         application_id=settings.application_id,
#         client_secret=settings.client_secret,
#     )

#     token = connect_outlook(settings_obj)
#     yield token



def test_import_email_creates_new_email(db, email_data):
    email = import_email(db, email_data)

    assert email is not None
    assert email.message_id == email_data.message_id
    assert email.subject == email_data.subject


def test_import_email_returns_existing_email(db, email_data):
    first = import_email(db, email_data)
    second = import_email(db, email_data)

    assert first.id == second.id


def test_import_multiple_emails_with_duplicates(db, email_data):
    emails = import_emails(db, [email_data, email_data])

    assert len(emails) == 2
    assert emails[0].id == emails[1].id


def test_import_outlook_messages(db, email_data, outlook_token):

    with patch("app.mail.mail_services.importer.graph_headers") as mock_headers, \
         patch("app.mail.mail_services.importer.search_folder") as mock_search, \
         patch("app.mail.mail_services.importer.fetch_outlook_messages") as mock_fetch, \
         patch("app.mail.mail_services.importer.normalize_outlook_message") as mock_normalize:

        mock_headers.return_value = {"Authorization": "Bearer token"}

        mock_search.return_value = {
            "id": "folder123",
            "displayName": "Inbox",
        }

        mock_fetch.return_value = [
            {"id": "abc"},
            {"id": "def"},
        ]

        mock_normalize.side_effect = [
            email_data,
            email_data.model_copy(update={"message_id": "message-2"}),
        ]

        imported = import_outlook_messages(
            db,
            outlook_token,
        )

        assert len(imported) == 2

        mock_headers.assert_called_once_with(outlook_token)

        mock_search.assert_called_once()

        mock_fetch.assert_called_once()

        assert mock_normalize.call_count == 2


def test_import_real_outlook_messages(db, outlook_token):

    imported = import_outlook_messages(
        db,
        outlook_token,
    )

    assert len(imported) > 0

    assert imported[0].provider == EmailProvider.OUTLOOK