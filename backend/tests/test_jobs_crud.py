import uuid
from uuid import UUID

from app.jobs.crud import create_job, delete_job, get_job, list_jobs, update_job, update_job_status
from app.jobs.models import Job, JobStatus
from app.jobs.schemas import JobCreate, JobUpdate


def test_create_job(db, job_data):
  
    created = create_job(db, job_data)

    assert created.id is not None
    assert created.title == job_data.title
    assert created.company == job_data.company
    assert created.status == JobStatus.NEW
    assert created.created_at is not None
    assert created.updated_at is not None

    # db.query(job).delete()
    # db.commit()


def test_get_job(db, job_data):

    created = create_job(db, job_data)
    found = get_job(db, created.id)

    assert found is not None
    assert found.id == created.id
    assert found.title == "Senior Python Developer"
    assert found.company == "OpenAI"
    assert found.status == JobStatus.NEW


def test_get_job_not_found(db):
    db.query(Job).delete()
    db.commit()

    assert get_job(db, UUID('00000000-0000-0000-0000-000000000000')) is None


def test_list_jobs(db, job_data):

    created = create_job(db, job_data)
    jobs = list_jobs(db)

    assert len(jobs) == 1
    assert jobs[0].id == created.id


def test_list_jobs_filter_by_status(db, job_data):
    created = create_job(db, job_data)

    reviewed = JobCreate(
        **{
            **job_data.model_dump(mode="json"),
            "title": "Reviewed Job",
        }
    )

    created = create_job(db, reviewed)
    update_job_status(db, created.id, JobStatus.REVIEWED)

    jobs = list_jobs(db, status=JobStatus.REVIEWED)

    assert len(jobs) == 1
    assert jobs[0].id == created.id
    assert jobs[0].status == JobStatus.REVIEWED


def test_list_jobs_filter_by_company(db, job_data):
    created = create_job(db, job_data)

    second = JobCreate(
        **{
            **job_data.model_dump(mode="json"),
            "title": "OpenAI Job",
            "company": "Backend Engineer",
        }
    )

    create_job(db, second)
    jobs = list_jobs(db, company="OpenAI")
    assert len(jobs) == 1
    assert jobs[0].id == created.id
    assert jobs[0].company == "OpenAI"


def test_list_jobs_pagination(db, job_data):
    for i in range(5):
        job = JobCreate(
            **{
                **job_data.model_dump(mode="json"),
                "title": f"Job {i}",
            }
        )
        create_job(db, job)

    jobs = list_jobs(db, skip=2, limit=2)

    assert len(jobs) == 2
    assert jobs[0].title == "Job 2"
    assert jobs[-1].title == "Job 1"


def test_update_job(db, job_data):
    update = JobUpdate(title="Updated Title")
    
    created = create_job(db, job_data)
    # updated = update_job(db, created.id, {"title": "Updated Title"})
    updated = update_job(db, created.id, job_data=update)

    assert updated is not None
    assert updated.title == "Updated Title"
    assert updated.company == job_data.company
    assert updated.id == created.id


def test_update_job_status(db, job_data):
    created = create_job(db, job_data)
    updated = update_job_status(db, created.id, JobStatus.REVIEWED)

    assert updated is not None
    assert updated.status == JobStatus.REVIEWED
    assert updated.id == created.id


def test_update_job_not_found(db):
    db.query(Job).delete()
    db.commit()

    updated = update_job(
        db,
        uuid.uuid4(),
        JobUpdate(title="Doesn't Matter"),
    )

    assert updated is None

def test_update_job_status_invalid_status(client, job_payload):
    response = client.post("/jobs/", json=job_payload)
    job_id = UUID(response.json()["id"])

    response = client.patch(
        f"/jobs/{job_id}/status",
        json={"status": "closed"},
    )

    assert response.status_code == 422
    

def test_delete_job(db, job_data):
    
    created = create_job(db, job_data)
    deleted = delete_job(db, created.id)

    assert deleted is True
    assert get_job(db, created.id) is None
    assert list_jobs(db) == []


def test_delete_job_not_found(db):
    db.query(Job).delete()
    db.commit()

    deleted = delete_job(db, uuid.uuid4())

    assert deleted is False


