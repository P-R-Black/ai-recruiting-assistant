
from app.mail.models import EmailProvider, EmploymentType
from app.mail.schemas import EmailCreate
from app.mail.mail_services.service import WorkLocation, ExtractJob
from app.jobs.models import JobSource

from app.mail.mappers.job_email import build_job_create


def test_build_job_create():
    extracted = ExtractJob(
        title="Junior Frontend Developer",
        company="OpenAI",
        location="Orlando, FL",
        salary="$180,000 - $220,000",
        apply_url="https://jobs.openai.com/12345",
        employment_type=EmploymentType.FULL_TIME,
        recruiter="Jane Smith",
        work_location=WorkLocation.REMOTE,
    )

    fingerprint = "a" * 64

    result = build_job_create(
        extracted,
        fingerprint=fingerprint,
        description="Junior Frontend Developer position...",
        source=JobSource.MAIL,
    )

    assert result.title == "Junior Frontend Developer"
    assert result.company == "OpenAI"
    assert result.location == "Orlando, FL"
    assert result.salary_min == 180000
    assert result.salary_max == 220000
    assert result.salary_currency == "USD"
    assert str(result.job_url )== "https://jobs.openai.com/12345"
    assert result.employment_type == EmploymentType.FULL_TIME
    assert result.work_location == WorkLocation.REMOTE
    assert result.recruiter_name == "Jane Smith"
    assert result.description == "Junior Frontend Developer position..."
    assert result.source == JobSource.MAIL
    assert result.fingerprint == fingerprint
