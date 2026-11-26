import json
from pathlib import Path
import pytest
from bs4 import BeautifulSoup

from app.job_page.retriever import retrieve_job_page
from app.job_page.parsers.linkedin import LinkedInJobPageExtractor
# from app.job_page.schema import JobPageResponse
from app.job_page.parsers.glassdoor import JobPageResponse

from app.job_page.parsers.helpers.common import (
    find_job_posting, 
    parse_description_html, 
    parse_description_text,
    score_parsed,
    build_candidates,
    parse_description_text,
    parse_description_html,
    ParsedDescription,
    )
from app.job_page.schema import (
    JobPageProcessingResponse,
    RetrievedJobPage,
)
from app.job_page.service import process_job_page


import app.job_page.parsers.helpers.common as common
from app.job_page import service as job_page_service


linkedin_one = "https://www.linkedin.com/jobs/view/4486537867/?trk=eml-email_jobs_qualification_board-JOBS_POSTING_SECTION_1-0-job_card_0_jobid_4486537867_fmid_9r04q9~mwtlmtuj~bo&refId=%2BI6JmNJx2F7h35ILpTGYBg%3D%3D&trackingId=3Dw6Qca%2ByDSsfHxUn0VbTA%3D%3D"
linkedin_two = "https://www.linkedin.com/jobs/search-results/?currentJobId=4458531029&eBP=CwEAAAGiDduyN2em00pXscUA8Ee240m9CL-pQiDRWtwLOOSR2SmdrfR2FOmujzweuFWeDdv4vhc1IIeF0V2rEMk4iPI-a8wBnh4a80ktWzUqvOXAuJHOCru6urvOx2P0wQcoqDaSW59DJPch9gdEXbge2ZF-G5LPFdsAs5me6ZJTX74A9GOC-s7X36IrxOAAhk4BiVnpW3x10BOwQ3eWGF7o-S9fHKV4J-e8cpsworQGhdLXwvGDjphl54mqz5cy7qdcKFjqLrrDgMfHB-93gk6HtDbmoIP4ZgmSSBosEy91dVk4GzK-rH4EAXVT_Wg9nOjeIYL-RxiNFFItlY-FL9IjxsiTPJGqSZincH1bN6AHvRrHdhxvTv31GL9SRjv94s9ZcAb8wMN_LHoDKtGkx4esO8lzZeU&trackingId=eM8hb3H6qtaGHCCrVYAHug%3D%3D&keywords=Web%20Developer%2C%20Junior%20%28Active%20Secret%20Clearance%20or%20Able%20to%20Obtain%29&origin=JOB_DETAILS_SIMILAR_JOBS_CARD&originToLandingJobPostings=4458531029&geoId=103644278"
linkedin_three = "https://www.linkedin.com/jobs/view/4475293639/?alternateChannel=search&eBP=CwEAAAGiDfvoQJmWJkqSTsbexutozDmEFpX8vXsQ6cmUljMxJNXNPev9eMDP_jwHBZVjizpgexEzdjuz0E2iyXI4Vlfc7kiyaJBalQBwedWrpbXNt3ppl0MQCI_3ZBlx6404JgdQ4hWZs1o2HlKdr_OS54Xz-TkciRjyd6Ucm70puFHXyFKWFOUeeO7RblVayvHYmzY530MpsxZ4HlRkr0hig46hMOGiAwx7iVdq8DmeNaKmKB0LK-zOa1Xehm4NaG_EA7L-mJK9nK2uRWho0qIARicgB6fFuXf6Oa1Tw9WhvPin-xy-BlEw9VtXzG-JD29K806hcYViP6YV5doTrADYmE8PfeeiyYQw857vSLwHOj1tF66CLS_YkpCL501QsLaK3-D9IJzS7cv1RLEY5zNe&refId=DJg2034%2BxEKKOW9CZgR13Q%3D%3D&trackingId=ZiIxFtCgqLPz3dx9NcJpbQ%3D%3D"


# def test_job_service_sample_test():

#     url = linkedin_three

#     page = retrieve_job_page(url)

#     print("Status:", page.status_code)
#     print("Requested URL:", page.requested_url)
#     print("Final URL:", page.final_url)
#     print("Title:", page.title)
#     print("HTML length:", len(page.html or ""))
#     print("HTML preview:", (page.html or "")[:1000])

#     html = page.html or ""
#     html_lower = html.lower()

#     markers = [
#         "jobposting",
#         '"description"',
#         "description__text",
#         "show-more-less-html",
#         "job-details",
#         "authwall",
#         "uas/login",
#         "sign in",
#         "join linkedin",
#         "job is no longer available",
#         "<h1",
#         "<title",
#         "og:title",
#     ]

#     for marker in markers:
#         count = html_lower.count(marker.lower())

#         print(f"\nMarker: {marker}")
#         print(f"Occurrences: {count}")

#         if count:
#             index = html_lower.find(marker.lower())
#             start = max(0, index - 150)
#             end = min(len(html), index + 350)
#             print("Context:", html[start:end])

# def test_linkedin_parser_against_live_url():
#     url = linkedin_three  # Change this to url_two or url_three to test different cases

#     retrieved_page = retrieve_job_page(url)
#     assert retrieved_page.status_code == 200

#     extractor = LinkedInJobPageExtractor()
#     job = extractor.extract(retrieved_page)
#     # print(f"\nDEBUG - Job: {job}")
#     print(f"\nDEBUG - Job.description: {job.description}")
#     assert job.description

#     print(f"\nJob Description")
#     print(job.description)
#     print(f"\nResponsibilities")
#     print(job.responsibilities)
#     print(f"\nRequired Qualifications")
#     print(job.required_qualifications)
#     print(f"\nPreferred Qualifications")
#     print(job.preferred_qualifications)



FIXTURE_DIR = (
    Path(__file__).parent.parent
    / "fixtures"
    / "job_pages"
    / "linkedin"
)


@pytest.fixture
def load_html_fixture():
    def _load(filename: str) -> str:
        return (FIXTURE_DIR / filename).read_text(encoding="utf-8")
    return _load


@pytest.mark.parametrize(
    "fixture_name",
    [
        "optum_job_1.html",
        "optum_job_2.html",
        "job_3.html",
    ],
)


# def test_linkedin_extractor_directly(load_html_fixture, fixture_name):

#     html = load_html_fixture(fixture_name)
#     print('test_linkedin_extractor_directly html:', html)
  

#     page = JobPageResponse(
#         requested_url="https://www.linkedin.com/job-listing/test-job.htm",
#         final_url="https://www.linkedin.com/job-listing/test-job.htm",
#         status_code=200,
#         html=html,
#     )


#     extractor = LinkedInJobPageExtractor()

#     soup = BeautifulSoup(html, "html.parser")
    
#     description_html = extractor._dom_description_html(soup)

#     print("\nFixture:", fixture_name)
#     print("Description HTML found:", bool(description_html))
#     print("Description HTML length:", len(description_html or ""))

#     result = extractor.extract(page)
    
#     print("Extracted description:", bool(result.description))
#     print("Extraction method:", result.extraction_method)
#     print("Responsibilities:", result.responsibilities)
#     print("Required:", result.required_qualifications)
#     print("Preferred:", result.preferred_qualifications)



# @pytest.mark.parametrize(
#     "fixture_name",
#     [
#         "optum_job_1.html",
#         "optum_job_2.html",
#         "job_3.html",
#     ],
# )

# def test_linkedin_fixtures(load_html_fixture, fixture_name):

#     html = load_html_fixture(fixture_name)
    
#     soup = BeautifulSoup(html, "html.parser")

#     print("TITLE SELECTOR:")
#     print(soup.select_one('[data-testid="serp-job-details-title"]'))

#     print("\nJOB DESCRIPTION HEADINGS:")
#     for heading in soup.find_all(["h2", "h3"]):
#         if "description" in heading.get_text(" ", strip=True).lower():
#             print("Heading:", heading)
#             print("Parent:", heading.parent)
#             print("Next sibling:", heading.find_next_sibling())
#             print("Next div sibling:", heading.find_next_sibling("div"))

#     print("\nJSON-LD:")
#     for script in soup.find_all("script", type="application/ld+json"):
#         print(script.get_text()[:1000])
        

def test_process_job_page_with_linkedin_fixtures(
    monkeypatch,
    load_html_fixture,
    fixture_name,
    ):
    html = load_html_fixture(fixture_name)


    page = JobPageResponse(
        requested_url="https://www.linkedin.com/job-listing/test-job.htm",
        final_url="https://www.linkedin.com/job-listing/test-job.htm",
        status_code=200,
        html=html,
    )

    monkeypatch.setattr(
        job_page_service,
        "retrieve_job_page",
        lambda _: page,
    )

    result = job_page_service.process_job_page(page.requested_url)

    assert result.requested_url == page.requested_url
    assert result.final_url == page.final_url
    assert result.status_code == 200

    assert result.description
    assert result.extraction_method

    assert isinstance(result.responsibilities, list)
    assert isinstance(result.required_qualifications, list)
    assert isinstance(result.preferred_qualifications, list)


@pytest.mark.parametrize(
    ("fixture_name", "expected_responsibilities", "expected_required"),
    [
        (
            "optum_job_1.html",
            [
                # Replace these with actual items from the fixture.
            ],
            [
                # Replace these with actual items from the fixture.
            ],
        ),
        (
            "optum_job_2.html",
            [
                # Replace these with actual items from the fixture.
            ],
            [
                # Replace these with actual items from the fixture.
            ],
        ),
        (
            "job_3.html",
            [
                # Replace these with actual items from the fixture.
            ],
            [
                # Replace these with actual items from the fixture.
            ],
        ),
    ],
)


def test_process_job_page_extracts_expected_content_linkedin(
    monkeypatch,
    load_html_fixture,
    fixture_name,
    expected_responsibilities,
    expected_required,
):
    html = load_html_fixture(fixture_name)

    page = JobPageResponse(
        requested_url="https://www.linkedin.com/job-listing/test-job.htm",
        final_url="https://www.linkedin.com/job-listing/test-job.htm",
        status_code=200,
        html=html,
    )

    monkeypatch.setattr(
        job_page_service,
        "retrieve_job_page",
        lambda _: page,
    )

    result = job_page_service.process_job_page(page.requested_url)

    for item in expected_responsibilities:
        assert item in result.responsibilities

    for item in expected_required:
        assert item in result.required_qualifications


def test_parse_description_html_preserves_full_description_linkedin():
    html = """
    <div>
        <p>Introductory paragraph.</p>

        <h2>Responsibilities</h2>
        <ul>
            <li>Build APIs.</li>
            <li>Maintain services.</li>
        </ul>

        <h2>Required Qualifications</h2>
        <ul>
            <li>Experience with Python.</li>
        </ul>

        <h2>Preferred Qualifications</h2>
        <ul>
            <li>Experience with Docker.</li>
        </ul>
    </div>
    """

    result = parse_description_html(html)
    assert result.description is not None

    assert "Introductory paragraph." in result.description
    assert "Responsibilities" in result.description
    assert "Build APIs." in result.description
    assert "Required Qualifications" in result.description
    assert "Experience with Python." in result.description
    assert "Preferred Qualifications" in result.description
    assert "Experience with Docker." in result.description

    assert result.responsibilities == [
        "Build APIs.",
        "Maintain services.",
    ]
    assert result.required_qualifications == [
        "Experience with Python.",
    ]
    assert result.preferred_qualifications == [
        "Experience with Docker.",
    ]



@pytest.mark.parametrize(
    "job_type",
    [
        "JobPosting",
        "https://schema.org/JobPosting",
        "http://schema.org/JobPosting",
        "https://schema.org/JobPosting/",
    ],
)


def test_find_job_posting_recognizes_type_formats_linkedin(job_type):
    data = {
        "@type": job_type,
        "title": "Software Engineer",
    }

    soup = BeautifulSoup(
        f'<script type="application/ld+json">{json.dumps(data)}</script>',
        "html.parser",
    )

    result = find_job_posting(soup)

    assert result is not None
    assert result["title"] == "Software Engineer"


def test_find_job_posting_recognizes_type_array_linkedin():
    data = {
        "@type": ["Thing", "https://schema.org/JobPosting"],
        "title": "Software Engineer",
    }

    soup = BeautifulSoup(
        f'<script type="application/ld+json">{json.dumps(data)}</script>',
        "html.parser",
    )

    result = find_job_posting(soup)

    assert result is not None
    assert result["title"] == "Software Engineer"


def test_find_job_posting_finds_job_posting_in_graph_linkedin():
    data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "name": "Example Company",
            },
            {
                "@type": "https://schema.org/JobPosting",
                "title": "Software Engineer",
            },
        ],
    }

    soup = BeautifulSoup(
        f'<script type="application/ld+json">{json.dumps(data)}</script>',
        "html.parser",
    )

    result = find_job_posting(soup)

    assert result is not None
    assert result["title"] == "Software Engineer"


def test_find_job_posting_skips_malformed_json_linkedin():
    soup = BeautifulSoup(
        """
        <script type="application/ld+json">
            {"@type": "JobPosting",
        </script>
        """,
        "html.parser",
    )

    assert find_job_posting(soup) is None


def test_find_job_posting_handles_non_object_json_linkedin():
    soup = BeautifulSoup(
        """
        <script type="application/ld+json">"not an object"</script>
        <script type="application/ld+json">null</script>
        """,
        "html.parser",
    )

    assert find_job_posting(soup) is None


def test_process_job_page_with_linkedin_extraction(monkeypatch):
    html = """
    <div>
        <div>
            <h2>About the job</h2>
        </div>
        <p>
            <span data-testid="expandable-text-box">
                <span>
                    Introductory paragraph.

                    <strong>Responsibilities</strong>
                    <ul>
                        <li>Build APIs.</li>
                        <li>Maintain services.</li>
                    </ul>

                    <strong>Required Qualifications</strong>
                    <ul>
                        <li>Experience with Python.</li>
                    </ul>

                    <strong>Preferred Qualifications</strong>
                    <ul>
                        <li>Experience with Docker.</li>
                    </ul>
                </span>
                <button
                    data-testid="expandable-text-button"
                    type="button"
                >
                    … more
                </button>
            </span>
        </p>
    </div>
    """

    retrieved_page = RetrievedJobPage(
        requested_url=(
            "https://www.linkedin.com/job-listing/example"
        ),
        final_url=(
            "https://www.linkedin.com/job-listing/example"
        ),
        status_code=200,
        html=html,
    )

    monkeypatch.setattr(
        "app.job_page.service.retrieve_job_page",
        lambda url: retrieved_page,
    )

    result = process_job_page(retrieved_page.requested_url)
 
    assert result == JobPageProcessingResponse(
        requested_url=retrieved_page.requested_url,
        final_url=retrieved_page.final_url,
        status_code=200,
        # description="Introductory paragraph.",
        description=(
            "Introductory paragraph.\n\n"
            "Responsibilities\n\n"
            "• Build APIs.\n\n"
            "• Maintain services.\n\n"
            "Required Qualifications\n\n"
            "• Experience with Python.\n\n"
            "Preferred Qualifications\n\n"
            "• Experience with Docker."
        ),
        responsibilities=[
        "Build APIs.",
        "Maintain services.",
        ],
        required_qualifications=[
            "Experience with Python.",
        ],
        preferred_qualifications=[
            "Experience with Docker.",
        ],
        extraction_method="dom+html"
    )



def test_parse_description_text_preserves_full_description_linkedin():
    text = """
    Introductory paragraph.

    Responsibilities
    - Build APIs.
    - Maintain services.

    Required Qualifications
    - Experience with Python.

    Preferred Qualifications
    - Experience with Docker.
    """

    result = parse_description_text(text)

    assert result.description == (
        "Introductory paragraph.\n\n"
        "Responsibilities\n\n"
        "- Build APIs.\n\n"
        "- Maintain services.\n\n"
        "Required Qualifications\n\n"
        "- Experience with Python.\n\n"
        "Preferred Qualifications\n\n"
        "- Experience with Docker."
    )

    assert result.responsibilities == [
    "Build APIs",
    "Maintain services",
    ]

    assert result.required_qualifications == [
        "Experience with Python",
    ]

    assert result.preferred_qualifications == [
        "Experience with Docker",
    ]


def test_score_parsed_long_description_has_no_penalty_linkedin():
    parsed = ParsedDescription(
        description="A" * 5000,
        responsibilities=[],
        required_qualifications=[],
        preferred_qualifications=[],
    )

    assert score_parsed(parsed) == 2.0


def test_score_parsed_rewards_all_populated_categories_linkedin():
    parsed = ParsedDescription(
        description="Job description.",
        responsibilities=["Build APIs"],
        required_qualifications=["Python"],
        preferred_qualifications=["Docker"],
    )

    assert score_parsed(parsed) == 11.06


def test_score_parsed_penalizes_long_list_items_linkedin():
    parsed = ParsedDescription(
        description="Job description.",
        responsibilities=["A" * 501],
        required_qualifications=[],
        preferred_qualifications=[],
    )

    assert score_parsed(parsed) == 4.02


def test_score_parsed_caps_long_item_penalty_linkedin():
    parsed = ParsedDescription(
        description="Job description.",
        responsibilities=["A" * 501 for _ in range(5)],
        required_qualifications=[],
        preferred_qualifications=[],
    )

    assert score_parsed(parsed) == 2.1


def test_build_candidates_from_multiple_sources_linkedin():
    sources = [
        ("json-ld", "<p>First description.</p>"),
        ("dom", "<p>Second description.</p>"),
    ]

    candidates = build_candidates(sources)

    methods = [candidate.method for candidate in candidates]

    assert any(method.startswith("json-ld+") for method in methods)
    assert any(method.startswith("dom+") for method in methods)


def test_build_candidates_removes_duplicates_linkedin():
    description = "<p>Build and maintain APIs.</p>"

    sources = [
        ("json-ld", description),
        ("dom", description),
    ]

    candidates = build_candidates(sources)

    assert len(candidates) == 1
    assert candidates[0].method == "json-ld+html"


def test_build_candidates_preserves_priority_when_scores_tie_linkedin():
    sources = [
        ("json-ld", "<p>Same description.</p>"),
        ("dom", "<p>Different description.</p>"),
    ]

    candidates = build_candidates(sources)

    best = max(candidates, key=lambda candidate: candidate.score)

    assert best.method == "json-ld+html"


def test_build_candidates_returns_empty_list_without_sources_linkedin():
    candidates = build_candidates([])

    assert candidates == []


def test_build_candidates_html_candidate_receives_bonus_linkedin(monkeypatch):
    html_parsed = ParsedDescription(
        description="Job description.",
        responsibilities=["Build APIs"],
        required_qualifications=[],
        preferred_qualifications=[],
    )
    text_parsed = ParsedDescription(
        description="Job description.",
        responsibilities=["Build APIs", "Maintain services"],
        required_qualifications=[],
        preferred_qualifications=[],
    )
    
    monkeypatch.setattr(
        common,
        "parse_description_html",
        lambda _: html_parsed,
    )

    monkeypatch.setattr(
        common,
        "parse_description_text",
        lambda _: text_parsed,
    )

    candidates = build_candidates([("dom", "<p>Job description.</p>")])

    html_candidate = next(c for c in candidates if c.method == "dom+html")
    text_candidate = next(c for c in candidates if c.method == "dom+text")

    assert html_candidate.score == score_parsed(html_parsed) + 0.5
    assert text_candidate.score == score_parsed(text_parsed)


def test_build_candidates_preserves_source_priority_when_scores_tie_linkedin(monkeypatch):
    parsed_one = ParsedDescription(
        description="First description.",
        responsibilities=[],
        required_qualifications=[],
        preferred_qualifications=[],
    )
    parsed_two = ParsedDescription(
        description="Second description.",
        responsibilities=[],
        required_qualifications=[],
        preferred_qualifications=[],
    )

    monkeypatch.setattr(
        common,
        "parse_description_html",
        lambda _: parsed_one,
    )
    monkeypatch.setattr(
        common,
        "parse_description_text",
        lambda _: parsed_two,
    )
    monkeypatch.setattr(
        common,
        "score_parsed",
        lambda _: 2.0,
    )

    candidates = build_candidates([
        ("json-ld", "<p>First</p>"),
        ("dom", "<p>Second</p>"),
    ])

    best = max(candidates, key=lambda candidate: candidate.score)

    assert best.method == "json-ld+html"
