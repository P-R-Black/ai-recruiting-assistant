from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.mail.connectors.imap_connector import (
    connect_imap, 
    fetch_imap_messages, 
    fetch_message, 
    search_messages
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

    with patch("app.mail.mail_services.imap_connector.imaplib.IMAP4_SSL") as mock_client:
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

    ids = search_messages(client)

    assert ids == [b"1", b"2", b"3"]

    client.select.assert_called_once_with("INBOX")
    client.search.assert_called_once_with(None, "ALL")


def test_search_messages_empty():
    client = MagicMock()

    client.select.return_value = ("OK", [b""])
    client.search.return_value = ("OK", [b""])

    ids = search_messages(client)

    assert ids == []


def test_search_messages_search_failure():
    client = MagicMock()

    client.select.return_value = ("OK", [b""])
    client.search.return_value = ("NO", [])

    with pytest.raises(RuntimeError):
        search_messages(client)



def test_fetch_message():
    raw = b"From: recruiter@example.com\r\n\r\nHello"

    client = MagicMock()

    client.fetch.return_value = (
        "OK",
        [(b"1 (BODY[] {35})", raw)],
    )

    result = fetch_message(client, b"1")
   

    assert result == raw

    client.fetch.assert_called_once_with(
        b"1",
        "(BODY[])",
    )



def test_fetch_message_failure():
    client = MagicMock()

    client.fetch.return_value = ("NO", [])

    with pytest.raises(RuntimeError):
        fetch_message(client, b"1")


def test_fetch_message_empty():
    client = MagicMock()

    client.fetch.return_value = ("OK", [])

    with pytest.raises(RuntimeError):
        fetch_message(client, b"1")


def test_fetch_imap_messages(monkeypatch, db):
    class FakeConnection:
        def __init__(self):
            self.logged_out = False

        def logout(self):
            self.logged_out = True

    connection = FakeConnection()

    monkeypatch.setattr(
        "app.mail.mail_services.imap_connector.connect_imap",
        lambda settings: connection,
    )

    monkeypatch.setattr(
        "app.mail.mail_services.imap_connector.search_messages",
        lambda conn: [b"1", b"2"],
    )

    monkeypatch.setattr(
        "app.mail.mail_services.imap_connector.fetch_message",
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
        "app.mail.mail_services.imap_connector.parse_email",
        lambda raw, provider: email,
    )

    imported = []

    def fake_import(db, email):
        imported.append(email)
        return email

    monkeypatch.setattr(
        "app.mail.mail_services.imap_connector.import_email",
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
    assert len(imported) == 2
    assert connection.logged_out is True