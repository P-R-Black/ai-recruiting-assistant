import email
from email.utils import parseaddr

from bs4 import BeautifulSoup


from app.mail.normalizer.base import NormalizedJob, BaseEmailNormalizer, ParsedEmail
from app.mail.mail_services.mime_parser import get_html_from_raw_email

from app.mail.connectors.imap_connector import connect_imap, fetch_message, search_messages
from tests.integration.test_icloud_connection import icloud_connection



class GlassdoorNormalizer(BaseEmailNormalizer):
    def normalize(
            self,
            email: ParsedEmail,
    ) -> list[NormalizedJob]:
        if email.html_body is None:
            return []
        
        return extract_glassdoor_jobs(email.html_body)



def extract_glassdoor_jobs(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    for link in soup.find_all("a", href=True):
        if "jobListing.htm" not in link["href"]:
            continue  # skip "related jobs" links, footer links, etc.

        p_tags = link.find_all("p")
        if not p_tags:
            continue

        title = p_tags[0].get_text(strip=True)
        location = p_tags[1].get_text(strip=True) if len(p_tags) > 1 else None
        salary = p_tags[2].get_text(strip=True) if len(p_tags) > 2 else None

        company_span = link.find("span")
        company = company_span.get_text(strip=True) if company_span else None

        jobs.append(
            NormalizedJob(
                title=title,
                company=company,
                location=location,
                salary=salary,
                job_url=link["href"],
            )
        )
    return jobs


def matches_keywords(title: str, keywords: list[str]) -> bool:
    title_lower = title.lower()
    return any(kw.lower() in title_lower for kw in keywords)


# Map sender domain -> board identifier
KNOWN_JOB_BOARDS = {
    "glassdoor.com": "glassdoor",
    "linkedin.com": "linkedin",
    "indeed.com": "indeed",
    "match.indeed.com":"indeed",
    "indeedemail.com": "indeed",       # Indeed sometimes sends from this domain instead
    "ziprecruiter.com": "ziprecruiter",

}


def identify_job_board(raw_bytes: bytes) -> str | None:
    """Identify which job board sent this email, based on the From header."""
    msg = email.message_from_bytes(raw_bytes)
    from_header = msg.get("From", "")

    _, sender_email = parseaddr(from_header)  # "Glassdoor Jobs <noreply@glassdoor.com>" -> "noreply@glassdoor.com"
    if "@" not in sender_email:
        return None

    domain = sender_email.split("@")[-1].lower()
    return KNOWN_JOB_BOARDS.get(domain)


# Registry of board_id -> parser function
JOB_BOARD_PARSERS = {
    "glassdoor": extract_glassdoor_jobs,
    # "linkedin": extract_linkedin_jobs,     # add these as you build them out
    # "indeed": extract_indeed_jobs,
    # "ziprecruiter": extract_ziprecruiter_jobs,
}


def process_job_email(raw_bytes: bytes, keywords: list[str]) -> list[dict]:
    board = identify_job_board(raw_bytes)
    if board is None:
        return []  # not a job board we recognize — skip it

    parser = JOB_BOARD_PARSERS.get(board)
    if parser is None:
        return []  # we know the board, but haven't written its parser yet

    html = get_html_from_raw_email(raw_bytes)
    if html is None:
        return []

    jobs = parser(html)
    for j in jobs:
        j["source"] = board  # tag it, useful for your SQLAlchemy model later

    return [j for j in jobs if matches_keywords(j["title"], keywords)]



"""
Glassdoor Example, Multiple Jobs
[
NormalizedJob(
title='Junior Software Developer', 
company='dicedemo', 
location='Boston, AL', 
salary='Easy Apply', 
job_url='https://www.glassdoor.com/partner/jobListing.htm?pos=101&ao=...'), 
NormalizedJob(
title='Part-Time Angular / TypeScript UI Developer', 
company='600 West LLC', 
location='United States', 
salary='$50 - $60(Employer est.)', 
job_url='https://www.glassdoor.com/partner/jobListing.htm?pos=102&ao=...'), 
NormalizedJob(
title='Junior Software Developer – Web & Mobile Application', 
company='', 
location='Houston, TX', 
salary='$18(Employer est.)', 
job_url='https://www.glassdoor.com/partner/jobListing.htm?pos=103&ao=1136043&s=...'), 
NormalizedJob(
title='Web Developer', 
company='', 
location='Phoenix, AZ', 
salary='$53K - $78K(Glassdoor est.)', 
job_url='https://www.glassdoor.com/partner/jobListing.htm?pos=104&ao=...')
], 
"""