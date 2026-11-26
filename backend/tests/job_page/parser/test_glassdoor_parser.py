import json
from pathlib import Path
import pytest
from bs4 import BeautifulSoup

from app.job_page.retriever import retrieve_job_page
from app.job_page.parsers.glassdoor import GlassdoorJobPageExtractor, JobPageResponse
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


glassdoor_one = "https://www.glassdoor.com/job-listing/frontend-software-engineer-react-typescript-select-source-solutions-JV_KO0,43_KE44,67.htm?jl=1010315069518&utm_source=jobalert&utm_medium=email&utm_content=ja-jobpos10-agejp-1010315069518&utm_campaign=jobAlertAlert&tgt=GD_JOB_VIEW&src=GD_JOB_AD&uido=31A21D4BAD477BFD012C0C83DC3E22A8&ao=1136043&jrtk=5-yul1-0-1k6fetd7eiuf6800-d574a76295de8122&cs=1_ad47ae5f&s=224&t=JA&pos=110&ja=299751390&guid=000001a19e5a8881a3c47d9a793b0fce&jobListingId=1010315069518&ea=1&vt=e&cb=1793667806666&ctt=1793809675337&srs=EMAIL_JOB_ALERT&gdir=1"
glassdoor_two = "https://www.glassdoor.com/job-listing/frontend-engineer-fieldx-target-JV_IC1162260_KO0,24_KE25,31.htm?jl=1010312106672&utm_source=jobalert&utm_medium=email&utm_content=ja-jobpos2-age1d-1010312106672&utm_campaign=jobAlertAlert&tgt=GD_JOB_VIEW&src=GD_JOB_AD&uido=31A21D4BAD477BFD012C0C83DC3E22A8&ao=1136043&jrtk=5-yul1-0-1k6cie2uui8pn800-44fed7abd100989f&cs=1_678696f2&s=224&t=JA&pos=102&ja=420529732&guid=000001a198fd04098df365a6b66ecc7e&jobListingId=1010312106672&vt=e&cb=1793570835642&ctt=1793809907458&srs=EMAIL_JOB_ALERT&gdir=1"
glassdoor_three = "https://www.glassdoor.com/job-listing/software-engineer-atasc-ai-JV_KO0,17_KE18,26.htm?jl=1010315163879&utm_source=jobalert&utm_medium=email&utm_content=ja-jobpos6-agept-1010315163879&utm_campaign=jobAlertAlert&tgt=GD_JOB_VIEW&src=GD_JOB_AD&uido=31A21D4BAD477BFD012C0C83DC3E22A8&ao=1136043&jrtk=5-yul1-0-1k6g6sjkel52g800-2fc5236ade818f31&cs=1_963ba87e&s=224&t=JA&pos=106&ja=313092446&guid=000001a1a0118a5489b86d69ce89e744&jobListingId=1010315163879&ea=1&vt=e&cb=1793692946256&ctt=1793809804286&srs=EMAIL_JOB_ALERT&gdir=1"

test_url = "https://www.glassdoor.com/partner/jobListing.htm?pos=110&ao=1136043&s=224&guid=000001a1db14209b8ffc454a6304572b&src=GD_JOB_AD&t=JA&vt=e&uido=31A21D4BAD477BFD012C0C83DC3E22A8&ea=1&cs=1_abd4ae84&cb=1794678468848&jobListingId=1010323923396&jrtk=5-yul1-0-1k7dioc1mj726800-a2d7440087450fcb&tgt=GD_JOB_VIEW&utm_medium=email&utm_source=jobalert&utm_campaign=jobAlertAlert&utm_content=ja-jobpos10-age2d-1010323923396&ja=382694110"

# def test_job_service_sample_test():

#     url = "https://www.linkedin.com/jobs/view/4485275539/"

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


# def test_glassdoor_parser_against_live_url():
#     url = glassdoor_one  # Change this to url_two or url_three to test different cases

#     retrieved_page = retrieve_job_page(url)
#     assert retrieved_page.status_code == 200

#     extractor = GlassdoorJobPageExtractor()
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
    / "glassdoor"
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


def test_process_job_page_with_glassdoor_fixtures(
    monkeypatch,
    load_html_fixture,
    fixture_name,
):
    html = load_html_fixture(fixture_name)


    page = JobPageResponse(
        requested_url="https://www.glassdoor.com/job-listing/test-job.htm",
        final_url="https://www.glassdoor.com/job-listing/test-job.htm",
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


def test_process_job_page_extracts_expected_content(
    monkeypatch,
    load_html_fixture,
    fixture_name,
    expected_responsibilities,
    expected_required,
):
    html = load_html_fixture(fixture_name)

    page = JobPageResponse(
        requested_url="https://www.glassdoor.com/job-listing/test-job.htm",
        final_url="https://www.glassdoor.com/job-listing/test-job.htm",
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


def test_parse_description_html_preserves_full_description():
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

def test_find_job_posting_recognizes_type_formats(job_type):
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


def test_find_job_posting_recognizes_type_array():
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


def test_find_job_posting_finds_job_posting_in_graph():
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


def test_find_job_posting_skips_malformed_json():
    soup = BeautifulSoup(
        """
        <script type="application/ld+json">
            {"@type": "JobPosting",
        </script>
        """,
        "html.parser",
    )

    assert find_job_posting(soup) is None


def test_find_job_posting_handles_non_object_json():
    soup = BeautifulSoup(
        """
        <script type="application/ld+json">"not an object"</script>
        <script type="application/ld+json">null</script>
        """,
        "html.parser",
    )

    assert find_job_posting(soup) is None




def test_process_job_page_with_glassdoor_extraction(monkeypatch):
    html = """
    <div class="JobDetails_jobDescription__uW_fK">
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

    retrieved_page = RetrievedJobPage(
        requested_url=(
            "https://www.glassdoor.com/job-listing/example"
        ),
        final_url=(
            "https://www.glassdoor.com/job-listing/example"
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




def test_parse_description_text_preserves_full_description():
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


def test_score_parsed_long_description_has_no_penalty():
    parsed = ParsedDescription(
        description="A" * 5000,
        responsibilities=[],
        required_qualifications=[],
        preferred_qualifications=[],
    )

    assert score_parsed(parsed) == 2.0


def test_score_parsed_rewards_all_populated_categories():
    parsed = ParsedDescription(
        description="Job description.",
        responsibilities=["Build APIs"],
        required_qualifications=["Python"],
        preferred_qualifications=["Docker"],
    )

    assert score_parsed(parsed) == 11.06


def test_score_parsed_penalizes_long_list_items():
    parsed = ParsedDescription(
        description="Job description.",
        responsibilities=["A" * 501],
        required_qualifications=[],
        preferred_qualifications=[],
    )

    assert score_parsed(parsed) == 4.02


def test_score_parsed_caps_long_item_penalty():
    parsed = ParsedDescription(
        description="Job description.",
        responsibilities=["A" * 501 for _ in range(5)],
        required_qualifications=[],
        preferred_qualifications=[],
    )

    assert score_parsed(parsed) == 2.1


def test_build_candidates_from_multiple_sources():
    sources = [
        ("json-ld", "<p>First description.</p>"),
        ("dom", "<p>Second description.</p>"),
    ]

    candidates = build_candidates(sources)

    methods = [candidate.method for candidate in candidates]

    assert any(method.startswith("json-ld+") for method in methods)
    assert any(method.startswith("dom+") for method in methods)


def test_build_candidates_removes_duplicates():
    description = "<p>Build and maintain APIs.</p>"

    sources = [
        ("json-ld", description),
        ("dom", description),
    ]

    candidates = build_candidates(sources)

    assert len(candidates) == 1
    assert candidates[0].method == "json-ld+html"


def test_build_candidates_preserves_priority_when_scores_tie():
    sources = [
        ("json-ld", "<p>Same description.</p>"),
        ("dom", "<p>Different description.</p>"),
    ]

    candidates = build_candidates(sources)

    best = max(candidates, key=lambda candidate: candidate.score)

    assert best.method == "json-ld+html"


def test_build_candidates_returns_empty_list_without_sources():
    candidates = build_candidates([])

    assert candidates == []


def test_build_candidates_html_candidate_receives_bonus(monkeypatch):
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


def test_build_candidates_preserves_source_priority_when_scores_tie(monkeypatch):
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