import pytest
from datetime import datetime, timezone

from pathlib import Path
from app.core.config import settings

from app.mail.mail_services.mime_parser import build_parsed_email
from app.mail.models import EmailProvider, EmploymentType
from app.mail.schemas import EmailCreate
from app.mail.mail_services.service import WorkLocation, ExtractJob
from app.jobs.models import JobSource

from app.mail.normalizer.glassdoor import GlassdoorNormalizer

from app.jobs.mappers.job_email import build_job_create, build_job_create_from_normalized
from app.mail.mappers.job_email import build_email_create_from_normalized
from app.mail.normalizer.base import NormalizedJob

from tests.mail.normalizer.test_glassdoor_normalizer import load_email_fixture
from app.jobs.classifiers.role import classify_job, JobClassification, JobRoleType, ResumeRecommendation



@pytest.mark.integration
@pytest.mark.skipif(
    settings.icloud_username is None,
    reason="iCloud credentials not configured",
)
def test_build_email_create_from_normalized():
    raw_email = load_email_fixture(
            "glassdoor_multiple_jobs.eml"
        )
    
    parsed = build_parsed_email(
        raw_email,
        EmailProvider.ICLOUD,
    )

    jobs = GlassdoorNormalizer().normalize(parsed)
    select_job = jobs[0]
    result = build_email_create_from_normalized(select_job)


    assert result.provider == EmailProvider.ICLOUD
    assert result.message_id == "5KLZLo1zRzSlKBfX41ea-w@geopod-ismtpd-44"
    assert result.subject == "Business Developer at Al's Complete Lawn Care and 11 more jobs in United States of America for you. Apply Now."
    assert result.sender == "noreply@glassdoor.com"
    assert result.recipient.endswith("@me.com")
    assert result.received_at == datetime(2026, 8, 17, 1, 20, 44, tzinfo=timezone.utc)
    assert result.raw_body == ""



def test_build_job_create_from_normalized():
    raw_email = load_email_fixture(
        "glassdoor_multiple_jobs.eml"
    )
        
    parsed = build_parsed_email(
        raw_email,
        EmailProvider.ICLOUD,
    )

    jobs = GlassdoorNormalizer().normalize(parsed)
    select_job = jobs[0]

    fingerprint = "a" * 64

    classification = classify_job(select_job)

    result = build_job_create_from_normalized(
        normalized=select_job, 
        fingerprint=fingerprint, 
        source=JobSource.MAIL,
        classification=classification)
    
    

    assert result.title == "IT Business Systems Developer"
    assert result.company == "WITTENSTEIN"
    assert result.location == "United States"

    assert result.employment_type is None
    assert result.work_location is None
    assert result.recruiter_name is None

    assert result.salary_min == 70
    assert result.salary_max == 90
    assert result.salary_currency == "USD"

    assert result.description == "N/A"
    
    assert str(result.job_url).startswith("https://www.glassdoor.com/partner")
    assert result.source == JobSource.MAIL
    assert result.fingerprint == "a" * 64

    assert result.is_relevant == False
    assert result.role_type == JobRoleType.UNKNOWN
    assert result.recommended_resume == ResumeRecommendation.UNKNOWN



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
