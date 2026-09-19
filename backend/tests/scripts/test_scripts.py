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

from app.orchestrator.orchestrator import run_mail_ingestion

def test_run_mail_ingestion_continues_if_outlook_fails(mocker, db):
    outlook_mock = mocker.patch(
        "app.orchestrator.orchestrator.run_outlook_ingestion",
        side_effect=Exception("Outlook failed"),
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

    outlook_mock.assert_called_once()

    imap_mock.assert_called_once_with(
        db=db,
        username="icloud-user",
        password="icloud-password",
    )