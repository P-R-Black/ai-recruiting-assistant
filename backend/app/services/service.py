from dataclasses import dataclass, field
from typing import Any

from app.constants.keyword_list import (
    SALARY_KEYWORDS, 
    RECRUITER_TITLE_KEYWORDS, 
    NON_PERSON_WORDS,
    APPLY_URL_KEYWORDS,
    NON_APPLY_URL_KEYWORDS
    )
from app.mail.models import EmailProvider, WorkLocation


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
    remote: bool = False
    employment_type: str | None = None
    recruiter: str | None = None
    work_location: WorkLocation = WorkLocation.UNKNOWN


@dataclass
class ExtractedValue:
    line_index: int | None
    value: Any = None # str | None
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



def looks_like_recruiter_title(text: str) -> bool:
    if not text: 
            return False
    
    text = text.lower()

    return any(keyword in text for keyword in RECRUITER_TITLE_KEYWORDS)


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



def looks_like_person_name(text: str) -> bool:
    words =  text.strip().split()

    if not (2 <= len(words) <= 4):
        return False

    for word in words:
        if not word[0].isupper():
            return False

        if any(char.isdigit() for char in word):
            return False

        if word.lower() in NON_PERSON_WORDS:
            return False

    return True


def calculate_apply_url_score(url: str) -> int:
    score = 0

    for word in APPLY_URL_KEYWORDS:
        if word in url.lower():
            score += 2

    for word in NON_APPLY_URL_KEYWORDS:
        if word in url.lower():
            score -= 2

    return score    


def get_clean_lines(text: str) -> list[str]:
    return [
        " ".join(line.split())
        for line in text.splitlines()
        if line.strip()
    ]





