import pytest

from datetime import datetime, timezone

from app.mail.mail_services.extractor import (
    extract_apply_url,
    extract_company_name,
    extract_job_information,
    extract_job_title,
    extract_location,
    extract_salary,
    extract_work_location,
    extract_employment_type,
    extract_recruiter_name,
    extract_company_website,
    extract_application_url,
    
)

from app.mail.models import EmailProvider, EmploymentType
from app.mail.schemas import EmailCreate
from app.mail.mail_services.service import WorkLocation
from app.mail.mail_services.service import parse_salary

from tests.conftest import (
    sample_job_email_complete, 
    sample_job_email_multi_emails,
    sample_job_email_no_emails)


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


def sample_job_email_two() -> EmailCreate:
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

            Remote

            Salary: $180,000 - $220,000

            Apply here:
            https://jobs.openai.com/12345
            """,
                )

def sample_job_email_full_time() -> EmailCreate:
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

            Remote

            Full-time

            Salary: $180,000 - $220,000

            Apply here:
            https://jobs.openai.com/12345
            """,
                )



def sample_job_email_contractor() -> EmailCreate:
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

            Remote

            Contractor

            Salary: $180,000 - $220,000

            Apply here:
            https://jobs.openai.com/12345
            """,
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
    assert result.confidence == pytest.approx(1.0)


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


def test_salary_parser():
    email = sample_job_email()
    
    searchable = " ".join([
            email.subject,
            email.raw_body,
        ])
    
    title = extract_job_title(searchable)
    company = extract_company_name(searchable, title)
    location = extract_location(searchable, company)
    result = extract_salary(searchable, location)
    salary_range = parse_salary(result.value)

    assert salary_range.salary_min == 180000
    assert salary_range.salary_max == 220000
    assert salary_range.currency == 'USD'



def test_parse_single_salary():
    result = parse_salary("Salary: $180,000")

    assert result.salary_min == 180000
    assert result.salary_max is None
    assert result.currency == "USD"


def test_parse_euro_salary():
    result = parse_salary("€80,000 - €100,000")

    assert result.salary_min == 80000
    assert result.salary_max == 100000
    assert result.currency == "EUR"


def test_parse_pound_salary():
    result = parse_salary("£60,000")

    assert result.salary_min == 60000
    assert result.salary_max is None
    assert result.currency == "GBP"


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


def test_extract_apply_url():
    email = sample_job_email()

    result = extract_apply_url(email)

    assert result == "https://jobs.openai.com/12345"



def test_extract_work_location():
    email = sample_job_email_two()
    
    searchable = " ".join([
        email.subject,
        email.raw_body,
    ])

    result = extract_work_location(searchable)

    assert result.value == WorkLocation.REMOTE
    assert result.confidence == pytest.approx(1.0)
    assert result.line_index == 3


def test_extract_work_location_search_unknown():
    email = sample_job_email()
    
    searchable = " ".join([
        email.subject,
        email.raw_body,
    ])

    result = extract_work_location(searchable)

    assert result.value == WorkLocation.UNKNOWN
    assert result.confidence == pytest.approx(0.0)
    assert result.line_index == None


def test_extract_work_location_remote():
    result = extract_work_location(
        "This position is fully remote."
    )

    assert result.value == WorkLocation.REMOTE
    assert result.confidence == pytest.approx(1.0)


def test_extract_work_location_hybrid():
    result = extract_work_location(
        "This is a hybrid position."
    )

    assert result.value == WorkLocation.HYBRID


def test_extract_work_location_onsite():
    result = extract_work_location(
        "This role is onsite."
    )

    assert result.value == WorkLocation.ONSITE


def test_extract_work_location_unknown():
    result = extract_work_location(
        "Junior Frontend Developer"
    )

    assert result.value == WorkLocation.UNKNOWN
    assert result.confidence == pytest.approx(0.0)



def test_extract_employment_type():
    email = sample_job_email_full_time()
    
    searchable = " ".join([
        email.subject,
        email.raw_body,
    ])

    result = extract_employment_type(searchable)

    assert result.value == EmploymentType.FULL_TIME
    assert result.confidence == pytest.approx(1.0)


def test_extract_employment_type_contractor():
    email = sample_job_email_contractor()
    
    searchable = " ".join([
        email.subject,
        email.raw_body,
    ])

    result = extract_employment_type(searchable)

    assert result.value == EmploymentType.CONTRACT
    assert result.confidence == pytest.approx(1.0)


def test_extract_employment_type_unknown():
    email = sample_job_email()
    
    searchable = " ".join([
        email.subject,
        email.raw_body,
    ])

    result = extract_employment_type(searchable)

    assert result.value == EmploymentType.UNKNOWN
    assert result.confidence == pytest.approx(0.0)




def test_extract_recruiter_name():
    email = sample_job_email_complete()
        
    searchable = " ".join([
        email.subject,
        email.raw_body,
    ])

    result = extract_recruiter_name(searchable)

    assert result.value == 'Jane Smith'
    assert result.confidence == pytest.approx(1.0)
    assert result.line_index == 7



def test_extract_company_website():
    email = sample_job_email_complete()
            
    searchable = " ".join([
        email.subject,
        email.raw_body,
    ])


    title = extract_job_title(searchable)
    company = extract_company_name(searchable, title)
    apply_url = extract_apply_url(email)
    result = extract_company_website(company.value, apply_url)

    assert result.value == "openai.com"
    assert result.confidence == pytest.approx(0.95)


def test_extract_application_single_url():
    email = sample_job_email()
    
    result = extract_application_url(email)
    
    assert result.value == "https://jobs.openai.com/12345"

 
def test_extract_application_url():
    email = sample_job_email_multi_emails()
    
    result = extract_application_url(email)
    
    assert result.value == "https://careers.google.com/12345"



def test_extract_application_no_urls():
    email = sample_job_email_no_emails()
    result = extract_application_url(email)
        
    assert result.value == None

"""
Run individual tests
uv run pytest tests/test_jobs_api.py
make test TEST=tests/test_jobs_api.py
uv run pytest -s (to show print statements for passing tests)
uv run pytest -s tests/test_jobs_api.py (to show print statements for passing tests)
uv run pytest tests/test_extractor_service.py::test_extract_job_information (to run specific test)
"""