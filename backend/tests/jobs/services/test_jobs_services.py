from app.jobs.models import JobSource, Job
from app.jobs.jobs_services.service import create_job_from_email, create_jobs_from_email

from app.mail.crud import create_email

from tests.conftest import sample_job_email_complete


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