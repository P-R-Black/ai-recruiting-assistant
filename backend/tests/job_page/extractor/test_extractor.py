
import pytest
from app.job_page.extractor import extract_job_description

import app.job_page.extractor as job_page_extractor

from app.job_page.schema import (
    JobDescriptionResponse,
    JobPageResponse,
)



def test_extract_job_description_from_json_ld():
    html = """
    <html>
        <head>
            <script type="application/ld+json">
            {
                "@type": "JobPosting",
                "title": "Frontend Developer",
                "description": "<p>We are looking for a <strong>Frontend Developer</strong>.</p>"
            }
            </script>
        </head>
    </html>
    """

    result = extract_job_description(html)

    assert result.description == "We are looking for a Frontend Developer."
    assert result.extraction_method == "json_ld"


def test_extract_job_description_from_json_ld_graph():
    html = """
    <script type="application/ld+json">
    {
        "@graph": [
            {
                "@type": "Organization",
                "name": "Example Company"
            },
            {
                "@type": "JobPosting",
                "description": "<p>Build great software.</p>"
            }
        ]
    }
    </script>
    """

    result = extract_job_description(html)

    assert result.description == "Build great software."
    assert result.extraction_method == "json_ld"


def test_extract_job_description_from_html_fallback():
    html = """
    <html>
        <body>
            <div id="jobDescriptionText">
                <p>We are hiring a developer.</p>
                <p>Experience with Python is required.</p>
            </div>
        </body>
    </html>
    """

    result = extract_job_description(html)

    assert "We are hiring a developer." in result.description
    assert "Experience with Python is required." in result.description
    assert result.extraction_method == "html"


def test_extract_job_description_falls_back_when_json_ld_is_malformed():
    html = """
    <html>
        <head>
            <script type="application/ld+json">
                { invalid json
            </script>
        </head>
        <body>
            <div class="job-description">
                <p>Job description from HTML.</p>
            </div>
        </body>
    </html>
    """

    result = extract_job_description(html)

    assert result.description == "Job description from HTML."
    assert result.extraction_method == "html"


def test_extract_job_description_returns_empty_response_when_not_found():
    html = """
    <html>
        <body>
            <h1>Frontend Developer</h1>
            <p>Example Company</p>
        </body>
    </html>
    """

    result = extract_job_description(html)

    assert result.description is None
    assert result.extraction_method is None


def test_extract_job_description_removes_script_and_style_content():
    html = """
    <div id="jobDescriptionText">
        <p>Build frontend applications.</p>
        <script>alert("unwanted content")</script>
        <style>.hidden { display: none; }</style>
    </div>
    """

    result = extract_job_description(html)

    assert result.description == "Build frontend applications."
    assert "alert" not in result.description
    assert "display: none" not in result.description


def test_extract_job_description_from_json_ld_schema_url():
    html = """
    <script type="application/ld+json">
    {
        "@type": "https://schema.org/JobPosting",
        "description": "<p>Develop scalable applications.</p>"
    }
    </script>
    """

    result = extract_job_description(html)

    assert result.description == "Develop scalable applications."
    assert result.extraction_method == "json_ld"


def mock_glassdoor_extraction(monkeypatch):
    def fake_extract(self, page: JobPageResponse):
        return page.model_copy(
            update={
                "description": "Glassdoor job description",
                "responsibilities": ["Build software"],
                "required_qualifications": ["Python experience"],
                "preferred_qualifications": ["AWS experience"],
                "extraction_method": "glassdoor",
            }
        )

    monkeypatch.setattr(
        job_page_extractor.GlassdoorJobPageExtractor,
        "extract",
        fake_extract,
    )


def test_extract_job_description_uses_glassdoor_extractor(
    monkeypatch,
):
    mock_glassdoor_extraction(monkeypatch)

    result = job_page_extractor.extract_job_description(
        html="<html><body>Job posting</body></html>",
        url="https://www.glassdoor.com/job-listing/example",
    )

    assert result == JobDescriptionResponse(
        description="Glassdoor job description",
        responsibilities=["Build software"],
        required_qualifications=["Python experience"],
        preferred_qualifications=["AWS experience"],
        extraction_method="glassdoor",
    )


def test_extract_job_description_uses_glassdoor_extractor_for_subdomain(
    monkeypatch,
):
    mock_glassdoor_extraction(monkeypatch)

    result = job_page_extractor.extract_job_description(
        html="<html><body>Job posting</body></html>",
        url="https://jobs.glassdoor.com/job-listing/example",
    )

    assert result.extraction_method == "glassdoor"
    assert result.description == "Glassdoor job description"


def test_extract_job_description_uses_generic_extraction_for_unknown_domain(
    monkeypatch,
):
    monkeypatch.setattr(
        job_page_extractor,
        "extract_json_ld_description",
        lambda soup: "Generic job description",
    )

    monkeypatch.setattr(
        job_page_extractor,
        "extract_html_description",
        lambda soup: None,
    )

    result = job_page_extractor.extract_job_description(
        html="<html><body>Job posting</body></html>",
        url="https://jobs.example.com/listing/123",
    )

    assert result == JobDescriptionResponse(
        description="Generic job description",
        extraction_method="json_ld",
    )

def test_extract_job_description_uses_generic_extraction_without_url(
    monkeypatch,
):
    monkeypatch.setattr(
        job_page_extractor,
        "extract_json_ld_description",
        lambda soup: "Generic job description",
    )

    monkeypatch.setattr(
        job_page_extractor,
        "extract_html_description",
        lambda soup: None,
    )

    result = job_page_extractor.extract_job_description(
        html="<html><body>Job posting</body></html>",
    )

    assert result == JobDescriptionResponse(
        description="Generic job description",
        extraction_method="json_ld",
    )

def test_extract_job_description_returns_empty_response_for_empty_html(
    monkeypatch,
):
    def unexpected_call(*args, **kwargs):
        pytest.fail("Extraction should not be called for empty HTML")

    monkeypatch.setattr(
        job_page_extractor,
        "get_job_page_extractor",
        unexpected_call,
    )

    monkeypatch.setattr(
        job_page_extractor,
        "extract_json_ld_description",
        unexpected_call,
    )

    monkeypatch.setattr(
        job_page_extractor,
        "extract_html_description",
        unexpected_call,
    )

    result = job_page_extractor.extract_job_description(
        html="   ",
        url="https://www.glassdoor.com/job-listing/example",
    )

    assert result == JobDescriptionResponse()


def test_extract_job_description_uses_generic_extraction_for_indeed_url():
    html = """
    <html>
        <head>
            <script type="application/ld+json">
            {
                "@type": "JobPosting",
                "title": "Backend Developer",
                "description": "<p>Build and maintain backend services.</p>"
            }
            </script>
        </head>
    </html>
    """

    url = "https://www.indeed.com/viewjob?jk=example123"

    # Indeed does not currently have a specialized page extractor.
    assert job_page_extractor.get_job_page_extractor(url) is None

    result = job_page_extractor.extract_job_description(
        html=html,
        url=url,
    )

    print("DEBUG result", result)

    assert result.description == "Build and maintain backend services."
    assert result.extraction_method == "json_ld"



def test_extract_job_description_falls_back_when_glassdoor_extractor_finds_no_description(
    monkeypatch,
):
    def fake_extract(self, page: JobPageResponse):
        return page.model_copy(
            update={
                "description": None,
                "extraction_method": None,
            }
        )

    monkeypatch.setattr(
        job_page_extractor.GlassdoorJobPageExtractor,
        "extract",
        fake_extract,
    )

    monkeypatch.setattr(
        job_page_extractor,
        "extract_json_ld_description",
        lambda soup: "Generic JSON-LD description",
    )

    result = job_page_extractor.extract_job_description(
        html="<html><body>Job posting</body></html>",
        url="https://www.glassdoor.com/job-listing/example",
    )

    assert result.description == "Generic JSON-LD description"
    assert result.extraction_method == "json_ld"
