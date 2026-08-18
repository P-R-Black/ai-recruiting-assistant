from urllib.parse import urlparse

from app.constants.keyword_list import (
    CONTRACT_KEYWORDS,
    FREELANCE_KEYWORDS,
    FULL_TIME_KEYWORDS,
    HYBRID_KEYWORDS,
    INTERNSHIP_KEYWORDS,
    JOB_SITE_PREFIXES,
    ONSITE_KEYWORDS,
    PART_TIME_KEYWORDS,
    REMOTE_KEYWORDS,
    TEMPORARY_KEYWORDS,
    URL_PATTERN,
)
from app.mail.mail_services.service import (
    ExtractedValue,
    ExtractJob,
    calculate_apply_url_score,
    clean_extracted_job_title,
    get_clean_lines,
    looks_like_company_name,
    looks_like_job_title,
    looks_like_location_name,
    looks_like_person_name,
    looks_like_recruiter_title,
    looks_like_salary,
)
from app.mail.models import EmploymentType, WorkLocation
from app.mail.schemas import EmailCreate


def extract_job_information(email: EmailCreate) -> ExtractJob:
    searchable = " ".join([
        email.subject or "",
        email.raw_body,
    ])

    title = extract_job_title(searchable)
    company = extract_company_name(searchable, title)
    location = extract_location(searchable, company)

    salary = extract_salary(searchable, location)
    employment_type = extract_employment_type(searchable)
    recruiter = extract_recruiter_name(searchable)
    work_location = extract_work_location(searchable)
    apply_url = extract_application_url(email)

    return ExtractJob(
        title=title.value,
        company=company.value,
        location=location.value,
        salary=salary.value,
        apply_url=apply_url.value,
        employment_type=employment_type.value,
        recruiter=recruiter.value,
        work_location=work_location.value,
        
    )

    

def extract_apply_url(email: EmailCreate) -> str | None:
    
    match = URL_PATTERN.search(email.raw_body)
    if match:
        return match.group(0)
    return None



def extract_job_title(text: str) -> ExtractedValue:
    lines = get_clean_lines(text)
    for index, line in enumerate(lines):
        if not looks_like_job_title(line):
            continue

        title = clean_extracted_job_title(line)

        confidence = 0.7

        if index == 0:
            confidence += 0.2

        if len(title.split()) <= 6:
            confidence += 0.1

        return ExtractedValue(
            value=title,
            line_index=index,
            confidence=min(confidence, 1.0),
        )

    return ExtractedValue(None, None, 0.0)



def extract_company_name(text: str, title: str) -> ExtractedValue:
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



def extract_work_location(text: str) -> ExtractedValue:

    lines = get_clean_lines(text)

    for index, line, in enumerate(lines):
        searchable = line.lower()

        if any(word in searchable for word in REMOTE_KEYWORDS):
            return ExtractedValue(
                value=WorkLocation.REMOTE,
                line_index=index,
                confidence=1.0,
            )

        if any(word in searchable for word in HYBRID_KEYWORDS):
            return ExtractedValue(
                value=WorkLocation.HYBRID,
                line_index=index,
                confidence=1.0,
            )

        if any(word in searchable for word in ONSITE_KEYWORDS):
            return ExtractedValue(
                value=WorkLocation.ONSITE,
                line_index=index,
                confidence=1.0,
            )

    return ExtractedValue(
        value=WorkLocation.UNKNOWN,
        line_index=None,
        confidence=0.0,
    )


def extract_salary(text: str, location: str) -> ExtractedValue:
    lines = get_clean_lines(text)
   
    if location.line_index is None:
        return ExtractedValue(None, None, 0.0)
   
    for index in range(location.line_index + 1, len(lines)):
        line = lines[index]
        if looks_like_salary(line):
            return ExtractedValue(value=line, line_index=index, confidence=1.0)
       
    return ExtractedValue(value=None, line_index=None, confidence=0.0)



def extract_employment_type(text: str) -> ExtractedValue:
    searchable = text.lower()

    if any(k in searchable for k in FULL_TIME_KEYWORDS):
        return ExtractedValue(
            value=EmploymentType.FULL_TIME,
            line_index=None,
            confidence=1.0,
        )

    if any(k in searchable for k in PART_TIME_KEYWORDS):
        return ExtractedValue(
            value=EmploymentType.PART_TIME,
            line_index=None,
            confidence=1.0,
        )

    if any(k in searchable for k in CONTRACT_KEYWORDS):
        return ExtractedValue(
            value=EmploymentType.CONTRACT,
            line_index=None,
            confidence=1.0,
        )

    if any(k in searchable for k in TEMPORARY_KEYWORDS):
        return ExtractedValue(
            value=EmploymentType.TEMPORARY,
            line_index=None,
            confidence=1.0,
        )

    if any(k in searchable for k in INTERNSHIP_KEYWORDS):
        return ExtractedValue(
            value=EmploymentType.INTERN,
            line_index=None,
            confidence=1.0,
        )

    if any(k in searchable for k in FREELANCE_KEYWORDS):
        return ExtractedValue(
            value=EmploymentType.FREELANCE,
            line_index=None,
            confidence=1.0,
        )

    return ExtractedValue(
        value=EmploymentType.UNKNOWN,
        line_index=None,
        confidence=0.0,
    )


def extract_recruiter_name(text: str) -> ExtractedValue:
    lines = get_clean_lines(text)

    for index in range(len(lines) -1, -1, -1):
        print('index', index, 'lines[index]', lines[index])
        if looks_like_recruiter_title(lines[index]):
            if index > 0:
                candidate = lines[index - 1]

                if looks_like_person_name(candidate):
                    return ExtractedValue(
                        value=candidate,
                        line_index=index - 1,
                        confidence=1.0
                    )

    return ExtractedValue(value=None, line_index=None, confidence=0.0)


def extract_company_website(
        company: ExtractedValue,
        apply_url: str | None,
    ) -> ExtractedValue:
    if not apply_url:
        return ExtractedValue(value=None, line_index=None, confidence=0.0)
    
    hostname = urlparse(apply_url)

    parts = hostname.netloc.split(".")

    if parts[0] in JOB_SITE_PREFIXES:
        parts = parts[1:]

    return ExtractedValue(
        value=".".join(parts),
        line_index=None,
        confidence=0.95,
    )


def extract_application_url(email: EmailCreate) -> ExtractedValue:

    matches = URL_PATTERN.findall(email.raw_body)

    best_score = float("-inf")
    best_url = None
    for match in matches:
        curr_link_score = calculate_apply_url_score(match)
        if curr_link_score > best_score:
            best_score = curr_link_score
            best_url = match


    return ExtractedValue(value=best_url, line_index=None, confidence=0.95)
