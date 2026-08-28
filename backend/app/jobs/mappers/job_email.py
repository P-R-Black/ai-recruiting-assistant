from uuid import UUID

from app.jobs.classifiers.role import JobClassification
from app.jobs.schemas import JobCreate, JobSource
from app.mail.mail_services.service import ExtractJob, parse_salary
from app.mail.normalizer.base import NormalizedJob


def build_job_create_from_normalized(
        normalized: NormalizedJob,
        *,
        fingerprint: str,
        source: JobSource,
        email_id: UUID | None = None,
        classification: JobClassification
       
) -> JobCreate:
    print("build_job_create_from_normalized called!!!")

    if normalized.title is None:
            raise ValueError("Cannot create JobCreate: job title was not extracted")
    
    if normalized.company is None:
        raise ValueError("Cannot create JobCreate: company was not extracted")

    if normalized.job_url is None:
        raise ValueError("Cannot create JobCreate: application URL was not extracted")

    salary = parse_salary(normalized.salary)

    print('callin classification:', classification)
    # classification = classify_job(normalized)


    return JobCreate(
            title=normalized.title,
            company=normalized.company,
            location=normalized.location,
            employment_type=None,
            work_location=None,
            recruiter_name=None,
            salary_min=salary.salary_min,
            salary_max=salary.salary_max,
            salary_currency=salary.currency,
            description="N/A",
            job_url=normalized.job_url,
            source=source,
            email_id=email_id,
            fingerprint=fingerprint,

            role_type=classification.role_type,
            recommended_resume=classification.recommended_resume,
            is_relevant=classification.is_relevant
            
        )


def build_job_create(
        extracted: ExtractJob,
        *,
        fingerprint: str,
        description: str,
        source: JobSource,
        email_id: UUID | None = None,
    ) -> JobCreate:

    if extracted.title is None:
        raise ValueError("Cannot create JobCreate: job title was not extracted")

    if extracted.company is None:
        raise ValueError("Cannot create JobCreate: company was not extracted")

    if extracted.apply_url is None:
        raise ValueError("Cannot create JobCreate: application URL was not extracted")

    salary = parse_salary(extracted.salary)

    return JobCreate(
        title=extracted.title,
        company=extracted.company,
        location=extracted.location,
        employment_type=extracted.employment_type,
        work_location=extracted.work_location,
        recruiter_name=extracted.recruiter,
        salary_min=salary.salary_min,
        salary_max=salary.salary_max,
        salary_currency=salary.currency,
        description=description,
        job_url=extracted.apply_url,
        source=source,
        email_id=email_id,
        fingerprint=fingerprint,
    )
