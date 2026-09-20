import pytest
from pathlib import Path

from datetime import datetime, timezone
from app.core.config import settings


from app.mail.mail_services.parsers.mime_parser import build_parsed_email
from app.mail.mail_services.detectors.detector import detect_job_email
from app.mail.connectors.imap_connector import connect_imap


from app.mail.providers.icloud import (
    fetch_imap_message, 
    search_imap_messages, 
    fetch_imap_messages)

from app.mail.models import EmailProvider

from app.mail.normalizer.linkedin import LinkedInNormalizer
from app.mail.normalizer.base import ParsedEmail
from email.message import EmailMessage

from contextlib import contextmanager

from app.mail.mail_services.parsers.graph_parser import build_parsed_email_from_graph_message


from app.mail.connectors.outlook_connector import create_outlook_settings
from app.mail.providers.outlook import (
    connect_outlook, 
    fetch_outlook_messages,
    graph_headers,
    normalize_outlook_message,
    search_folder,
    MissingRefreshTokenError
)


FIXTURES = Path(__file__).parent / "fixtures" / "emails"

def load_email_fixture(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()



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

    

def test_linkedin_job_no_reply_email():
    raw_email = load_email_fixture("linkedin_multiple_jobs_0.eml")

    parsed = build_parsed_email(raw_email, EmailProvider.OUTLOOK)

    assert parsed.html_body is not None
    assert parsed.sender == "jobs-noreply@linkedin.com"
    assert parsed.subject == "HiredBuddy is hiring for a Web role"


def test_linkedin_job_alert_email():
    raw_email = load_email_fixture("linkedin_multiple_jobs_1.eml")

    parsed = build_parsed_email(raw_email, EmailProvider.OUTLOOK)

    assert parsed.html_body is not None
    assert parsed.sender == "jobalerts-noreply@linkedin.com"
    assert parsed.subject == "Full Stack Engineer - Junior at Breeze"


def test_linkedin_normalizer_no_reply():
    raw_email = load_email_fixture(
        "linkedin_multiple_jobs_0.eml"
    )

    parsed = build_parsed_email(
        raw_email,
        EmailProvider.OUTLOOK,
    )

    normalizer = LinkedInNormalizer()

    jobs = normalizer.normalize(parsed)

    assert len(jobs) == 6
    assert jobs[0].title == "Web Developer"
    assert jobs[0].location == "San Francisco, CA (Remote)"
    assert jobs[0].salary == None
    assert jobs[0].job_url.startswith("https://www.linkedin.com/")


def test_linkedin_normalizer_job_alert():
    raw_email = load_email_fixture(
        "linkedin_multiple_jobs_1.eml"
    )

    parsed = build_parsed_email(
        raw_email,
        EmailProvider.OUTLOOK,
    )

    normalizer = LinkedInNormalizer()

    jobs = normalizer.normalize(parsed)

    assert len(jobs) == 6
    assert jobs[0].title == "Full Stack Engineer - Junior"
    assert jobs[0].location == "New York, NY"
    assert jobs[0].salary == None
    assert jobs[0].job_url.startswith("https://www.linkedin.com/")



def test_linkedin_normalizer_extracts_unique_urls():
    raw_email = load_email_fixture(
        "linkedin_multiple_jobs_1.eml"
    )

    parsed = build_parsed_email(
        raw_email,
        EmailProvider.OUTLOOK,
    )

    jobs = LinkedInNormalizer().normalize(parsed)
    urls = [job.job_url for job in jobs]
   
    assert len(urls) == len(set(urls))


def test_linkedin_non_job_email():
    raw_email = load_email_fixture(
        "linkedin_multiple_jobs.eml"
    )

    parsed = build_parsed_email(
        raw_email,
        EmailProvider.OUTLOOK,
    )

    jobs = LinkedInNormalizer().normalize(parsed)

    assert jobs == []
       




"""
Run individual tests
uv run pytest tests/test_jobs_api.py
make test TEST=tests/test_jobs_api.py
uv run pytest -s (to show print statements for passing tests)
uv run pytest -s tests/test_jobs_api.py (to show print statements for passing tests)
uv run pytest tests/mail/normalizer/test_glassdoor_normalizer.py::test_normalizer_stuff (to run specific test)
"""

"""
To get .eml file from linkedin email
"""
# def graph_message_to_eml(message: dict) -> bytes:
#     from_address = (
#         message.get("from", {})
#         .get("emailAddress", {})
#         .get("address", "")
#     )

#     to_recipients = message.get("toRecipients", [])
#     to_address = (
#         to_recipients[0]
#         .get("emailAddress", {})
#         .get("address", "")
#         if to_recipients
#         else ""
#     )

#     body = message.get("body", {})
#     content_type = (body.get("contentType") or "").lower()
#     content = body.get("content", "")

#     msg = EmailMessage()

#     msg["From"] = from_address
#     msg["To"] = to_address
#     msg["Subject"] = message.get("subject") or ""

#     if message.get("receivedDateTime"):
#         msg["Date"] = message["receivedDateTime"]

#     if message.get("internetMessageId"):
#         msg["Message-ID"] = message["internetMessageId"]

#     if content_type == "html":
#         msg.set_content("This email contains an HTML body.")
#         msg.add_alternative(content, subtype="html")
#     else:
#         msg.set_content(content)

#     return msg.as_bytes()


# def create_linkedin_eml_file(outlook_token):

#     headers = graph_headers(outlook_token)
#     folder_name = 'Inbox'
#     target_folder = search_folder(headers, folder_name)
#     folder_id = target_folder['id']

#     messages = fetch_outlook_messages(outlook_token, folder_id=folder_id, top=2, max_results=2)
#     # print('messages:', messages)


#     for i, messages in enumerate(messages):
#         eml_bytes = graph_message_to_eml(messages)
#         with open(
#             f"/Users/paulblack/VS Code/ai-recruiting-assistant/"
#             f"backend/tests/mail/normalizer/fixtures/emails/"
#             f"linkedin_multiple_jobs_{i}.eml",
#             "wb",
#         ) as f:
#             f.write(eml_bytes)