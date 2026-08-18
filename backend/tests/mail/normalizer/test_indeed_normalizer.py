import pytest
from pathlib import Path
from datetime import datetime, timezone
from app.core.config import settings

from app.mail.normalizer.glassdoor import (
    extract_glassdoor_jobs,
    identify_job_board)

from app.mail.normalizer.indeed import extract_indeed_jobs
from app.mail.mail_services.mime_parser import build_parsed_email
from app.mail.mail_services.detector import detect_job_email
from app.mail.connectors.imap_connector import (
    connect_imap, 
    fetch_message, 
    search_messages, 
    fetch_imap_messages)

from app.mail.models import EmailProvider
from app.mail.normalizer.indeed import IndeedNormalizer
from app.mail.normalizer.base import ParsedEmail

from app.mail.mail_services.parser import parse_email
from app.mail.providers.icloud import create_icloud_settings


FIXTURES = Path(__file__).parent / "fixtures" / "emails"


# Fixture generation helper
#
# Uncomment when a new real email needs to be captured for testing.
# This intentionally uses a live iCloud connection and should not
# be part of the normal test suite.
# @pytest.fixture
# def icloud_connection():
#     settings_obj = create_icloud_settings(
#         username=settings.icloud_username,
#         password=settings.icloud_password,
#     )

#     connection = connect_imap(settings_obj)

#     yield connection

#     try:
#         connection.logout()
#     except Exception:
#         pass


# def test_to_get_raw_email_data(icloud_connection):
#     ids = search_messages(icloud_connection)
#     # print('ids:',ids)
    
#     # Remembe to run first and get Id for target email and update id (b'2351') """
#     raw_email = fetch_message(icloud_connection, b'2356') #b'1'
#     # print('DEBUG raw_email:', raw_email)
#     with open(
#         "/Users/paulblack/VS Code/ai-recruiting-assistant/backend/tests/mail/normalizer/fixtures/emails/mutliple_indeed_jobs.eml", "wb") as f:
#         f.write(raw_email)



def load_email_fixture(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


def test_indeed_email():
    raw_email = load_email_fixture("multiple_indeed_jobs.eml")

    parsed = build_parsed_email(raw_email, EmailProvider.ICLOUD)
    # print('parsed:', parsed)

    assert parsed.html_body is not None
    assert parsed.sender == "donotreply@match.indeed.com"
    assert parsed.subject == "Software Engineer at HackerEarth in Remote and 3 more new jobs"
    

def test_indeed_normalizer():
    raw_email = load_email_fixture(
        "multiple_indeed_jobs.eml"
    )

    

    parsed = build_parsed_email(
        raw_email,
        EmailProvider.ICLOUD,
    )

    normalizer = IndeedNormalizer()

    jobs = normalizer.normalize(parsed)

    print('jobs:', jobs[0])
    print('len(jobs):', len(jobs))

    assert len(jobs) == 4
    assert jobs[0].title == "Software Engineer"
    assert jobs[0].company == "HackerEarth"
    assert jobs[0].location == "Remote"
    assert jobs[0].salary == None
    assert jobs[0].job_url.startswith("https://www.indeed.com/pagead/")


def test_indeed_normalizer_extracts_unique_urls():
    raw_email = load_email_fixture(
        "zip_recruiter_multiple_jobs.eml"
    )

    parsed = build_parsed_email(
        raw_email,
        EmailProvider.ICLOUD,
    )

    jobs = IndeedNormalizer().normalize(parsed)

    urls = [job.job_url for job in jobs]

    assert len(urls) == len(set(urls))


def test_glassdoor_non_job_email():
    raw_email = load_email_fixture(
        "indeed_non_job.eml"
    )

    parsed = build_parsed_email(
        raw_email,
        EmailProvider.ICLOUD,
    )

    jobs = IndeedNormalizer().normalize(parsed)

    assert jobs == []


def test_zip_recruiter_without_html_returns_no_jobs():
    parsed = ParsedEmail(
        message_id="test-message",
        provider=EmailProvider.ICLOUD,
        subject="ZipRecruiter alert",
        sender="alerts@ziprecruiter.com",
        recipient="test@example.com",
        received_at=datetime.now(timezone.utc),
        text_body="Some text",
        html_body=None,
    )

    jobs = IndeedNormalizer().normalize(parsed)

    assert jobs == []