from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.mail.models import EmailProvider


class EmailCreate(BaseModel):
    provider: Annotated[EmailProvider, Field(max_length=50)]
    message_id: Annotated[str, Field(max_length=512)]
    subject: Annotated[str | None, Field(default=None, max_length=750)]
    sender: Annotated[str, Field(max_length=255)]
    recipient: Annotated[str, Field(max_length=255)]
    received_at: datetime
    raw_body: str

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class EmailResponse(BaseModel):
    id: UUID
    provider: EmailProvider
    message_id: str
    subject: str | None
    sender: str
    recipient: str
    received_at: datetime
    raw_body: str
    imported_at: datetime
    processed: bool
    is_job_email: bool

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        from_attributes=True,
    )


class EmailUpdate(BaseModel):
    processed: bool | None = None
    is_job_email: bool | None = None

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class EmailFilter(BaseModel):
    provider: EmailProvider | None = None
    sender: str | None = None
    recipient: str | None = None
    processed: bool | None = None
    is_job_email: bool | None = None

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

