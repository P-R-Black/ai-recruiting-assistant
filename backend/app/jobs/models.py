from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.jobs.classifiers.role import JobRoleType, ResumeRecommendation
from app.mail.models import EmploymentType, WorkLocation

if TYPE_CHECKING:
    from app.mail.models import Email


class JobStatus(str, enum.Enum):
    NEW = "new"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"
    FAILED = "failed"
    ARCHIVED = "archived"


class JobSource(str, enum.Enum):
    MAIL = "mail"
    SCRAPER = "scraper"
    API = "api"
    MANUAL = "manual"


class JobBoard(str, enum.Enum):
    GLASSDOOR = "glassdoor"
    INDEED = "indeed"
    ZIPRECRUITER = "ziprecruiter"
    LINKEDIN = "linkedin"
    DICE = "dice"
    UNKNOWN = "unknown"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    company: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
    )

    employment_type: Mapped[EmploymentType | None] = mapped_column(
        Enum(EmploymentType,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
            ),
    )

    work_location: Mapped[WorkLocation | None] = mapped_column(
        Enum(
            WorkLocation,
            values_callable=lambda enum_cls: [member.value for member in enum_cls], 
            ),
    )

    recruiter_name: Mapped[str | None] = mapped_column(
        String(255),
    )

    salary_min: Mapped[int | None] = mapped_column(
        Integer,
    )

    salary_max: Mapped[int | None] = mapped_column(
        Integer,
    )

    salary_currency: Mapped[str | None] = mapped_column(
        String(10),
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    job_url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
    )

    source: Mapped[JobSource] = mapped_column(
        Enum(JobSource, values_callable=lambda enum: [e.value for e in enum]),
        nullable=False,
    )


    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, values_callable=lambda enum: [e.value for e in enum]),
        default=JobStatus.NEW,
        nullable=False,
    )

    email_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("emails.id"),
        nullable=True,
        index=True
    )

    email: Mapped["Email | None"] = relationship(
        "Email",
        back_populates="jobs"
    )

    fingerprint: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )

    role_type: Mapped[JobRoleType] = mapped_column(
        Enum(
            JobRoleType,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=True,
    )

    recommended_resume: Mapped[ResumeRecommendation] = mapped_column(
        Enum(
            ResumeRecommendation,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=True,
    )

    is_relevant: Mapped[bool] = mapped_column(
        Boolean, 
        nullable=True
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )