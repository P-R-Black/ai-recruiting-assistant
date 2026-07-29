from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.jobs.models import Job
from app.jobs.schemas import JobCreate
from app.mail.models import EmailProvider
from app.mail.schemas import EmailCreate
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def job_data() -> JobCreate:
    return JobCreate(
        title="Senior Python Developer",
        company="OpenAI",
        location="Remote",
        employment_type="Full-time",
        remote_type="Remote",
        salary_min=150000,
        salary_max=200000,
        salary_currency="USD",
        description="A long enough description for validation purposes.",
        job_url="https://example.com/jobs/1",
        source="mail",
    )

@pytest.fixture
def job_payload():
    return {
        "title": "Senior Python Developer",
        "company": "OpenAI",
        "location": "Remote",
        "employment_type": "Full-time",
        "remote_type": "Remote",
        "salary_min": 150000,
        "salary_max": 200000,
        "salary_currency": "USD",
        "description": "A long enough description for validation purposes.",
        "job_url": "https://example.com/jobs/1",
        "source": "mail",
    }


@pytest.fixture
def db() -> Session:
    session = SessionLocal()

    session.query(Job).delete()
    session.commit()

    try:
        yield session
    finally:
        session.rollback()
        session.query(Job).delete()
        session.commit()
        session.close()


    # session = SessionLocal()
    
    # try:
    #     yield session
    # finally:
    #     session.rollback()
    #     session.close()


@pytest.fixture
def email_data():
    return EmailCreate(
        provider=EmailProvider.APPLE,
        message_id="<message-1@example.com>",
        subject="Python Developer",
        sender="jobs@example.com",
        recipient="me@example.com",
        received_at=datetime.now(UTC),
        raw_body="This is a sample job email"
    )