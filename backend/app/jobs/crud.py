from uuid import UUID

from sqlalchemy.orm import Session

from app.jobs.models import Job, JobSource, JobStatus
from app.jobs.schemas import JobCreate, JobUpdate
from app.mail.mail_services.service import WorkLocation

from app.jobs.classifiers.role import JobRoleType, ResumeRecommendation


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


def list_jobs(
        db: Session, 
        skip: int = 0, 
        limit: int = 20,
        status: JobStatus | None = None,
        source: JobSource | None = None,
        company: str | None = None,
        location: str | None = None,
        employment_type: str | None = None,
        # remote_type: str | None = None,
        work_location: WorkLocation | None = None,
        salary_min: int | None = None,
        salary_max: int | None = None,
        salary_currency: str | None = None,
        role_type: JobRoleType | None = None,
        recommended_resume: ResumeRecommendation | None = None,
        is_relevant: bool | None = None,
        ) -> list[Job]:
    
    query = db.query(Job)
    if status is not None:
        query = query.filter(Job.status == status)
    if source is not None:
        query = query.filter(Job.source == source)
    if company is not None:
        query = query.filter(Job.company.ilike(f"%{company}%"))
    if location is not None:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if employment_type is not None:
        query = query.filter(Job.employment_type.ilike(f"%{employment_type}%"))
    # if remote_type is not None:
    #     query = query.filter(Job.remote_type.ilike(f"%{remote_type}%"))
    if work_location is not None:
        query = query.filter(Job.work_location == work_location)
    if salary_min is not None:
        query = query.filter(Job.salary_min >= salary_min)
    if salary_max is not None:
        query = query.filter(Job.salary_max <= salary_max)
    if salary_currency is not None:
        query = query.filter(Job.salary_currency.ilike(f"%{salary_currency}%"))

    if role_type is not None:
        query = query.filter(Job.role_type == role_type)
    if recommended_resume is not None:
        query = query.filter(Job.recommended_resume == recommended_resume)
    if is_relevant is not None:
        query = query.filter(Job.is_relevant == is_relevant)
        
    return query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()


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


def update_job_status(db: Session, job_id: UUID, status: JobStatus) -> Job | None:
    job = get_job(db, job_id)
    
    if not job:
        return None
    
    job.status = status
    db.commit()
    db.refresh(job)
    
    return job