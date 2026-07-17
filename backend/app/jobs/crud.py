from uuid import UUID

from sqlalchemy.orm import Session

from app.jobs.models import Job
from app.jobs.schemas import JobCreate, JobUpdate


def create_job(db: Session, job: JobCreate) -> Job:
    db_job = Job(**job.model_dump(mode="json"))

    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    return db_job
    


def get_job(db: Session, job_id: UUID) -> Job | None:
    return (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )


def list_jobs(db: Session) -> list[Job]:
    return db.query(Job).all()


def update_job(db: Session, job_id: UUID, job_data: JobUpdate) -> Job | None:
    
    job = get_job(db, job_id)
    
    if not job:
        return None
    
    updates = job_data.model_dump(exclude_unset=True)
    if "job_url" in updates:
        updates["job_url"] = str(updates["job_url"])
    
    for key, value in updates.items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)
    
    return job


def delete_job(db: Session, job_id: UUID) -> bool:
    job = get_job(db, job_id)
    if not job:
        return False
    db.delete(job)
    db.commit()
    return True