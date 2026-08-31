import pytest
from pathlib import Path
from app.core.config import settings

from datetime import datetime, timezone

from app.jobs.models import JobSource, Job
from app.jobs.jobs_services.service import (
    create_job_from_email, persist_normalized_jobs
    )


from app.mail.models import Email
from app.mail.mail_services.mime_parser import build_parsed_email
from app.mail.crud import create_email
from app.mail.models import EmailProvider

from tests.conftest import sample_job_email_complete

from app.mail.normalizer.glassdoor import GlassdoorNormalizer
from app.mail.normalizer.base import ParsedEmail

from tests.mail.normalizer.test_glassdoor_normalizer import load_email_fixture, FIXTURES



def test_create_job_from_email(db):
    email_data = sample_job_email_complete()

    email = create_email(db, email_data)

    job = create_job_from_email(db, email)

    assert job.title == "Junior Frontend Developer"
    assert job.company == "OpenAI"
    assert job.location == "Orlando, FL"
    assert job.email_id == email.id
    assert job.source == JobSource.MAIL
    assert job.salary_min == 180000
    assert job.salary_max == 220000

    assert job.fingerprint is not None
    assert len(job.fingerprint) == 64



def test_persist_normalized_jobs(db):
    raw_email = load_email_fixture(
           "glassdoor_multiple_jobs.eml"
       )
   
    parsed = build_parsed_email(
        raw_email,
        EmailProvider.ICLOUD,
    )

    jobs = GlassdoorNormalizer().normalize(parsed)
    print('DEBUG do i get jobs?', jobs)

    created_jobs = persist_normalized_jobs(db, jobs)
    print('DEBUG do i get created_jobs?', created_jobs)

    assert len(created_jobs) == 10

    email = db.query(Email).filter(Email.message_id == jobs[0].message_id).one()

    assert email is not None
    assert email.message_id == jobs[0].message_id

    for job in created_jobs:
        assert job.email_id == email.id

    assert len(email.jobs) == 10

    target_job = created_jobs[0]

    assert target_job.email_id is not None

 
    email = db.get(Email, target_job.email_id)
    assert email is not None
    assert email.message_id == jobs[0].message_id
    assert all(
        created_job.email_id == target_job.email_id
        for created_job in created_jobs
    )

    assert all(
        job.email_id == email.id
        for job in created_jobs
    )

    assert db.query(Email).count() == 1
    assert db.query(Job).count() == 10

    # assert target_job.title == "IT Business Systems Developer"
    # assert target_job.location == "United States"
    # assert target_job.company == "WITTENSTEIN"
    # assert target_job.salary_min == 70
    # assert target_job.salary_max == 90
    # assert target_job.salary_currency == "USD"
    # assert target_job.job_url.startswith("https://www.glassdoor.com/")

    # assert target_job.fingerprint is not None
    # assert len(target_job.fingerprint) == 64




def test_persist_normalized_jobs_is_idempotent(db):
    raw_email = load_email_fixture("glassdoor_multiple_jobs.eml")

    parsed = build_parsed_email(
        raw_email,
        EmailProvider.ICLOUD,
    )

    jobs = GlassdoorNormalizer().normalize(parsed)

    first = persist_normalized_jobs(db, jobs)
    second = persist_normalized_jobs(db, jobs)

    assert len(first) == 10
    assert len(second) == 0

    assert db.query(Email).count() == 1
    assert db.query(Job).count() == 10