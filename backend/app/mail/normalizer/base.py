from abc import ABC, abstractmethod

# from app.mail.parser import ParsedEmail
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from app.mail.models import EmailProvider


class NormalizedJobSource(str, Enum):
    GLASSDOOR = "glassdoor"
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    ZIPRECRUITER = "ziprecruiter"
    DICE = "dice"
    UNKNOWN = "unknown"


@dataclass
class NormalizedJob:
    title: str | None
    company: str | None
    location: str | None
    salary: str | None
    job_url: str | None

    provider: EmailProvider | None
    message_id: str | None
    subject: str | None
    sender: str | None
    recipient: str | None
    received_at: datetime | None




@dataclass
class ParsedEmail:
    message_id: str
    provider: EmailProvider
    subject: str | None
    sender: str
    recipient: str
    received_at: datetime
    text_body: str
    html_body: str | None






class BaseEmailNormalizer(ABC):
    """
    Base interface for provider-specific email normalizers.

    A single physical email may contain zero, one, or many jobs.
    Normalizers convert that provider-specific email into zero or more
    EmailCreate objects, with each EmailCreate representing one job
    opportunity.
    """

    @abstractmethod
    def normalize(self, email: ParsedEmail) -> list[NormalizedJob]:
        """
        Convert a provider-specific email into normalized jobs.

        A single physical email may contain zero, one, or many
        job opportunities.
        """
        raise NotImplementedError


def email_metadata(email: ParsedEmail) -> dict:
    """Shared metadata every NormalizedJob from this email will carry"""

    # print('_email_metadata:', email)

    return {
        "provider": email.provider,
        "message_id": email.message_id,
        "subject": email.subject,
        "sender": email.sender,
        "recipient": email.recipient,
        "received_at": email.received_at,
        }