import pytest
from app.core.config import settings

from sqlalchemy.orm import Session

from datetime import datetime, timezone


from app.mail.normalizer.base import ParsedEmail
from app.mail.models import EmailProvider, Email

from app.orchestrator.orchestrator import (
    process_email, 
    run_outlook_ingestion,
    run_imap_ingestion,
    run_mail_ingestion,
    JOB_BOARD_PARSERS
    )

from app.mail.providers.outlook import (
    connect_outlook,
    create_outlook_settings,
    fetch_outlook_messages,
    graph_headers,
    normalize_outlook_message,
    search_folder,
    delete_outlook_message,
    MissingRefreshTokenError
)

from app.mail.providers.icloud import create_icloud_settings
from app.mail.connectors.imap_connector import (
    connect_imap
    )

@pytest.fixture
def outlook_token():
    settings_obj = create_outlook_settings(
        application_id=settings.application_id,
        client_secret=settings.client_secret,
    )

    try:
        yield connect_outlook(settings_obj, interactive=False)
    except MissingRefreshTokenError:
        pytest.skip("Outlook refresh toke not available")

def test_process_email_ignores_unknown_sender(db):
    email = ParsedEmail(
        message_id="<123@example.com>",
        provider=EmailProvider.ICLOUD,
        subject="Some email",
        sender="someone@example.com",
        recipient="me@example.com",
        received_at=datetime.now(timezone.utc),
        text_body="",
        html_body="",
    )

    process_email(db, email)

    assert db.query(Email).count() == 0

def test_run_outlook_ingestion_connects_to_outlook(mocker):
    settings = mocker.Mock()
    token = "test-token"

    create_settings_mock = mocker.patch(
        "app.orchestrator.orchestrator.create_outlook_settings",
        return_value=settings,
    )

    connect_mock = mocker.patch(
        "app.orchestrator.orchestrator.connect_outlook",
        return_value=token,
    )
    mocker.patch(
        "app.orchestrator.orchestrator.graph_headers",
        return_value={},
    )

    mocker.patch(
        "app.orchestrator.orchestrator.search_folder",
        return_value={"id": "inbox-id"},
    )

    mocker.patch(
        "app.orchestrator.orchestrator.fetch_outlook_messages",
        return_value=[],
    )

    db = Session

    run_outlook_ingestion(
        db=db,
        application_id="app-id",
        client_secret="secret",
    )

    create_settings_mock.assert_called_once_with(
        application_id="app-id",
        client_secret="secret",
    )

    connect_mock.assert_called_once_with(settings)

def test_run_outlook_ingestion_fetches_inbox_messages(mocker, db):
    settings = mocker.Mock()
    access_token = "test-token"
    headers = {"Authorization": "Bearer test-token"}
    folder = {"id": "inbox-id"}
    messages = [
        {"id": "message-1"},
        {"id": "message-2"},
    ]

    mocker.patch(
        "app.orchestrator.orchestrator.create_outlook_settings",
        return_value=settings,
    )

    mocker.patch(
        "app.orchestrator.orchestrator.connect_outlook",
        return_value=access_token,
    )

    graph_headers_mock = mocker.patch(
        "app.orchestrator.orchestrator.graph_headers",
        return_value=headers,
    )

    search_folder_mock = mocker.patch(
        "app.orchestrator.orchestrator.search_folder",
        return_value=folder,
    )

    fetch_mock = mocker.patch(
        "app.orchestrator.orchestrator.fetch_outlook_messages",
        return_value=messages,
    )

    mocker.patch(
        "app.orchestrator.orchestrator.build_parsed_email",
        return_value=mocker.Mock(),
    )

    mocker.patch(
        "app.orchestrator.orchestrator.process_email",
    )

    run_outlook_ingestion(
        db=db,
        application_id="app-id",
        client_secret="secret",
    )

    graph_headers_mock.assert_called_once_with(access_token)

    search_folder_mock.assert_called_once_with(
        headers,
        "Inbox",
    )

    fetch_mock.assert_called_once_with(
        access_token,
        folder_id="inbox-id",
        top=50,
        max_results=200,
    )

def test_run_outlook_ingestion_parses_messages(mocker, db):
    settings = mocker.Mock()
    access_token = "test-token"
    headers = {"Authorization": "Bearer test-token"}
    folder = {"id": "inbox-id"}

    messages = [
        {"id": "message-1"},
        {"id": "message-2"},
    ]


    parsed_email_1 = mocker.Mock()
    parsed_email_2 = mocker.Mock()

    mocker.patch(
        "app.orchestrator.orchestrator.create_outlook_settings",
        return_value=settings,
    )

    mocker.patch(
        "app.orchestrator.orchestrator.connect_outlook",
        return_value=access_token,
    )

    mocker.patch(
        "app.orchestrator.orchestrator.graph_headers",
        return_value=headers,
    )

    mocker.patch(
        "app.orchestrator.orchestrator.search_folder",
        return_value=folder,
    )

    mocker.patch(
        "app.orchestrator.orchestrator.fetch_outlook_messages",
        return_value=messages,
    )

    build_parsed_email_mock = mocker.patch(
        "app.orchestrator.orchestrator.build_parsed_email",
        side_effect=[
            parsed_email_1,
            parsed_email_2,
        ],
    )

    mocker.patch(
        "app.orchestrator.orchestrator.process_email",
    )

    run_outlook_ingestion(
        db=db,
        application_id="app-id",
        client_secret="secret",
    )

    assert build_parsed_email_mock.call_count == 2

    build_parsed_email_mock.assert_any_call(
        messages[0],
        EmailProvider.OUTLOOK,
    )

    build_parsed_email_mock.assert_any_call(
        messages[1],
        EmailProvider.OUTLOOK,
    )

def test_run_outlook_ingestion_processes_parsed_emails(mocker, db):
    settings = mocker.Mock()
    access_token = "test-token"
    headers = {"Authorization": "Bearer test-token"}
    folder = {"id": "inbox-id"}

    messages = [
        {"id": "message-1"},
        {"id": "message-2"},
    ]

    parsed_email_1 = mocker.Mock()
    parsed_email_2 = mocker.Mock()

    mocker.patch(
        "app.orchestrator.orchestrator.create_outlook_settings",
        return_value=settings,
    )

    mocker.patch(
        "app.orchestrator.orchestrator.connect_outlook",
        return_value=access_token,
    )

    mocker.patch(
        "app.orchestrator.orchestrator.graph_headers",
        return_value=headers,
    )

    mocker.patch(
        "app.orchestrator.orchestrator.search_folder",
        return_value=folder,
    )

    mocker.patch(
        "app.orchestrator.orchestrator.fetch_outlook_messages",
        return_value=messages,
    )

    build_parsed_email_mock = mocker.patch(
        "app.orchestrator.orchestrator.build_parsed_email",
        side_effect=[
            parsed_email_1,
            parsed_email_2,
        ],
    )

    process_email_mock = mocker.patch(
        "app.orchestrator.orchestrator.process_email",
    )

    run_outlook_ingestion(
        db=db,
        application_id="app-id",
        client_secret="secret",
    )

    assert build_parsed_email_mock.call_count == 2
    assert process_email_mock.call_count == 2

    build_parsed_email_mock.assert_any_call(
        messages[0],
        EmailProvider.OUTLOOK,
    )

    build_parsed_email_mock.assert_any_call(
        messages[1],
        EmailProvider.OUTLOOK,
    )

    process_email_mock.assert_any_call(
        db=db,
        email=parsed_email_1,
        outlook_headers=headers,
        outlook_message_id="message-1",
    )

    process_email_mock.assert_any_call(
        db=db,
        email=parsed_email_2,
        outlook_headers=headers,
        outlook_message_id="message-2",
    )

def test_process_email_uses_linkedin_normalizer(mocker, db):
    email = mocker.Mock()
    email.sender = "jobalerts-noreply@linkedin.com"

    normalizer = mocker.Mock()
    normalizer.normalize.return_value = []

    mocker.patch.dict(
        JOB_BOARD_PARSERS,
        {"linkedin": normalizer},
    )

    process_email(db, email)

    normalizer.normalize.assert_called_once_with(email)

def test_process_email_ignores_unknown_sender_two(mocker, db):
    email = mocker.Mock()
    email.sender = "someone@example.com"

    normalizer = mocker.Mock()

    mocker.patch.dict(
        JOB_BOARD_PARSERS,
        {"linkedin": normalizer},
    )

    process_email(db, email)

    normalizer.normalize.assert_not_called()

def test_process_email_deletes_outlook_message_after_persistence(
    mocker,
    db,
):
    email = ParsedEmail(
        message_id="<123@example.com>",
        provider=EmailProvider.OUTLOOK,
        subject="Python Developer",
        sender="noreply@glassdoor.com",
        recipient="me@example.com",
        received_at=datetime.now(timezone.utc),
        text_body="",
        html_body="<html>...</html>",
    )

    normalizer = mocker.Mock()
    normalizer.normalize.return_value = [
        mocker.Mock()
    ]

    mocker.patch.dict(
        "app.orchestrator.orchestrator.JOB_BOARD_PARSERS",
        {"glassdoor": normalizer},
    )

    persist_mock = mocker.patch(
        "app.orchestrator.orchestrator.persist_normalized_jobs",
        return_value=[mocker.Mock()],
    )

    delete_mock = mocker.patch(
        "app.orchestrator.orchestrator.delete_email",
    )

    headers = {
        "Authorization": "Bearer test-token",
    }

    process_email(
        db,
        email,
        outlook_headers=headers,
        outlook_message_id="graph-message-123",
    )

    persist_mock.assert_called_once()
    delete_mock.assert_called_once_with(
        provider=EmailProvider.OUTLOOK,
        outlook_headers=headers,
        outlook_message_id="graph-message-123",
        imap_connection=None,
        imap_uid=None,
    )


@pytest.fixture
def icloud_connection():
    settings_obj = create_icloud_settings(
        username=settings.icloud_username,
        password=settings.icloud_password,
    )

    connection = connect_imap(settings_obj)

    yield connection

    try:
        connection.logout()
    except Exception:
        pass

def test_run_imap_ingestion_connects_to_imap(mocker):
    settings = mocker.Mock()
    connection = mocker.Mock()

    create_settings_mock = mocker.patch(
        "app.orchestrator.orchestrator.create_icloud_settings",
        return_value=settings,
    )

    connect_mock = mocker.patch(
        "app.orchestrator.orchestrator.connect_imap",
        return_value=connection,
    )

    search_mock = mocker.patch(
        "app.orchestrator.orchestrator.search_imap_messages",
        return_value=[],
    )

    db = Session

    run_imap_ingestion(
        db=db,
        username="imap_username",
        password="imap_password",
    )

    create_settings_mock.assert_called_once_with(
        username="imap_username",
        password="imap_password",
    )

    connect_mock.assert_called_once_with(settings)

    search_mock.assert_called_once_with(connection)

def test_run_imap_ingestion_fetches_each_uid(mocker, db):
    settings = mocker.Mock()
    connection = mocker.Mock()

    mocker.patch(
        "app.orchestrator.orchestrator.create_icloud_settings",
        return_value=settings,
    )

    mocker.patch(
        "app.orchestrator.orchestrator.connect_imap",
        return_value=connection,
    )

    search_mock = mocker.patch(
        "app.orchestrator.orchestrator.search_imap_messages",
        return_value=[b"101", b"102"],
    )

    fetch_mock = mocker.patch(
        "app.orchestrator.orchestrator.fetch_imap_message",
        side_effect=[
            b"raw email 1",
            b"raw email 2",
        ],
    )

    mocker.patch(
        "app.orchestrator.orchestrator.parse_email",
        return_value=None,
    )

    run_imap_ingestion(
        db=db,
        username="imap_username",
        password="imap_password",
    )

    search_mock.assert_called_once_with(connection)

    assert fetch_mock.call_count == 2

    fetch_mock.assert_any_call(
        connection,
        b"101",
    )

    fetch_mock.assert_any_call(
        connection,
        b"102",
    )

def test_run_imap_ingestion_parses_each_message(mocker, db):
    settings = mocker.Mock()
    connection = mocker.Mock()

    mocker.patch(
        "app.orchestrator.orchestrator.create_icloud_settings",
        return_value=settings,
    )

    mocker.patch(
        "app.orchestrator.orchestrator.connect_imap",
        return_value=connection,
    )

    mocker.patch(
        "app.orchestrator.orchestrator.search_imap_messages",
        return_value=[b"101", b"102"],
    )

    mocker.patch(
        "app.orchestrator.orchestrator.fetch_imap_message",
        side_effect=[
            b"raw email 1",
            b"raw email 2",
        ],
    )

    parsed_email_1 = mocker.Mock()
    parsed_email_2 = mocker.Mock()

    parse_mock = mocker.patch(
        "app.orchestrator.orchestrator.parse_email",
        side_effect=[
            parsed_email_1,
            parsed_email_2,
        ],
    )

    process_mock = mocker.patch(
        "app.orchestrator.orchestrator.process_email",
    )

    run_imap_ingestion(
        db=db,
        username="imap_username",
        password="imap_password",
    )

    assert parse_mock.call_count == 2

    parse_mock.assert_any_call(
        b"raw email 1",
        EmailProvider.ICLOUD,
    )

    parse_mock.assert_any_call(
        b"raw email 2",
        EmailProvider.ICLOUD,
    )

def test_process_email_ignores_unknown_sender_three(mocker, db):
    email = mocker.Mock()
    email.sender = "someone@example.com"

    identify_mock = mocker.patch(
        "app.orchestrator.orchestrator.identify_job_board",
        return_value=None,
    )

    normalize_mock = mocker.patch(
        "app.orchestrator.orchestrator.persist_normalized_jobs",
    )

    delete_mock = mocker.patch(
        "app.orchestrator.orchestrator.delete_email",
    )

    process_email(
        db=db,
        email=email,
    )

    identify_mock.assert_called_once_with(
        email.sender,
    )

    normalize_mock.assert_not_called()
    delete_mock.assert_not_called()

def test_process_email_does_not_persist_when_no_jobs(mocker, db):

    email = mocker.Mock()
    email.sender = "noreply@glassdoor.com"

    normalizer = mocker.Mock()
    normalizer.normalize.return_value = []

    mocker.patch(
        "app.orchestrator.orchestrator.identify_job_board",
        return_value="glassdoor",
    )

    mocker.patch.dict(
        "app.orchestrator.orchestrator.JOB_BOARD_PARSERS",
        {
            "glassdoor": normalizer,
        },
    )

    persist_mock = mocker.patch(
        "app.orchestrator.orchestrator.persist_normalized_jobs",
    )

    delete_mock = mocker.patch(
        "app.orchestrator.orchestrator.delete_email",
    )

    process_email(
        db=db,
        email=email,
    )

    normalizer.normalize.assert_called_once_with(email)
    persist_mock.assert_not_called()
    delete_mock.assert_not_called()

def test_process_email_persists_normalized_jobs(mocker, db):
    email = mocker.Mock()
    email.sender = "noreply@glassdoor.com"

    normalizer = mocker.Mock()

    normalized_jobs = [
        mocker.Mock(),
        mocker.Mock(),
    ]

    normalizer.normalize.return_value = normalized_jobs

    mocker.patch(
        "app.orchestrator.orchestrator.identify_job_board",
        return_value="glassdoor",
    )

    mocker.patch.dict(
        "app.orchestrator.orchestrator.JOB_BOARD_PARSERS",
        {
            "glassdoor": normalizer,
        },
    )

    persist_mock = mocker.patch(
        "app.orchestrator.orchestrator.persist_normalized_jobs",
        return_value=[mocker.Mock()],
    )

    delete_mock = mocker.patch(
        "app.orchestrator.orchestrator.delete_email",
    )

    process_email(
        db=db,
        email=email,
    )

    persist_mock.assert_called_once_with(
        db,
        normalized_jobs,
    )

def test_process_email_deletes_email_after_successful_persistence(
    mocker,
    db,
):
    email = mocker.Mock()
    email.sender = "noreply@glassdoor.com"
    email.provider = EmailProvider.OUTLOOK

    normalizer = mocker.Mock()

    normalized_jobs = [
        mocker.Mock(),
    ]

    created_jobs = [
        mocker.Mock(),
    ]

    normalizer.normalize.return_value = normalized_jobs

    mocker.patch(
        "app.orchestrator.orchestrator.identify_job_board",
        return_value="glassdoor",
    )

    mocker.patch.dict(
        "app.orchestrator.orchestrator.JOB_BOARD_PARSERS",
        {
            "glassdoor": normalizer,
        },
    )

    mocker.patch(
        "app.orchestrator.orchestrator.persist_normalized_jobs",
        return_value=created_jobs,
    )

    delete_mock = mocker.patch(
        "app.orchestrator.orchestrator.delete_email",
    )

    headers = {
        "Authorization": "Bearer test-token",
    }

    process_email(
        db=db,
        email=email,
        outlook_headers=headers,
        outlook_message_id="message-123",
    )

    delete_mock.assert_called_once_with(
        provider=EmailProvider.OUTLOOK,
        outlook_headers=headers,
        outlook_message_id="message-123",
        imap_connection=None,
        imap_uid=None,
    )


def test_process_email_does_not_delete_when_persistence_creates_no_jobs(
    mocker,
    db,
):
    email = mocker.Mock()
    email.sender = "noreply@glassdoor.com"

    normalizer = mocker.Mock()
    normalizer.normalize.return_value = [mocker.Mock()]

    mocker.patch(
        "app.orchestrator.orchestrator.identify_job_board",
        return_value="glassdoor",
    )

    mocker.patch.dict(
        "app.orchestrator.orchestrator.JOB_BOARD_PARSERS",
        {
            "glassdoor": normalizer,
        },
    )

    mocker.patch(
        "app.orchestrator.orchestrator.persist_normalized_jobs",
        return_value=[],
    )

    delete_mock = mocker.patch(
        "app.orchestrator.orchestrator.delete_email",
    )

    process_email(
        db=db,
        email=email,
    )

    delete_mock.assert_not_called()


def test_run_mail_ingestion_runs_both_providers(mocker, db):
    outlook_mock = mocker.patch(
        "app.orchestrator.orchestrator.run_outlook_ingestion",
    )

    imap_mock = mocker.patch(
        "app.orchestrator.orchestrator.run_imap_ingestion",
    )

    run_mail_ingestion(
        db=db,
        outlook_application_id="outlook-app-id",
        outlook_client_secret="outlook-secret",
        icloud_username="icloud-user",
        icloud_password="icloud-password",
    )

    outlook_mock.assert_called_once_with(
        db=db,
        application_id="outlook-app-id",
        client_secret="outlook-secret",
    )

    imap_mock.assert_called_once_with(
        db=db,
        username="icloud-user",
        password="icloud-password",
    )