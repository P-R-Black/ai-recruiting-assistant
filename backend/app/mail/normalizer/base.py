from abc import ABC, abstractmethod
from datetime import datetime

from app.jobs.models import JobBoard
from app.mail.schemas import EmailCreate
from app.mail.models import EmailProvider
# from app.mail.parser import ParsedEmail

from dataclasses import dataclass
from enum import Enum


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