from uuid import UUID

from app.jobs.schemas import JobCreate, JobSource
from app.mail.mail_services.service import ExtractJob, parse_salary


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

