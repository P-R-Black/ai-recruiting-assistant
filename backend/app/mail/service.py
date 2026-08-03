import re
from dataclasses import dataclass, field

from app.mail.models import EmailProvider

JOB_KEYWORDS = [
    "job",
    "position",
    "opportunity",
    "career",
    "application",
    "interview",
    "recruiter",
    "hiring",
]

FREE_EMAIL_PROVIDERS = [
    "gmail.com",
    "hotmail.com",
    "outlook.com",
    "icloud.com",
    "me.com",
    "yahoo.com",
    "aol.com",
]

RECRUITER_KEYWORDS = [
    "recruit",
    "recruiter",
    "talent",
    "career",
    "careers",
    "hiring",
    "jobs",
    "staffing",
    "hr",
    "humanresources",
]

JOB_BOARD_DOMAINS = {
    "linkedin.com": 5,
    "indeed.com": 5,
    "glassdoor.com": 5,
    "greenhouse.io": 4,
    "lever.co": 4,
    "ashbyhq.com": 4,
    "workday.com": 3,
}


SALARY_KEYWORDS = [
    "salary",
    "$",
    "usd",
    "per year",
    "/year",
    "annual",
    "compensation",
]

REJECTION_KEYWORDS = [
    "unfortunately",
    "we regret",
    "not moving forward",
    "another candidate",
    "other candidates",
    "position has been filled",
    "thank you for your interest",
    "we appreciate your interest",
    "we have decided",
    "we will not",
    "declined",
]

UNSUBSCRIBE_KEYWORDS = [
    "unsubscribe",
    "manage preferences",
    "email preferences",
    "stop receiving",
    "opt out",
]


JOB_EMAIL_THRESHOLD = 3
URL_PATTERN = re.compile(r"https?://\S+")



@dataclass
class IMAPSettings:
    host: str
    port: int
    username: str
    password: str
    provider: EmailProvider
    use_ssl: bool = True


@dataclass
class OutlookSettings:
    application_id: str
    client_secret: str
    tenant_id: str
    authority: str
    provider: EmailProvider


@dataclass
class JobDetectionResult:
    is_job: bool = False
    score: int = 0
    is_rejection: bool = False
    is_interview: bool = False
    is_job_alert: bool = False
    is_application_confirmation: bool = False
    reasons: list[str] = field(default_factory=list)


@dataclass
class ExtractJob:
    title: str | None
    company: str | None
    location: str | None
    salary: str | None
    apply_url: str | None


@dataclass
class ExtractedValue:
    value: str | None
    line_index: int | None
    confidence: float = 1.0






def looks_like_job_title(text: str) -> str | None:
    if not text: 
        return False

    text = text.strip().lower()

    if text in {"remote", "hybrid"}:
        return False

    if text.startswith("salary"):
        return False

    if text.startswith("apply"):
        return False

    if text.startswith("http"):
        return False

    return True


def clean_extracted_job_title(text: str) -> str | None:
    if not text: 
        return ""

    words = text.split()
    midpoint = len(words) // 2

    left = words[:midpoint]
    right = words[midpoint:]

    if left == right:
        return " ".join(left)
    
    return text.strip()




def looks_like_company_name(text: str) -> str | None:
    if not text: 
        return False

    text = text.strip().lower()

    if text in {"remote", "hybrid"}:
        return False

    if text.startswith("salary"):
        return False

    if text.startswith("apply"):
        return False

    if text.startswith("http"):
        return False

    return True
  


def looks_like_location_name(text: str) -> str | None:
    if not text: 
        return False

    text = text.strip().lower()

    if text.startswith("salary"):
        return False

    if text.startswith("apply"):
        return False

    if text.startswith("http"):
        return False
    

    return True


def looks_like_salary(text: str) -> str | None:
    if not text: 
        return False

    text = text.strip().lower()


    return any(keyword in text for keyword in SALARY_KEYWORDS)


def get_clean_lines(text: str) -> list[str]:
    return [
        " ".join(line.split())
        for line in text.splitlines()
        if line.strip()
    ]





