
import json
import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from app.job_page.parsers.base import BaseJobPageExtractor
from app.job_page.parsers.glassdoor import GlassdoorJobPageExtractor
from app.job_page.parsers.linkedin import LinkedInJobPageExtractor
from app.job_page.parsers.ziprecruiter import ZipRecruiterJobPageExtractor
from app.job_page.schema import JobDescriptionResponse, JobPageResponse

JOB_DESCRIPTION_SELECTORS = [
    '[itemprop="description"]',
    "#jobDescriptionText",
    "#jobDescription",
    ".jobDescriptionContent",
    ".job-description",
    ".jobDescription",
    ".description__text",
    '[class*="jobDescription"]',
    '[class*="job-description"]',
]


def clean_description(description: str) -> str | None:
    """
    Convert an HTML or plain-text job description into clean text.
    """
    if not description or not description.strip():
        return None

    soup = BeautifulSoup(description, "html.parser")

    # Remove elements that don't contribute to the description.
    for element in soup(["script", "style", "noscript", "svg"]):
        element.decompose()

    # Preserve basic block formatting and line breaks.
    for element in soup.find_all("br"):
        element.replace_with("\n")

    block_elements = soup.find_all(
        ["p", "div", "li", "h1", "h2", "h3", "h4", "ul", "ol"]
    )

    for element in block_elements:
        element.insert_before("\n")
        element.insert_after("\n")

    text = soup.get_text(separator="", strip=False)

    # Normalize whitespace without removing paragraph boundaries.
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    text = text.strip()

    return text or None


def find_job_posting(data):
    """
    Recursively find JobPosting objects in JSON-LD data.
    Supports dictionaries, lists, and @graph structures.
    """
    if isinstance(data, dict):
        job_type = data.get("@type")

        if isinstance(job_type, str):
            job_types = [job_type]
        elif isinstance(job_type, list):
            job_types = job_type
        else:
            job_types = []

        is_job_posting = any(
            isinstance(job_type, str)
            and job_type.rstrip("/").rsplit("/", 1)[-1].rsplit("#", 1)[-1]
            == "JobPosting"
            for job_type in job_types
        )

        if is_job_posting:
            yield data

        for value in data.values():
            yield from find_job_posting(value)

    elif isinstance(data, list):
        for item in data:
            yield from find_job_posting(item)


def extract_json_ld_description(soup: BeautifulSoup) -> str | None:
    """
    Extract a job description from JSON-LD JobPosting data.
    """
    scripts = soup.find_all(
        "script",
        attrs={"type": "application/ld+json"},
    )

    for script in scripts:
        if not script.string and not script.get_text(strip=True):
            continue

        try:
            data = json.loads(script.string or script.get_text())
        except (json.JSONDecodeError, TypeError):
            continue

        for job_posting in find_job_posting(data):
            description = job_posting.get("description")

            if not isinstance(description, str):
                continue

            cleaned_description = clean_description(description)

            if cleaned_description:
                return cleaned_description

    return None


def extract_html_description(soup: BeautifulSoup) -> str | None:
    """
    Extract a job description from common HTML description containers.
    """
    for selector in JOB_DESCRIPTION_SELECTORS:
        element = soup.select_one(selector)

        if element is None:
            continue

        cleaned_description = clean_description(
            str(element)
        )

        if cleaned_description:
            return cleaned_description

    return None


def extract_job_description(
        html: str, 
        url: str | None = None, ) -> JobDescriptionResponse:
    """
    Extract a job description from retrieved job-page HTML.

    JSON-LD is preferred. Common HTML description containers
    are used as a fall back.
    """
    if not html or not html.strip():
        return JobDescriptionResponse()

    if url:
        extractor = get_job_page_extractor(url)

        if extractor:
            page = JobPageResponse(
                requested_url=url,
                final_url=url,
                status_code=200,
                html=html,
            )

            extracted_page = extractor.extract(page)

            if extracted_page.description:
                return JobDescriptionResponse(
                    description=extracted_page.description,
                    responsibilities=extracted_page.responsibilities,
                    required_qualifications=(
                        extracted_page.required_qualifications
                    ),
                    preferred_qualifications=(
                        extracted_page.preferred_qualifications
                    ),
                    extraction_method=extracted_page.extraction_method,
                )
        
    soup = BeautifulSoup(html, "html.parser")

    description = extract_json_ld_description(soup)

    if description:
        return JobDescriptionResponse(
            description=description,
            extraction_method="json_ld",
        )

    description = extract_html_description(soup)

    if description:
        return JobDescriptionResponse(
            description=description,
            extraction_method="html",
        )

    return JobDescriptionResponse()


# --------------------------------------------------------------------------- #
# Dispatch by domain (same idea as the email normalizers)
# --------------------------------------------------------------------------- #
 
_EXTRACTORS: dict[str, type[BaseJobPageExtractor]] = {
    "glassdoor.com": GlassdoorJobPageExtractor,
    "linkedin.com": LinkedInJobPageExtractor,
    "ziprecruiter.com": ZipRecruiterJobPageExtractor,
}
 
 
 
def get_job_page_extractor(url: str) -> BaseJobPageExtractor | None:
    host = (urlparse(url).hostname or "").lower()
    for domain, cls in _EXTRACTORS.items():
        if host == domain or host.endswith("." + domain):
            return cls()
    return None