import json
from pathlib import Path
import httpx
import pytest
from app.job_page.schema import JobPageProcessingResponse
from app.jobs.models import JobSource, Job, JobExtractionStatus
from app.jobs.jobs_services.service import (
    create_job_from_email, persist_normalized_jobs
    )


from app.mail.models import Email
from app.mail.mail_services.parsers.mime_parser import build_parsed_email
from app.mail.crud import create_email
from app.mail.models import EmailProvider

from app.job_page.normalizer import normalizer
from tests.conftest import sample_job_email_complete

from app.mail.normalizer.glassdoor import GlassdoorNormalizer

from app.job_page.parsers.glassdoor import GlassdoorJobPageExtractor, JobPageResponse

from tests.mail.normalizer.test_glassdoor_normalizer import load_email_fixture, FIXTURES


from app.job_page import service as job_page_service


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

    created_jobs = persist_normalized_jobs(db, jobs)

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


@pytest.fixture
def normalized_glassdoor_jobs():
    raw_email = load_email_fixture("glassdoor_multiple_jobs.eml")

    parsed = build_parsed_email(
        raw_email,
        EmailProvider.ICLOUD,
    )

    return GlassdoorNormalizer().normalize(parsed)


def test_persist_normalized_jobs_saves_job_description(db, mocker, normalized_glassdoor_jobs):
    process_job_page_mock = mocker.patch(
        "app.jobs.jobs_services.service.process_job_page",
        return_value=JobPageProcessingResponse(
            requested_url="https://www.glassdoor.com/job-listing/example",
            final_url="https://www.glassdoor.com/job-listing/example",
            status_code=200,
            description="This is the full job description.",
            responsibilities=[
                "Build APIs",
                "Maintain backend services",
            ],
            required_qualifications=["Python experience"],
            preferred_qualifications=["Docker experience"],
            extraction_method="dom+text",
        ),
    )


    created_jobs = persist_normalized_jobs(
        db,
        normalized_glassdoor_jobs,
    )

    for job in created_jobs:
        assert job.description == "This is the full job description."
        assert job.extraction_status == JobExtractionStatus.SUCCEEDED
        assert job.extraction_method == "dom+text"


    assert len(created_jobs) == 10

    for job in created_jobs:
        assert job.description == "This is the full job description."

    assert process_job_page_mock.call_count == 10



def test_persist_normalized_jobs_skips_page_processing_for_duplicates(
    db,
    mocker,
    normalized_glassdoor_jobs
):
    process_job_page_mock = mocker.patch(
        "app.jobs.jobs_services.service.process_job_page",
        return_value=JobPageProcessingResponse(
            requested_url="https://www.glassdoor.com/job-listing/example",
            final_url="https://www.glassdoor.com/job-listing/example",
            status_code=200,
            description="This is the full job description.",
        ),
    )

  
    first_result = persist_normalized_jobs(db, normalized_glassdoor_jobs)

    assert len(first_result) == 10
    assert process_job_page_mock.call_count == 10

    process_job_page_mock.reset_mock()

    second_result = persist_normalized_jobs(db, normalized_glassdoor_jobs)

    assert second_result == []
    process_job_page_mock.assert_not_called()
    assert db.query(Job).count() == 10


def test_persist_normalized_jobs_saves_job_when_page_retrieval_fails(
        db,
        mocker,
        normalized_glassdoor_jobs
    ):
    process_job_page_mock = mocker.patch(
        "app.jobs.jobs_services.service.process_job_page",
        side_effect=httpx.HTTPError("Job page unavailable"),
    )

    created_jobs = persist_normalized_jobs(
            db,
            normalized_glassdoor_jobs,
        )

    for job in created_jobs:
        assert job.description is None
        assert job.extraction_status == JobExtractionStatus.FAILED
        assert job.extraction_method is None

    assert len(created_jobs) == 10

    for job in created_jobs:
        assert job.description is None

    assert process_job_page_mock.call_count == 10
    assert db.query(Job).count() == 10



def test_persist_normalized_jobs_saves_job_when_description_is_empty(
    db,
    mocker,
    normalized_glassdoor_jobs
    ):

    process_job_page_mock = mocker.patch(
        "app.jobs.jobs_services.service.process_job_page",
        return_value=JobPageProcessingResponse(
            requested_url="https://www.glassdoor.com/job-listing/example",
            final_url="https://www.glassdoor.com/job-listing/example",
            status_code=200,
            description=None,
            extraction_method=None,
        ),
    )

    created_jobs = persist_normalized_jobs(db, normalized_glassdoor_jobs)

    for job in created_jobs:
        assert job.description is None
        assert job.extraction_status == JobExtractionStatus.NO_DESCRIPTION
        assert job.extraction_method is None

    assert len(created_jobs) == 10

    for job in created_jobs:
        assert job.description is None

    assert process_job_page_mock.call_count == 10
    assert db.query(Job).count() == 10


FIXTURE_DIR = (
    Path(__file__).parent.parent.parent
    / "job_page"
    / "fixtures"
    / "job_pages"
    / "glassdoor"
)




@pytest.fixture
def load_html_fixture():
    def _load(filename: str) -> str:
        return (FIXTURE_DIR / filename).read_text(encoding="utf-8")

    return _load



def test_persist_normalized_jobs_saves_extracted_description(
    db,
    monkeypatch,
    normalized_glassdoor_jobs,
    load_html_fixture,
):
    # Arrange: load a real Glassdoor job-page fixture.
    html = load_html_fixture("optum_job_1.html")

    requested_url = normalized_glassdoor_jobs[0].job_url

    page = JobPageResponse(
        requested_url=requested_url,
        final_url="https://www.glassdoor.com/job-listing/test-job.htm",
        status_code=200,
        html=html,
    )

    # Mock only the HTTP retrieval. The real extraction logic will run.
    monkeypatch.setattr(
        job_page_service,
        "retrieve_job_page",
        lambda _: page,
    )

    # Act: persist one normalized job through the complete pipeline.
    created_jobs = persist_normalized_jobs(
        db,
        normalized_glassdoor_jobs[:1],
    )

    # Assert: the job was created.
    assert len(created_jobs) == 1

    # Retrieve the persisted record directly from the database.
    persisted_job = db.query(Job).one()

    assert persisted_job.id == created_jobs[0].id

    # Verify the extracted description made it into the database.
    assert persisted_job.description
    assert persisted_job.description == created_jobs[0].description

    assert persisted_job.extraction_status == JobExtractionStatus.SUCCEEDED
    assert persisted_job.extraction_method is not None