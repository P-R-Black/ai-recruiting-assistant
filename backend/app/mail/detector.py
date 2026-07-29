from email import policy
from email.utils import parsedate_to_datetime, parseaddr

from app.mail import crud
from app.mail.schemas import EmailCreate
from app.mail.models import Email
from app.mail.service import JobDetectionResult
from app.mail.service import (
    JOB_EMAIL_THRESHOLD, JOB_KEYWORDS, FREE_EMAIL_PROVIDERS, JOB_BOARD_DOMAINS, 
    REJECTION_KEYWORDS, UNSUBSCRIBE_KEYWORDS, RECRUITER_KEYWORDS
    )




def detect_job_email(email: EmailCreate) -> JobDetectionResult:
    searchable = " ".join([
        email.subject or "",
        email.sender,
        email.raw_body,
    ])

    score = 0
    reasons = []

    keyword_score = calculate_job_keyword_score(searchable)
    score += keyword_score

    if keyword_score:
        reasons.append(f"Job keywords (+{keyword_score})")
    
    sender_score = calculate_job_board_sender_score(email.sender)
    score += sender_score

    if sender_score:
        reasons.append(f"Job board sender (+{sender_score})")
    
    recruiter_score = calculate_recruiter_sender_score(email.sender)
    score += recruiter_score

    if recruiter_score:
        reasons.append(f"Recruiter sender (+{recruiter_score})")

    result = JobDetectionResult(
        is_job=score >= JOB_EMAIL_THRESHOLD,
        score=score,
        reasons=reasons,
    )

    rejection_score = calculate_rejection_score(searchable)
    if rejection_score:
        result.is_rejection = True
        result.reasons.append("Rejection language detected")

    unsubscribe_score = calculate_unsubscribe_score(searchable)
    if unsubscribe_score:
        result.unsubscribe_score = True
        result.reasons.append("Newsletter footer detected, not job related")

    result.is_rejection = rejection_score  >= 1
    result.is_job_alert = unsubscribe_score  >= 1

    # result.is_rejection = calculate_rejection_score(searchable)  >= 1
    # result.is_job_alert = calculate_unsubscribe_score(searchable)  >= 1
    
    return result

def calculate_job_keyword_score(text: str) -> bool:
    text = text.lower()
    return sum(keyword in text for keyword in JOB_KEYWORDS)


def calculate_recruiter_sender_score(sender: str) -> int:
    """
    Returns a score indicating how likely the sender is a recruiter
    """
    score = 0

    _, email = parseaddr(sender)
    if not email or "@" not in email:
        return score
    
    local, domain = email.lower().split("@", 1)

    # recruiter keywords in the mailbox name
    if any(keyword in local for keyword in RECRUITER_KEYWORDS):
        score += 2

    # recruiter keywords in the domain
    if any(keyword in domain for keyword in RECRUITER_KEYWORDS):
        score += 2
    
    # company email addresses are generally more trustworthy
    if domain not in FREE_EMAIL_PROVIDERS:
        score += 1
    
    return score


def calculate_job_board_sender_score(sender: str) -> int:
    """
    Returns a score indicating how likely the sender
    is a job board.
    """

    _, email = parseaddr(sender)

    if not email or "@" not in email:
        return 0
    
    _, domain = email.lower().split("@", 1)

    
    # recruiter keywords in the domain
    for job_board, score in JOB_BOARD_DOMAINS.items():
        if domain == job_board or domain.endswith("." + job_board):
            return score
    
    return 0


def calculate_unsubscribe_score(text: str) -> None:
    text = text.lower()
    return sum(keyword in text for keyword in UNSUBSCRIBE_KEYWORDS)

def calculate_rejection_score(text: str) -> int:
    text = text.lower()

    return sum(keyword in text for keyword in REJECTION_KEYWORDS)


