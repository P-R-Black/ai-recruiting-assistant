import pytest

from datetime import datetime, timezone

from app.mail.normalizer.base import ParsedEmail
from app.mail.models import EmailProvider

from app.mail.filters.job_board_filter import (
    is_job_board_email, 
    identify_job_board
    )


def test_is_job_board_email_accepts_glassdoor():
    email = ParsedEmail(
        message_id="<123@example.com>",
        provider=EmailProvider.ICLOUD,
        subject="New jobs for you",
        sender="noreply@glassdoor.com",
        recipient="me@example.com",
        received_at=datetime.now(timezone.utc),
        text_body="",
        html_body=""
    )

    assert is_job_board_email(email) is True


def test_is_job_board_email_accepts_altered_glassdoor():
    email = ParsedEmail(
        message_id="<123@example.com>",
        provider=EmailProvider.ICLOUD,
        subject="New jobs for you",
        sender="Glassdoor Jobs <noreply@glassdoor.com>",
        recipient="me@example.com",
        received_at=datetime.now(timezone.utc),
        text_body="",
        html_body=""
    )

    assert is_job_board_email(email) is True


def test_linkedin_notification_senders_are_excluded():
    non_job_senders = [
        "notifications-noreply@linkedin.com",
        "messages-noreply@linkedin.com",
        "updates-noreply@linkedin.com",
        "editors-noreply@linkedin.com",
    ]
    for sender in non_job_senders:
        assert identify_job_board(sender) is None


def test_linkedin_job_senders_are_included():
    job_senders = [
        "jobalerts-noreply@linkedin.com",
        "jobs-noreply@linkedin.com",
    ]
    for sender in job_senders:
        assert identify_job_board(sender) == "linkedin"


def test_identify_job_board_handles_display_name():
    assert (
        identify_job_board("Glassdoor Jobs <noreply@glassdoor.com>")
        == "glassdoor"
    )

def test_identify_job_board_is_case_insensitive():
    assert (
        identify_job_board("NOREPLY@GLASSDOOR.COM")
        == "glassdoor"
    )


def test_identify_job_board_returns_none_for_unknown_sender():
    assert identify_job_board("someone@example.com") is None


def test_identify_job_board_returns_none_for_empty_sender():
    assert identify_job_board(None) is None


"""
Run individual tests
uv run pytest tests/test_jobs_api.py
make test TEST=tests/test_jobs_api.py
uv run pytest -s (to show print statements for passing tests)
uv run pytest -s tests/test_jobs_api.py (to show print statements for passing tests)
uv run pytest tests/mail/normalizer/test_glassdoor_normalizer.py::test_normalizer_stuff (to run specific test)
"""
