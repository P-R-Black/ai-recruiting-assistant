from email.utils import parseaddr

from app.mail.normalizer.base import ParsedEmail

KNOWN_JOB_BOARDS: dict[str, str] = {
    "glassdoor.com": "glassdoor",
    "linkedin.com": "linkedin",
    "indeed.com": "indeed",
    "match.indeed.com":"indeed",
    # Indeed sometimes sends from this domain instead
    "indeedemail.com": "indeed",      
    "ziprecruiter.com": "ziprecruiter",

}

KNOWN_JOB_BOARD_SENDERS: dict[str, str] = {
    "noreply@glassdoor.com": "glassdoor",
    "alerts@ziprecruiter.com": "ziprecruiter",
    "dice@connect.dice.com": "dice",
    "donotreply@match.indeed.com": "indeed",
    "jobalerts-noreply@linkedin.com": "linkedin",
    "jobs-noreply@linkedin.com": "linkedin",
}

KNOWN_JOB_BOARD_EMAILS = [
    "noreply@glassdoor.com", 
    "alerts@ziprecruiter.com", 
    "dice@connect.dice.com", 
    "donotreply@match.indeed.com",
    "jobalerts-noreply@linkedin.com",

    "notifications-noreply@linkedin.com", # <- no jobs
    "messages-noreply@linkedin.com", # <- no jobs
    "updates-noreply@linkedin.com", # <- no jobs
    "editors-noreply@linkedin.com", # <- no jobs
]

def identify_job_board(sender: str | None) -> str | None:
    """
    Resolve a sender address to a known job board name, or None if
    the sender isn't recognized. Shared by both the filter step and the
    provider/source-determination step, so domain parsing only lives once.
    """

    if not sender:
        return None

    _, address = parseaddr(sender)
    return KNOWN_JOB_BOARD_SENDERS.get(address.strip().lower())


def is_job_board_email(email: ParsedEmail) -> bool:
    return identify_job_board(email.sender) is not None