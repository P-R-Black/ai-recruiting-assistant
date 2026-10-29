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

        # Simulate a successful capability response.
        instance.capability.return_value = (
            "OK",
            [b"IMAP4REV1 UIDPLUS"],
        )
        
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
    client.uid.return_value = ("OK", [b"1 2 3"])

    ids = search_imap_messages(client)

    assert ids == [b"1", b"2", b"3"]

    client.select.assert_called_once_with("INBOX")
    client.uid.assert_called_once_with("SEARCH", None, "ALL")


def test_search_messages_empty():
    client = MagicMock()
    client.select.return_value = ("OK", [b""])
    client.uid.return_value = ("OK", [b""])

    assert search_imap_messages(client) == []

    # client = MagicMock()

    # client.select.return_value = ("OK", [b""])
    # client.search.return_value = ("OK", [b""])

    # ids = search_imap_messages(client)

    # assert ids == []


def test_search_messages_search_failure():
    # client = MagicMock()

    # client.select.return_value = ("OK", [b""])
    # client.search.return_value = ("NO", [])

    # with pytest.raises(RuntimeError):
    #     search_imap_messages(client)

    client = MagicMock()
    client.select.return_value = ("OK", [b""])
    client.uid.return_value = ("NO", [])

    with pytest.raises(RuntimeError, match="Search failed"):
        search_imap_messages(client)


def test_search_messages_returns_uids():
    client = MagicMock()
    client.select.return_value = ("OK", [b""])
    client.uid.return_value = ("OK", [b"2351 2352 2353"])

    ids = search_imap_messages(client)

    assert ids == [b"2351", b"2352", b"2353"]
    client.select.assert_called_once_with("INBOX")
    client.uid.assert_called_once_with("SEARCH", None, "ALL")


def test_fetch_message():
    raw = b"From: recruiter@example.com\r\n\r\nHello"

    client = MagicMock()
    client.uid.return_value = (
        "OK",
        [(b"1 (UID 1 BODY[] {35})", raw)],
    )

    result = fetch_imap_message(client, b"1")

    assert result == raw
    client.uid.assert_called_once_with(
        "FETCH",
        b"1",
        "(BODY.PEEK[])",
    )



def test_fetch_message_failure():
    client = MagicMock()
    client.uid.return_value = ("NO", [])

    with pytest.raises(RuntimeError):
        fetch_imap_message(client, b"1")

    client.uid.assert_called_once_with(
        "FETCH",
        b"1",
        "(BODY.PEEK[])",
    )


def test_fetch_message_empty():
    client = MagicMock()
    client.uid.return_value = ("OK", [])

    with pytest.raises(RuntimeError):
        fetch_imap_message(client, b"1")

    client.uid.assert_called_once_with(
        "FETCH",
        b"1",
        "(BODY.PEEK[])",
    )


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


def test_fetch_message_skips_leading_flags_line():
    raw = b"From: recruiter@example.com\r\n\r\nHello"

    client = MagicMock()
    client.uid.return_value = (
        "OK",
        [b"1 (FLAGS (\\Seen))", (b"1 (UID 1 BODY[] {35}", raw), b")"],
    )

    assert fetch_imap_message(client, b"1") == raw


def test_fetch_message_raises_when_no_body():
    client = MagicMock()
    client.uid.return_value = ("OK", [None])

    with pytest.raises(RuntimeError):
        fetch_imap_message(client, b"1")


def test_fetch_message_raises_on_non_ok_status():
    client = MagicMock()
    client.uid.return_value = ("NO", [b"error"])

    with pytest.raises(RuntimeError):
        fetch_imap_message(client, b"1")
        

def test_delete_imap_message(mocker):
    connection = mocker.Mock()
    uid = b"2351"

    connection.uid.return_value = ("OK", [b""])
    # connection.capabilities = (b"IMAP4REV1", b"UIDPLUS")

    connection.capability.return_value = (
        "OK",
        [b"IMAP4REV1 UIDPLUS"],
    )
    delete_imap_message(connection, uid)

    assert connection.uid.call_args_list == [
        mocker.call(
            "STORE",
            uid,
            "+FLAGS",
            r"(\Deleted)",
        ),
        mocker.call("EXPUNGE", uid),
    ]



def test_delete_imap_message_without_uidplus_raises_error(mocker):
    connection = mocker.Mock()
    uid = b"2351"

    # Simulate an authenticated server without UIDPLUS support.
    connection.capability.return_value = (
        "OK",
        [b"IMAP4REV1 IMAP4"],
    )

    with pytest.raises(
        RuntimeError,
        match="UIDPLUS",
    ):
        delete_imap_message(connection, uid)

    # The function must fail before modifying or expunging the message.
    connection.uid.assert_not_called()
