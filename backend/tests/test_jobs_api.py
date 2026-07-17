from uuid import UUID

from app.jobs.models import Job
    

def test_create_job_endpoint(client, db, job_payload):

    response = client.post("/jobs/", json=job_payload)

    assert response.status_code == 201

    data = response.json()
    
    assert data["title"] == job_payload["title"]
    assert data["company"] == job_payload["company"]
    assert data["status"] == "new"
    assert data["job_url"] == job_payload["job_url"]
    assert data["source"] == job_payload["source"]
    assert "id" in data
    assert "created_at" in data

    job = db.get(Job, UUID(data["id"]))
    assert job is not None
    assert job.title == job_payload["title"]



def test_list_jobs_endpoint(client, db):
    response = client.get("/jobs/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_job_endpoint(client, db, job_payload):
   
    response = client.post("/jobs/", json=job_payload)
    assert response.status_code == 201
    job_id = UUID(response.json()["id"])

    # Then, retrieve the job
    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(job_id)


def test_get_missing_job(client):
    response = client.get("/jobs/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_update_job_endpoint(client, db, job_payload):
    # Create a job first
    create_response = client.post("/jobs/", json=job_payload)
    assert create_response.status_code == 201

    job_id = create_response.json()["id"]

    # Update only a few fields
    update_payload = {
        "title": "Principal Python Developer",
        "salary_max": 250000,
    }

    response = client.patch(
        f"/jobs/{job_id}",
        json=update_payload,
    )

    assert response.status_code == 200

    data = response.json()

    # Updated fields
    assert data["title"] == update_payload["title"]
    assert data["salary_max"] == update_payload["salary_max"]

    # Unchanged fields
    assert data["company"] == job_payload["company"]
    assert data["salary_min"] == job_payload["salary_min"]

    # Verify database contents
    job = db.get(Job, UUID(job_id))

    assert job is not None
    assert job.title == update_payload["title"]
    assert job.salary_max == update_payload["salary_max"]
    assert job.company == job_payload["company"]


def test_delete_job_endpoint(client, db, job_payload):
    # Create a job
    response = client.post("/jobs/", json=job_payload)
    assert response.status_code == 201

    job_id = UUID(response.json()["id"])

    # Delete the job
    response = client.delete(f"/jobs/{job_id}")

    assert response.status_code == 204

    # Verify it was deleted from the database
    job = db.get(Job, job_id)
    assert job is None

"""
Run individual tests
uv run pytest tests/test_jobs_api.py
make test TEST=tests/test_jobs_api.py
uv run pytest -s (to show print statements for passing tests)
uv run pytest -s tests/test_jobs_api.py (to show print statements for passing tests)
"""