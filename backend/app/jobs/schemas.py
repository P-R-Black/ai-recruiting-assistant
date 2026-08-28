from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from app.jobs.classifiers.role import JobRoleType, ResumeRecommendation
from app.jobs.models import JobSource, JobStatus
from app.mail.models import EmploymentType, WorkLocation

Title = Annotated[str, Field(min_length=1, max_length=255)]
Company = Annotated[str, Field(min_length=1, max_length=255)]
Location = Annotated[str | None, Field(max_length=255)]
RemoteType = Annotated[str | None, Field(max_length=100)]
Salary = Annotated[int | None, Field(ge=0)]
Currency = Annotated[str | None, Field(max_length=10)]
Description = Annotated[str, Field(min_length=1)]
JobUrl = HttpUrl


class JobBase(BaseModel):
    title: Title
    company: Company
    location: Location = None

    employment_type: EmploymentType | None = None
    work_location: WorkLocation | None = None

    recruiter_name: str | None = None

    salary_min: Salary = None
    salary_max: Salary = None
    salary_currency: Currency = None

    description: Description
    job_url: JobUrl
    source: JobSource

    email_id: UUID | None = None
    fingerprint: str

    role_type: JobRoleType | None = None
    recommended_resume: ResumeRecommendation | None = None

    is_relevant: bool | None = None

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class JobCreate(JobBase):
    @model_validator(mode="after")
    def validate_salary_range(self) -> "JobCreate":
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_max < self.salary_min
        ):
            raise ValueError(
                "salary_max must be greater than or equal to salary_min"
            )

        return self


class JobUpdate(BaseModel):
    title: Title | None = None
    company: Company | None = None
    location: Location = None

    employment_type: EmploymentType | None = None
    work_location: WorkLocation | None = None
    recruiter_name: str | None = None

    email_id: UUID | None = None

    salary_min: Salary = None
    salary_max: Salary = None
    salary_currency: Currency = None

    description: Description | None = None
    job_url: JobUrl | None = None
    source: JobSource | None = None

    
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    @model_validator(mode="after")
    def validate_salary_range(self) -> "JobUpdate":
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_max < self.salary_min
        ):
            raise ValueError(
                "salary_max must be greater than or equal to salary_min"
            )

        return self


class JobStatusUpdate(BaseModel):
    status: JobStatus


class JobResponse(JobBase):
    id: UUID
    status: JobStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# A pydantic model for AI/Extraction Results
class JobExtraction(BaseModel):
    title: Title | None = None
    company: Company | None = None
    location: Location | None = None

    employment_type: EmploymentType = EmploymentType.UNKNOWN
    work_location: WorkLocation = WorkLocation.UNKNOWN

    recruiter_name: str| None = None
    
    salary_min: Salary = None
    salary_max: Salary = None
    salary_currency: Currency = None
    
    description: Description | None = None
    job_url: JobUrl | None = None

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )
    

# Update to use later
# class JobFilter(BaseModel):
#     skip: int = 0
#     limit: int = 20
#     status: JobStatus | None = None
#     source: JobSource | None = None
#     company: Company | None = None
#     location: Location | None = None
#     employment_type: EmploymentType | None = None
#     remote_type: RemoteType | None = None
#     salary_min: Salary | None = None
#     salary_max: Salary | None = None
#     salary_currency: Currency | None = None


