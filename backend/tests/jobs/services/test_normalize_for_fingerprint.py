from app.jobs.jobs_services.deduplication import (
    normalize_for_fingerprint, 
    calculate_job_fingerprint,
    calculate_normalized_job_fingerprint)

from app.mail.models import EmploymentType, WorkLocation
from app.mail.mail_services.service import ExtractJob

def test_normalize_for_fingerprint():
    assert normalize_for_fingerprint("OpenAI") == "openai"
    assert normalize_for_fingerprint("  OpenAI  ") == "openai"
    assert normalize_for_fingerprint("Full   Stack   Developer") == "full stack developer"
    assert normalize_for_fingerprint("\nReact\tDeveloper\n") == "react developer"
    assert normalize_for_fingerprint(None) == ""
    assert normalize_for_fingerprint("") == ""


def test_same_job_produces_same_fingerprint():
    job1 = ExtractJob(
        title="Full Stack Developer Java & React",
        company="Citi",
        location="Durham, NH",
        salary="$80K - $100K",
        apply_url="https://www.glassdoor.com/job-listing/123",
        employment_type=EmploymentType.FULL_TIME,
        work_location=WorkLocation.HYBRID,
    )

    job2 = ExtractJob(
        title="  FULL STACK DEVELOPER JAVA & REACT  ",
        company="  CITI  ",
        location="Durham,   NH",
        salary="$85K - $105K",
        apply_url="https://www.indeed.com/viewjob?jk=456",
        employment_type=EmploymentType.FULL_TIME,
        work_location=WorkLocation.HYBRID,
    )

    assert calculate_job_fingerprint(job1) == calculate_job_fingerprint(job2)


def test_different_company_produces_different_fingerprint():
    job1 = ExtractJob(
        title="React Developer",
        company="Citi",
        location="Durham, NH",
        salary=None,
        apply_url="https://example.com/1",
        employment_type=EmploymentType.FULL_TIME,
        work_location=WorkLocation.HYBRID,
    )

    job2 = ExtractJob(
        title="React Developer",
        company="OpenAI",
        location="Durham, NH",
        salary=None,
        apply_url="https://example.com/2",
        employment_type=EmploymentType.FULL_TIME,
        work_location=WorkLocation.HYBRID,
    )

    assert calculate_job_fingerprint(job1) != calculate_job_fingerprint(job2)


def test_different_title_produces_different_fingerprint():
    job1 = ExtractJob(
        title="React Developer",
        company="Citi",
        location="Durham, NH",
        salary=None,
        apply_url="https://example.com/1",
        employment_type=EmploymentType.FULL_TIME,
        work_location=WorkLocation.HYBRID,
    )

    job2 = ExtractJob(
        title="Senior React Developer",
        company="Citi",
        location="Durham, NH",
        salary=None,
        apply_url="https://example.com/2",
        employment_type=EmploymentType.FULL_TIME,
        work_location=WorkLocation.HYBRID,
    )

    assert calculate_job_fingerprint(job1) != calculate_job_fingerprint(job2)


def test_fingerprint_handles_missing_optional_fields():
    job = ExtractJob(
        title="React Developer",
        company="Citi",
        location=None,
        salary=None,
        apply_url="https://example.com/job",
        employment_type=EmploymentType.UNKNOWN,
        work_location=WorkLocation.UNKNOWN,
    )

    fingerprint = calculate_job_fingerprint(job)

    assert fingerprint
    assert len(fingerprint) == 64


def test_salary_and_url_do_not_affect_fingerprint():
    job1 = ExtractJob(
        title="React Developer",
        company="Citi",
        location="Durham, NH",
        salary="$80K - $100K",
        apply_url="https://glassdoor.com/job/123",
        employment_type=EmploymentType.FULL_TIME,
        work_location=WorkLocation.HYBRID,
    )

    job2 = ExtractJob(
        title="React Developer",
        company="Citi",
        location="Durham, NH",
        salary="$90K - $110K",
        apply_url="https://indeed.com/viewjob?jk=456",
        employment_type=EmploymentType.FULL_TIME,
        work_location=WorkLocation.HYBRID,
    )

    assert calculate_job_fingerprint(job1) == calculate_job_fingerprint(job2)


import datetime
from app.mail.normalizer.base import NormalizedJob
from app.mail.models import EmailProvider

def test_salary_and_url_do_not_affect_fingerprint_normalized_job():
    job1 = NormalizedJob(
         title="Full Stack Developer Java & React",
        company="Citi",
        location="Durham, NH",
        salary="$65K - $100K(Employer est.)",
        job_url="https://www.glassdoor.com/job-listing/123",
        provider=EmailProvider.ICLOUD,
        message_id="n86Jd6EZR2yXzQOJrC06mA@geopod-ismtpd-77",
        subject="Localization Web Developer at NinjaOne and 7 more jobs in Remote, US for you. Apply Now.",
        sender="noreply@glassdoor.com",
        recipient="juanjohnsmith@aol.com",
        received_at=datetime.datetime(2026, 8, 21, 0, 22, 42, tzinfo=datetime.timezone.utc)
    )

    job2 = NormalizedJob(
        title="Full Stack Developer Java & React",
        company="Citi",
        location="Durham, NH",
        salary="$65K - $100K(Employer est.)",
        job_url="https://www.indeed.com/job-listing/123",
        provider=EmailProvider.ICLOUD,
        message_id="n86Jd6EZR2yXzQOJrC06mA@geopod-ismtpd-77",
        subject="Localization Web Developer at NinjaOne and 7 more jobs in Remote, US for you. Apply Now.",
        sender="noreply@glassdoor.com",
        recipient="juanjohnsmith@aol.com",
        received_at=datetime.datetime(2026, 8, 21, 0, 22, 42, tzinfo=datetime.timezone.utc)
    )

    assert calculate_normalized_job_fingerprint(job1) == calculate_normalized_job_fingerprint(job2)


def test_same_job_produces_same_fingerprint_from_normalized_job():


    job1 = NormalizedJob(
        title="Full Stack Developer Java & React",
        company="Citi",
        location="Durham, NH",
        salary="$65K - $100K(Employer est.)",
        job_url="https://www.glassdoor.com/job-listing/123",
        provider=EmailProvider.ICLOUD,
        message_id="n86Jd6EZR2yXzQOJrC06mA@geopod-ismtpd-77",
        subject="Localization Web Developer at NinjaOne and 7 more jobs in Remote, US for you. Apply Now.",
        sender="noreply@glassdoor.com",
        recipient="juanjohnsmith@aol.com",
        received_at=datetime.datetime(2026, 8, 21, 0, 22, 42, tzinfo=datetime.timezone.utc)
    )


    job2 = NormalizedJob(
        title="Full Stack Developer Java & React",
        company="Citi",
        location="Durham, NH",
        salary="$65K - $100K(Employer est.)",
        job_url="https://www.glassdoor.com/job-listing/123",
        provider=EmailProvider.ICLOUD,
        message_id="n86Jd6EZR2yXzQOJrC06mA@geopod-ismtpd-77",
        subject="Localization Web Developer at NinjaOne and 7 more jobs in Remote, US for you. Apply Now.",
        sender="noreply@glassdoor.com",
        recipient="juanjohnsmith@aol.com",
        received_at=datetime.datetime(2026, 8, 21, 0, 22, 42, tzinfo=datetime.timezone.utc)
    )

    assert calculate_normalized_job_fingerprint(job1) == calculate_normalized_job_fingerprint(job2)