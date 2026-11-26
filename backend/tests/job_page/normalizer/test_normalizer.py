
import pytest
from types import SimpleNamespace
from unittest.mock import Mock
from bs4 import BeautifulSoup

from app.job_page.normalizer.normalizer import normalize_parsed_description
from app.job_page.parsers.helpers.common import ParsedDescription
from app.job_page.parsers import glassdoor


def make_parsed_description(
    description: str | None = None,
    responsibilities: list[str] | None = None,
    required_qualifications: list[str] | None = None,
    preferred_qualifications: list[str] | None = None,
) -> ParsedDescription:
    """Create a ParsedDescription for testing."""
    return ParsedDescription(
        description=description,
        responsibilities=responsibilities or [],
        required_qualifications=required_qualifications or [],
        preferred_qualifications=preferred_qualifications or [],
    )


def test_normalize_recovers_all_three_sections():
    parsed = make_parsed_description(
        description=(
            "Job Description\n\n"
            "Responsibilities:\n"
            "- Build and maintain APIs.\n"
            "- Work with the engineering team.\n\n"
            "Required Qualifications:\n"
            "- 3+ years of Python experience.\n"
            "- Experience with PostgreSQL.\n\n"
            "Preferred Qualifications:\n"
            "- Experience with AWS.\n"
        )
    )

    result = normalize_parsed_description(parsed)

    assert result.description == parsed.description
    assert result.responsibilities == [
        "Build and maintain APIs.",
        "Work with the engineering team.",
    ]
    assert result.required_qualifications == [
        "3+ years of Python experience.",
        "Experience with PostgreSQL.",
    ]
    assert result.preferred_qualifications == [
        "Experience with AWS.",
    ]


def test_normalize_recovers_inline_heading_content():
    parsed = make_parsed_description(
        description=(
            "We are looking for a Graphic Designer.\n\n"
            "Duties Include: Designing Marketing Materials.\n"
        )
    )

    result = normalize_parsed_description(parsed)

    assert result.responsibilities == [
        "Designing Marketing Materials."
    ]


def test_normalize_stops_at_unknown_heading():
    parsed = make_parsed_description(
        description=(
            "Responsibilities:\n"
            "- Build APIs.\n"
            "- Maintain services.\n\n"
            "About Our Company:\n"
            "- We are a growing technology company.\n"
            "- We value collaboration.\n\n"
            "Required Qualifications:\n"
            "- Experience with Python.\n"
        )
    )

    result = normalize_parsed_description(parsed)

    assert result.responsibilities == [
        "Build APIs.",
        "Maintain services.",
    ]
    assert result.required_qualifications == [
        "Experience with Python."
    ]


def test_normalize_returns_empty_lists_when_no_sections_recognized():
    description = (
        "We are looking for a Graphic Designer.\n\n"
        "Experience with Adobe Creative Suite.\n"
        "Photography and videography experience preferred.\n"
    )

    parsed = make_parsed_description(description=description)

    result = normalize_parsed_description(parsed)

    assert result.description == description
    assert result.responsibilities == []
    assert result.required_qualifications == []
    assert result.preferred_qualifications == []


def test_normalize_removes_duplicate_items():
    parsed = make_parsed_description(
        description=(
            "Responsibilities:\n"
            "- Build APIs.\n"
            "- Maintain services.\n"
            "- Build APIs.\n"
        )
    )

    result = normalize_parsed_description(parsed)

    assert result.responsibilities == [
        "Build APIs.",
        "Maintain services.",
    ]


def test_normalize_returns_original_when_description_is_missing():
    parsed = make_parsed_description(description=None)

    result = normalize_parsed_description(parsed)

    assert result is parsed
    assert result.description is None
    assert result.responsibilities == []
    assert result.required_qualifications == []
    assert result.preferred_qualifications == []



def test_normalize_recovers_only_missing_sections():
    parsed = make_parsed_description(
        description=(
            "Responsibilities:\n"
            "- Build APIs.\n\n"
            "Required Qualifications:\n"
            "- Experience with Python.\n\n"
            "Preferred Qualifications:\n"
            "- Experience with AWS.\n"
        ),
        responsibilities=["Existing responsibility."],
    )

    result = normalize_parsed_description(parsed)

    assert result.responsibilities == ["Existing responsibility."]
    assert result.required_qualifications == [
        "Experience with Python."
    ]
    assert result.preferred_qualifications == [
        "Experience with AWS."
    ]


def test_normalize_does_not_modify_populated_lists():
    parsed = make_parsed_description(
        description="Responsibilities:\n- Build APIs.",
        responsibilities=["Existing responsibility."],
        required_qualifications=["Existing requirement."],
        preferred_qualifications=["Existing preference."],
    )

    result = normalize_parsed_description(parsed)

    assert result is parsed
    assert result.responsibilities == ["Existing responsibility."]
    assert result.required_qualifications == ["Existing requirement."]
    assert result.preferred_qualifications == ["Existing preference."]


def test_normalize_returns_original_when_all_lists_are_populated():
    parsed = make_parsed_description(
        description="Some job description.",
        responsibilities=["Build APIs."],
        required_qualifications=["Experience with Python."],
        preferred_qualifications=["Experience with AWS."],
    )

    result = normalize_parsed_description(parsed)

    assert result is parsed


def test_extract_normalizes_winning_candidate(monkeypatch):
    winning_parsed = ParsedDescription(
        description=(
            "Responsibilities:\n"
            "- Build APIs.\n\n"
            "Required Qualifications:\n"
            "- Experience with Python."
        ),
        responsibilities=[],
        required_qualifications=[],
        preferred_qualifications=[],
    )

    losing_parsed = ParsedDescription(
        description="A different candidate.",
        responsibilities=["Different responsibility."],
        required_qualifications=[],
        preferred_qualifications=[],
    )

    winning_candidate = glassdoor.Candidate(
        method="json-ld+text",
        parsed=winning_parsed,
        score=10.0,
    )

    losing_candidate = glassdoor.Candidate(
        method="dom+html",
        parsed=losing_parsed,
        score=5.0,
    )

    normalized_parsed = ParsedDescription(
        description=winning_parsed.description,
        responsibilities=["Build APIs."],
        required_qualifications=["Experience with Python."],
        preferred_qualifications=[],
    )

    normalizer_mock = Mock(return_value=normalized_parsed)

    monkeypatch.setattr(
        glassdoor,
        "normalize_parsed_description",
        normalizer_mock,
    )

    extractor = glassdoor.GlassdoorJobPageExtractor()

    monkeypatch.setattr(
        extractor,
        "candidates",
        lambda soup, posting: [losing_candidate, winning_candidate],
    )

    monkeypatch.setattr(extractor, "_title", lambda soup, posting: "Software Developer")
    monkeypatch.setattr(extractor, "_company", lambda soup, posting: "Example Company")
    monkeypatch.setattr(extractor, "_location", lambda soup, posting: "Remote")

    page = SimpleNamespace(
        status_code=200,
        html="<html><body></body></html>",
        title=None,
        company=None,
        location=None,
        model_copy=lambda update: SimpleNamespace(**update),
    )

    result = extractor.extract(page)

    normalizer_mock.assert_called_once_with(winning_parsed)

    assert result.extraction_method == "json-ld+text"
    assert result.description == winning_parsed.description
    assert result.responsibilities == ["Build APIs."]
    assert result.required_qualifications == ["Experience with Python."]
    assert result.preferred_qualifications == []


def test_extract_does_not_normalize_when_no_candidates(monkeypatch):
    normalizer_mock = Mock()

    monkeypatch.setattr(
        glassdoor,
        "normalize_parsed_description",
        normalizer_mock,
    )

    extractor = glassdoor.GlassdoorJobPageExtractor()

    monkeypatch.setattr(
        extractor,
        "candidates",
        lambda soup, posting: [],
    )

    monkeypatch.setattr(extractor, "_title", lambda soup, posting: "Software Developer")
    monkeypatch.setattr(extractor, "_company", lambda soup, posting: "Example Company")
    monkeypatch.setattr(extractor, "_location", lambda soup, posting: "Remote")

    page = SimpleNamespace(
        status_code=200,
        html="<html><body></body></html>",
        title=None,
        company=None,
        location=None,
        model_copy=lambda update: SimpleNamespace(**update),
    )

    result = extractor.extract(page)

    normalizer_mock.assert_not_called()

    assert result.title == "Software Developer"
    assert result.company == "Example Company"
    assert result.location == "Remote"
    assert result.extraction_method is None