
from sqlalchemy.orm import Session

from app.jobs.classifiers.role import classify_job
from app.jobs.crud import create_job
from app.jobs.jobs_services.deduplication import (
    calculate_job_fingerprint,
    calculate_normalized_job_fingerprint,
)
from app.jobs.mappers.job_email import build_job_create, build_job_create_from_normalized
from app.jobs.models import Job, JobSource
from app.mail.mail_services.extractor import extract_job_information
from app.mail.mail_services.service import persist_normalized_email
from app.mail.models import Email
from app.mail.normalizer.base import NormalizedJob


def persist_normalized_jobs(
    db: Session,
    jobs: list[NormalizedJob],

    ) -> list[Job]:

    
    if not jobs: 
        return []

    email = persist_normalized_email(db, jobs)
   
    

    if email is None:
        return []

    created_jobs = []

    for normalized in jobs:
        classification = classify_job(normalized)

        fingerprint = calculate_normalized_job_fingerprint(normalized)

        if job_exists_by_fingerprint(db, fingerprint):
            continue

        job_data = build_job_create_from_normalized(
            normalized,
            fingerprint=fingerprint,
            source=JobSource.MAIL,
            email_id=email.id,
            classification=classification
        )


        job = create_job(db, job_data)
        created_jobs.append(job)

    return created_jobs


# For Emails with one or more jobs
def create_jobs_from_email(
    db: Session,
    email: Email,
) -> list[Job]:

    extracted_jobs = extract_job_information(email)

    created_jobs = []

    for extracted in extracted_jobs:
        fingerprint = calculate_job_fingerprint(extracted)

        if job_exists_by_fingerprint(db, fingerprint):
            continue

        job_data = build_job_create(
            extracted,
            fingerprint=fingerprint,
            description=email.raw_body,
            source=JobSource.MAIL,
            email_id=email.id,
        )

        job = create_job(db, job_data)
        created_jobs.append(job)

    return created_jobs


def create_job_from_email(
    db: Session,
    email: Email,
    ) -> Job | None:

    # going to add a fuction here to see if dup first
    # if is_duplicate_job_email(db, email):
    #     return None


    extracted = extract_job_information(email)

    fingerprint = calculate_job_fingerprint(extracted)

    if job_exists_by_fingerprint(db, fingerprint):
        return None


    job_data = build_job_create(
        extracted,
        fingerprint=fingerprint,
        description=email.raw_body,
        source=JobSource.MAIL,
        email_id=email.id,
    )

    return create_job(db, job_data)


def job_exists_by_fingerprint(
        db: Session,
        fingerprint: str,
) -> bool:
    return(db.query(Job)
           .filter(Job.fingerprint == fingerprint)
           .first()
           is not None)