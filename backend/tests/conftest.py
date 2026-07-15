import pytest
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.jobs.models import Job
from app.jobs.schemas import JobCreate


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