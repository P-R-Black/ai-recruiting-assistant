from datetime import datetime, timezone

from email.message import EmailMessage
from app.mail.schemas import EmailCreate, EmailProvider
from app.mail.models import EmailProvider

from app.mail.extractor import (
    extract_apply_url, extract_company_name, extract_job_information, extract_job_title,
    extract_location, extract_salary
    )


def test_extract_job_information():
  
    email = sample_job_email()
    result = extract_job_information(email)

    assert result.title == "Junior Frontend Developer"
    assert result.company == "OpenAI"
    assert result.location == "Orlando, FL"
    assert result.salary == "Salary: $180,000 - $220,000"
    assert result.apply_url == "https://jobs.openai.com/12345"



def test_extract_job_information_without_salary():
    email = EmailCreate(
        provider=EmailProvider.APPLE,
        message_id="<123@example.com>",
        subject="Frontend Developer",
        sender="Recruiter <talent@google.com>",
        recipient="paul@example.com",
        received_at=datetime.now(timezone.utc),
        raw_body="""
            Frontend Developer

            Google

            Remote

            Apply here:
            https://careers.google.com/job/123
            """,
        
    )

    result = extract_job_information(email)

    assert result.title == "Frontend Developer"
    assert result.company == "Google"
    assert result.location == "Remote"
    assert result.salary is None
    assert result.apply_url == "https://careers.google.com/job/123"


def test_extract_job_information_minimal():
    email = EmailCreate(
        provider=EmailProvider.APPLE,
        message_id="<123@example.com>",
        subject="Software Engineer",
        sender="jobs@company.com",
        recipient="paul@example.com",
        received_at=datetime.now(timezone.utc),
        raw_body="""
            Software Engineer

            Apply:
            https://company.com/jobs/1
            """,
    )

    result = extract_job_information(email)

    assert result.title == "Software Engineer"
    assert result.company is None
    assert result.location is None
    assert result.salary is None
    assert result.apply_url == "https://company.com/jobs/1"


def test_extract_job_title():
    email = sample_job_email()

    searchable = " ".join([
        email.subject,
        email.raw_body,
    ])

    result = extract_job_title(searchable)

    assert result.value == "Junior Frontend Developer"
    assert result.line_index == 0
    assert result.confidence == 1.0


def test_extract_location():
    email = sample_job_email()

    searchable = " ".join([
        email.subject,
        email.raw_body,
    ])

    title = extract_job_title(searchable)
    company = extract_company_name(searchable, title)
    result = extract_location(searchable, company)

    assert result.value == "Orlando, FL"
    assert result.line_index == 2
    assert result.confidence == 1.0


def test_extract_salary():
    email = sample_job_email()

    searchable = " ".join([
        email.subject,
        email.raw_body,
    ])

    title = extract_job_title(searchable)
    company = extract_company_name(searchable, title)
    location = extract_location(searchable, company)
    result = extract_salary(searchable, location)

    assert result.value == "Salary: $180,000 - $220,000"
    assert result.line_index == 3
    assert result.confidence == 1.0


def test_extract_company_name():
    email = sample_job_email()

    searchable = " ".join([
        email.subject,
        email.raw_body,
    ])

    title = extract_job_title(searchable)
    result = extract_company_name(searchable, title)

    assert result.value == "OpenAI"
    assert result.line_index == 1
    assert result.confidence == 1.0


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

def test_extract_apply_url():
    email = sample_job_email()

    result = extract_apply_url(email)

    assert result == "https://jobs.openai.com/12345"


"""
Run individual tests
uv run pytest tests/test_jobs_api.py
make test TEST=tests/test_jobs_api.py
uv run pytest -s (to show print statements for passing tests)
uv run pytest -s tests/test_jobs_api.py (to show print statements for passing tests)
uv run pytest tests/test_mail_service.py::test_detect_job_email_true (to run specific test)
"""