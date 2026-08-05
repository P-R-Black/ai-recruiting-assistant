from unittest.mock import MagicMock, call, patch

import pytest

from app.mail.models import EmailProvider
from app.services.sync import fetch_messages, normalize_message, sync_all_providers, sync_provider


@patch("app.services.sync.fetch_icloud_messages")
def test_fetch_messages_icloud(mock_fetch):
    settings = MagicMock()

    mock_fetch.return_value = ["email1"]

    result = fetch_messages(
        EmailProvider.ICLOUD,
        settings,
    )

    assert result == ["email1"]
    mock_fetch.assert_called_once_with(settings)


def test_fetch_messages_unknown_provider():
    with pytest.raises(ValueError):
        fetch_messages(
            EmailProvider.GMAIL,
            MagicMock(),
        )


@patch("app.mail.providers.outlook.normalize_outlook_message")
def test_normalize_outlook(mock_normalize):

    message = {"id": "123"}

    email = MagicMock()

    mock_normalize.return_value = email

    result = normalize_message(
        EmailProvider.OUTLOOK,
        message,
    )

    assert result is email

    mock_normalize.assert_called_once_with(message)



def test_normalize_icloud():

    email = MagicMock()

    result = normalize_message(
        EmailProvider.ICLOUD,
        email,
    )

    assert result is email


@patch("app.services.sync.import_emails")
@patch("app.services.sync.normalize_message")
@patch("app.services.sync.fetch_messages")
def test_sync_provider(
    mock_fetch,
    mock_normalize,
    mock_import,
):
    db = MagicMock()
    settings = MagicMock()

    print('mock_fetch.return_value:', mock_fetch.return_value)
    mock_fetch.return_value = [{"id": "1"}, {"id": "2"},]
    mock_normalize.side_effect = ["email1", "email2"]
    mock_import.return_value = ["imported_email1", "imported_email2"]

    result = sync_provider(
        db,
        EmailProvider.ICLOUD,
        settings,
    )

    assert result == ["imported_email1", "imported_email2"]

    mock_fetch.assert_called_once_with(EmailProvider.ICLOUD, settings)
    assert mock_normalize.call_count == 2
    assert mock_normalize.call_args_list == [
        call(EmailProvider.ICLOUD, {"id": "1"}),
        call(EmailProvider.ICLOUD, {"id": "2"}),
    ]
    mock_import.assert_called_once_with(db, ["email1", "email2"])

@patch("app.services.sync.fetch_outlook_messages")
def test_fetch_messages_outlook(mock_fetch):
    settings = MagicMock()

    mock_fetch.return_value = ["email1"]

    result = fetch_messages(
        EmailProvider.OUTLOOK,
        settings,
    )

    assert result == ["email1"]

    mock_fetch.assert_called_once_with(settings)


def test_normalize_unknown_provider():

    with pytest.raises(ValueError):
        normalize_message(
            EmailProvider.GMAIL,
            {},
        )


@patch("app.services.sync.sync_provider")
def test_sync_all_providers(mock_sync):

    db = MagicMock()

    providers = {
        EmailProvider.ICLOUD: MagicMock(),
        EmailProvider.OUTLOOK: MagicMock(),
    }

    sync_all_providers(
        db,
        providers,
    )

    assert mock_sync.call_count == 2

    mock_sync.assert_any_call(
        db,
        EmailProvider.ICLOUD,
        providers[EmailProvider.ICLOUD],
    )

    mock_sync.assert_any_call(
        db,
        EmailProvider.OUTLOOK,
        providers[EmailProvider.OUTLOOK],
    )