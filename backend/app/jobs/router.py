
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.jobs import crud
from app.jobs.schemas import JobCreate, JobResponse, JobStatusUpdate, JobUpdate

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)

@router.post("/", response_model=JobResponse, status_code=201)
def create_new_job_endpoint(
    job: JobCreate,
    db: Session = Depends(get_db),
    ):
    return crud.create_job(db, job)


@router.get("/", response_model=list[JobResponse])
def list_jobs_endpoint(db: Session = Depends(get_db)):
    return crud.list_jobs(db)


@router.get("/{job_id}", response_model=JobResponse)
def get_job_endpoint(job_id: UUID,db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job


@router.patch("/{job_id}", response_model=JobResponse)
def update_job_endpoint(
    job_id: UUID,
    job_update: JobUpdate,
    db: Session = Depends(get_db),
    ):

    updated = crud.update_job(db, job_id, job_update)
    if updated is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return updated


@router.patch("/{job_id}/status", response_model=JobResponse)
def update_job_status_endpoint(
    job_id: UUID,
    status_update: JobStatusUpdate,
    db: Session = Depends(get_db),
    ):

    updated = crud.update_job_status(db, job_id, status_update.status)
    if updated is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return updated


@router.delete("/{job_id}", status_code=204)
def delete_job_endpoint(
    job_id: UUID,
    db: Session = Depends(get_db),
    ):

    deleted = crud.delete_job(db, job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return None
