from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.mail.connectors.imap_connector import (
    connect_imap, 
)


from app.mail.providers.icloud import (
    fetch_imap_messages,
    fetch_imap_message,
    search_imap_messages,
    delete_imap_message
)
from app.mail.models import EmailProvider
from app.mail.schemas import EmailCreate
from app.mail.mail_services.service import IMAPSettings


def sample_job_email() -> EmailCreate:
    return EmailCreate(
        provider=EmailProvider.APPLE,
        message_id="<123@example.com>",
        subject="Junior Frontend Developer",
        sender="Talent Team <talent@google.com>",
        recipient="paul@example.com",
        received_at=datetime.now(timezone.utc),
        raw_body="""
            Junior Frontend Developer

            OpenAI

            Orlando, FL

            Salary: $180,000 - $220,000

            Apply here:
            https://jobs.openai.com/12345
            """,
                )


def test_connect_imap():
    settings = IMAPSettings(
        host="imap.example.com",
        port=993,
        username="user@example.com",
        password="secret",
        provider=EmailProvider.APPLE
    )

    with patch("app.mail.connectors.imap_connector.imaplib.IMAP4_SSL") as mock_client:
        instance = MagicMock()
        mock_client.return_value = instance

        client = connect_imap(settings)

        mock_client.assert_called_once_with(
            "imap.example.com",
            993,
        )

        instance.login.assert_called_once_with(
            "user@example.com",
            "secret",
        )

        assert client == instance


def test_search_messages():
    client = MagicMock()

    client.select.return_value = ("OK", [b""])
    client.search.return_value = ("OK", [b"1 2 3"])

    ids = search_imap_messages(client)

    assert ids == [b"1", b"2", b"3"]

    client.select.assert_called_once_with("INBOX")
    client.search.assert_called_once_with(None, "ALL")


def test_search_messages_empty():
    client = MagicMock()

    client.select.return_value = ("OK", [b""])
    client.search.return_value = ("OK", [b""])

    ids = search_imap_messages(client)

    assert ids == []


def test_search_messages_search_failure():
    client = MagicMock()

    client.select.return_value = ("OK", [b""])
    client.search.return_value = ("NO", [])

    with pytest.raises(RuntimeError):
        search_imap_messages(client)



def test_fetch_message():
    raw = b"From: recruiter@example.com\r\n\r\nHello"

    client = MagicMock()

    client.fetch.return_value = (
        "OK",
        [(b"1 (BODY[] {35})", raw)],
    )

    result = fetch_imap_message(client, b"1")
   

    assert result == raw

    client.fetch.assert_called_once_with(
        b"1",
        "(BODY[])",
    )



def test_fetch_message_failure():
    client = MagicMock()

    client.fetch.return_value = ("NO", [])

    with pytest.raises(RuntimeError):
        fetch_imap_message(client, b"1")


def test_fetch_message_empty():
    client = MagicMock()

    client.fetch.return_value = ("OK", [])

    with pytest.raises(RuntimeError):
        fetch_imap_message(client, b"1")


def test_fetch_imap_messages(monkeypatch, db):
    class FakeConnection:
        def __init__(self):
            self.logged_out = False

        def logout(self):
            self.logged_out = True

    connection = FakeConnection()

    monkeypatch.setattr(
        "app.mail.providers.icloud.connect_imap",
        lambda settings: connection,
    )

    monkeypatch.setattr(
        "app.mail.providers.icloud.search_imap_messages",
        lambda conn: [b"1", b"2"],
    )

    monkeypatch.setattr(
        "app.mail.providers.icloud.fetch_imap_message",
        lambda conn, message_id: b"raw email",
    )

    email = EmailCreate(
        provider=EmailProvider.APPLE,
        message_id="<123@example.com>",
        subject="Python Developer",
        sender="recruiter@example.com",
        recipient="paul@example.com",
        received_at=datetime.now(timezone.utc),
        raw_body="Interview invitation",
    )

    monkeypatch.setattr(
        "app.mail.mail_services.parsers.mime_parser.build_parsed_email",
        lambda raw, provider: email,
    )

    import_calls = []

    def fake_import(db, email):
        import_calls.append(email)
        return email


    monkeypatch.setattr(
        "app.mail.providers.icloud.import_email",
        fake_import,
    )



    settings = IMAPSettings(
        host="imap.example.com",
        port=993,
        username="user",
        password="password",
        provider=EmailProvider.APPLE,
    )


    result = fetch_imap_messages(
        db,
        settings,
    )

    assert len(result) == 2
    assert len(import_calls) == 2
    assert connection.logged_out is True




def test_delete_imap_message(mocker):
    connection = mocker.Mock()
    uid = b"2351"

    delete_imap_message(connection, uid)

    connection.uid.assert_called_once_with(
        "STORE",
        uid,
        "+FLAGS",
        r"(\Deleted)",
    )

    connection.expunge.assert_called_once_with()