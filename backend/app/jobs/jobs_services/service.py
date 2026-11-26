
import logging

import httpx
from sqlalchemy.orm import Session

from app.job_page.service import process_job_page
from app.jobs.classifiers.role import classify_job
from app.jobs.crud import create_job
from app.jobs.jobs_services.deduplication import (
    calculate_job_fingerprint,
    calculate_normalized_job_fingerprint,
)
from app.jobs.mappers.job_email import build_job_create, build_job_create_from_normalized
from app.jobs.models import Job, JobExtractionStatus, JobSource
from app.mail.mail_services.extractors.extractor import extract_job_information
from app.mail.mail_services.service import persist_normalized_email
from app.mail.models import Email
from app.mail.normalizer.base import NormalizedJob

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


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

        # Retreive and extact the full job descriton.
        description = None
        extraction_method = None
        extraction_status = JobExtractionStatus.NOT_ATTEMPTED

        # build JobCreate using normalized and extracted data
        
        if normalized.job_url:
            try:
                logger.info("Retrieving job page: %s", normalized.job_url)

                page = process_job_page(normalized.job_url)

                logger.info(
                    "Job page result: description_present=%s, method=%s",
                    bool(page.description),
                    page.extraction_method,
                )

                description = page.description
                extraction_method = page.extraction_method

                if description:
                    extraction_status = JobExtractionStatus.SUCCEEDED
                else:
                    extraction_status = JobExtractionStatus.NO_DESCRIPTION

                # url not being opened and processed, getting a 429; 
                # trying to slow things down with sleep
                
            except (httpx.HTTPError, ValueError):
                logger.exception(
                    "Unable to retrieve job page: %s",
                    normalized.job_url,
                )
                extraction_status = JobExtractionStatus.FAILED

            # finally:
            #     time.sleep(7)

        # create the job

        job_data = build_job_create_from_normalized(
            normalized,
            fingerprint=fingerprint,
            source=JobSource.MAIL,
            email_id=email.id,
            classification=classification,
            description=description,
            extraction_status=extraction_status,
            extraction_method=extraction_method,
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