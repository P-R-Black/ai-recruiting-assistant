from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from app.jobs.models import JobSource, JobStatus

Title = Annotated[str, Field(min_length=1, max_length=255)]
Company = Annotated[str, Field(min_length=1, max_length=255)]
Location = Annotated[str | None, Field(max_length=255)]
EmploymentType = Annotated[str | None, Field(max_length=100)]
RemoteType = Annotated[str | None, Field(max_length=100)]
Salary = Annotated[int | None, Field(ge=0)]
Currency = Annotated[str | None, Field(max_length=10)]
Description = Annotated[str, Field(min_length=1)]
JobUrl = HttpUrl


class JobBase(BaseModel):
    title: Title
    company: Company
    location: Location = None
    employment_type: EmploymentType = None
    remote_type: RemoteType = None

    salary_min: Salary = None
    salary_max: Salary = None
    salary_currency: Currency = None

    description: Description
    job_url: JobUrl
    source: JobSource

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
    employment_type: EmploymentType = None
    remote_type: RemoteType = None

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


# Future endpoint:
# PATCH /jobs/{job_id}/status
# Used to update only the job status.
class JobStatusUpdate(BaseModel):
    status: JobStatus
    

class JobResponse(JobBase):
    id: UUID
    status: JobStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)