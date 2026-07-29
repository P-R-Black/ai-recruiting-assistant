
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class EmailProvider(str, enum.Enum):
    APPLE = "apple_mail"  
    GMAIL = "gmail"
    ICLOUD = "icloud"
    OUTLOOK = "outlook"
    YAHOO = "yahoo"
    OTHER = "other"


class Email(Base):

    __tablename__ = "emails"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    provider: Mapped[EmailProvider] = mapped_column(
        Enum(EmailProvider)
    )
    
    message_id: Mapped[str] = mapped_column(
        String(512), 
        unique=True,
        index=True,
        nullable=False    
    )
    subject: Mapped[str] = mapped_column(
        String(750), 
        nullable=True
    )

    sender: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )

    recipient: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False
    )

    raw_body: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    processed: Mapped[bool] = mapped_column(
        Boolean, 
        default=False,
        nullable=False
    )
    
    is_job_email: Mapped[bool] = mapped_column(
        Boolean, 
        default=False,
        nullable=False
    )

