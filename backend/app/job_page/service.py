from app.job_page.extractor import extract_job_description
from app.job_page.retriever import retrieve_job_page
from app.job_page.schema import JobPageProcessingResponse


def process_job_page(url: str) -> JobPageProcessingResponse:
    """
    Retrieve a job listing page and extract its description.

    Raises:
        ValueError: If the URL is invalid or unsafe.
        httpx.HTTPError: If the page cannot be retrieved.
    """
    page = retrieve_job_page(url)
    extracted_description = extract_job_description(html=page.html, url=page.final_url)

    return JobPageProcessingResponse(
        requested_url=page.requested_url,
        final_url=page.final_url,
        status_code=page.status_code,
        description=extracted_description.description,
        responsibilities=extracted_description.responsibilities,
        required_qualifications=(
            extracted_description.required_qualifications
        ),
        preferred_qualifications=(
            extracted_description.preferred_qualifications
        ),
        extraction_method=extracted_description.extraction_method,
    )