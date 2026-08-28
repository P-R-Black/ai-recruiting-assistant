import pytest
from pathlib import Path
from app.core.config import settings

from datetime import datetime, timezone

from app.jobs.models import JobSource, Job
from app.jobs.jobs_services.service import (
    create_job_from_email, create_job_from_email, persist_normalized_jobs
    )



from app.mail.mail_services.mime_parser import build_parsed_email
from app.mail.models import EmailProvider

from app.mail.normalizer.base import NormalizedJob
from app.mail.normalizer.glassdoor import GlassdoorNormalizer
from app.mail.normalizer.zip_recruiter import ZipRecruiterNormalizer


from tests.mail.normalizer.test_glassdoor_normalizer import load_email_fixture, FIXTURES

from app.jobs.classifiers.role import classify_job_title, classify_job, JobRoleType, ResumeRecommendation


def test_classify_frontend_title():
    assert classify_job_title("Frontend React Developer") == JobRoleType.FRONTEND


def test_classify_backend_title():
    assert classify_job_title("Backend Software Engineer") == JobRoleType.BACKEND


def test_classify_full_stack_title():
    assert classify_job_title("Full Stack Software Engineer") == JobRoleType.FULL_STACK


def test_classify_unrelated_title():
    assert classify_job_title("Civil Engineer") == JobRoleType.NON_SOFTWARE


def test_classify_job():
    jobs = NormalizedJob(
            title="Power Apps Software Developer",
            company="Example",
            location="Orlando, FL",
            salary=None,
            job_url="https://example.com/job",
            provider=EmailProvider.ICLOUD,
            message_id="test-message-id",
            subject="Test job",
            sender="test@example.com",
            recipient="ramoneblack@me.com",
            received_at=datetime.now(timezone.utc),
        )

    classified_job = classify_job(jobs)


    assert classified_job.is_relevant == True
    assert classified_job.role_type == JobRoleType.SOFTWARE_ENGINEER
    assert classified_job.recommended_resume == ResumeRecommendation.FULL_STACK


def test_classify_job_unknown():

    jobs = NormalizedJob(
        title="IT Business Systems Developer",
        company="Example",
        location="Orlando, FL",
        salary=None,
        job_url="https://example.com/job",
        provider=EmailProvider.ICLOUD,
        message_id="test-message-id",
        subject="Test job",
        sender="test@example.com",
        recipient="ramoneblack@me.com",
        received_at=datetime.now(timezone.utc),
    )


    classified_job = classify_job(jobs)

    assert classified_job.is_relevant == False
    assert classified_job.role_type == JobRoleType.UNKNOWN
    assert classified_job.recommended_resume == ResumeRecommendation.UNKNOWN


def test_classify_job_full_stack():
    jobs = NormalizedJob(
        title="Full Stack Engineer ID80989",
        company="Example",
        location="Orlando, FL",
        salary=None,
        job_url="https://example.com/job",
        provider=EmailProvider.ICLOUD,
        message_id="test-message-id",
        subject="Test job",
        sender="test@example.com",
        recipient="ramoneblack@me.com",
        received_at=datetime.now(timezone.utc),
    )

    classified_job = classify_job(jobs)

    assert classified_job.is_relevant == True
    assert classified_job.role_type == JobRoleType.FULL_STACK
    assert classified_job.recommended_resume == ResumeRecommendation.FULL_STACK


def test_classify_job_frontend():
    jobs = NormalizedJob(
            title="Front-End Engineer",
            company="Example",
            location="Orlando, FL",
            salary=None,
            job_url="https://example.com/job",
            provider=EmailProvider.ICLOUD,
            message_id="test-message-id",
            subject="Test job",
            sender="test@example.com",
            recipient="ramoneblack@me.com",
            received_at=datetime.now(timezone.utc),
        )

    classified_job = classify_job(jobs)
  

    assert classified_job.is_relevant == True
    assert classified_job.role_type == JobRoleType.FRONTEND
    assert classified_job.recommended_resume == ResumeRecommendation.FRONTEND


def test_classify_job_frontend():
 

    jobs = NormalizedJob(
            title="Front-End Engineer",
            company="Example",
            location="Orlando, FL",
            salary=None,
            job_url="https://example.com/job",
            provider=EmailProvider.ICLOUD,
            message_id="test-message-id",
            subject="Test job",
            sender="test@example.com",
            recipient="ramoneblack@me.com",
            received_at=datetime.now(timezone.utc),
        )

    classified_job = classify_job(jobs)
  

    assert classified_job.is_relevant == True
    assert classified_job.role_type == JobRoleType.FRONTEND
    assert classified_job.recommended_resume == ResumeRecommendation.FRONTEND



def test_classify_job_non_software():
 
    jobs = NormalizedJob(
            title="Graphic Designer",
            company="Example",
            location="Orlando, FL",
            salary=None,
            job_url="https://example.com/job",
            provider=EmailProvider.ICLOUD,
            message_id="test-message-id",
            subject="Test job",
            sender="test@example.com",
            recipient="ramoneblack@me.com",
            received_at=datetime.now(timezone.utc),
        )

    classified_job = classify_job(jobs)
  

    assert classified_job.is_relevant == False
    assert classified_job.role_type == JobRoleType.NON_SOFTWARE
    assert classified_job.recommended_resume == ResumeRecommendation.NON_SOFTWARE