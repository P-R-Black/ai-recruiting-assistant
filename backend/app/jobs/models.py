from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


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

    employment_type: Mapped[str | None] = mapped_column(
        String(100),
    )

    remote_type: Mapped[str | None] = mapped_column(
        String(100),
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