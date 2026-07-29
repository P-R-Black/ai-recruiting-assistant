from app.mail import crud
from app.mail.schemas import EmailCreate, EmailProvider
from app.mail.models import Email
from app.mail.service import ExtractedValue, ExtractJob
from app.mail.service import (
    get_clean_lines, clean_extracted_job_title, looks_like_company_name, looks_like_location_name,
    looks_like_salary)


from app.mail.service import URL_PATTERN

def extract_job_information(email: EmailCreate) -> ExtractJob:
    searchable = " ".join([
        email.subject or "",
        email.raw_body,
    ])

    title = extract_job_title(searchable)
    company = extract_company_name(searchable, title)
    location = extract_location(searchable, company)
    salary = extract_salary(searchable, location)
    apply_url = extract_apply_url(email)

    return ExtractJob(
        title=title.value,
        company=company.value,
        location=location.value,
        salary=salary.value,
        apply_url=apply_url,
        
    )

    

def extract_apply_url(email: EmailCreate) -> str | None:
    
    match = URL_PATTERN.search(email.raw_body)
    if match:
        return match.group(0)
    return None


def extract_job_title(text: str) -> str | None:
    lines = get_clean_lines(text)
    for index, line in enumerate(lines):
        if looks_like_job_title(line):
            title = clean_extracted_job_title(line)

            return ExtractedValue(
                value=title,
                line_index=index,
                confidence=1.0
            )

    return ExtractedValue(
        value=None,
        line_index=None,
        confidence=0.0
    )


def looks_like_job_title(text: str) -> str | None:
    if not text: return False

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


def extract_company_name(text: str, title: str) -> str | None:
    lines = get_clean_lines(text)
   
    if title.line_index is None:
        return ExtractedValue(None, None, 0.0)
   
    for index in range(title.line_index + 1, len(lines)):
        line = lines[index]
        if looks_like_company_name(line):
            return ExtractedValue(value=line, line_index=index, confidence=1.0)
       
    return ExtractedValue(value=None, line_index=None, confidence=0.0)


def extract_location(text: str, company: ExtractedValue) -> ExtractedValue:
    lines = get_clean_lines(text)
   
    if company.line_index is None:
        return ExtractedValue(None, None, 0.0)
   
    for index in range(company.line_index + 1, len(lines)):
        line = lines[index]
        if looks_like_location_name(line):
            return ExtractedValue(value=line, line_index=index, confidence=1.0)
       
    return ExtractedValue(value=None, line_index=None, confidence=0.0)


def extract_salary(text: str, location: str) -> str | None:
    lines = get_clean_lines(text)
   
    if location.line_index is None:
        return ExtractedValue(None, None, 0.0)
   
    for index in range(location.line_index + 1, len(lines)):
        line = lines[index]
        if looks_like_salary(line):
            return ExtractedValue(value=line, line_index=index, confidence=1.0)
       
    return ExtractedValue(value=None, line_index=None, confidence=0.0)