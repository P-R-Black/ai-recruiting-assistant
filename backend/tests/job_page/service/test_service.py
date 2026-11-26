from unittest.mock import Mock

import httpx
import pytest

from app.job_page.schema import (
    JobDescriptionResponse,
    JobPageProcessingResponse,
    JobPageResponse,
)
from app.job_page.service import process_job_page


TEST_URL = "https://jobs.example.com/listing/123"
FINAL_URL = "https://jobs.example.com/listing/456"
HTML = "<html><body><h1>Software Engineer</h1></body></html>"
DESCRIPTION = "We are looking for a Python developer."


@pytest.fixture
def mock_retrieve_job_page(monkeypatch):
    mock = Mock()

    monkeypatch.setattr(
        "app.job_page.service.retrieve_job_page",
        mock,
    )

    return mock


@pytest.fixture
def mock_extract_job_description(monkeypatch):
    mock = Mock()

    monkeypatch.setattr(
        "app.job_page.service.extract_job_description",
        mock,
    )

    return mock


@pytest.fixture
def retrieved_page():
    return JobPageResponse(
        requested_url=TEST_URL,
        final_url=FINAL_URL,
        status_code=200,
        html=HTML,
    )


def test_process_job_page_success(
    mock_retrieve_job_page,
    mock_extract_job_description,
    retrieved_page,
):
    mock_retrieve_job_page.return_value = retrieved_page

    mock_extract_job_description.return_value = JobDescriptionResponse(
        description=DESCRIPTION,
        extraction_method="json_ld",
    )

    result = process_job_page(TEST_URL)
  

    assert result == JobPageProcessingResponse(
        requested_url=TEST_URL,
        final_url=FINAL_URL,
        status_code=200,
        description=DESCRIPTION,
        extraction_method="json_ld",
    )

    mock_retrieve_job_page.assert_called_once_with(TEST_URL)
    mock_extract_job_description.assert_called_once_with(
        html=HTML,
        url=FINAL_URL,
    )


def test_process_job_page_uses_html_extraction(
    mock_retrieve_job_page,
    mock_extract_job_description,
    retrieved_page,
):
    mock_retrieve_job_page.return_value = retrieved_page

    mock_extract_job_description.return_value = JobDescriptionResponse(
        description=DESCRIPTION,
        extraction_method="html",
    )

    result = process_job_page(TEST_URL)

    assert result.description == DESCRIPTION
    assert result.extraction_method == "html"


def test_process_job_page_returns_empty_description(
    mock_retrieve_job_page,
    mock_extract_job_description,
    retrieved_page,
):
    mock_retrieve_job_page.return_value = retrieved_page

    mock_extract_job_description.return_value = JobDescriptionResponse()

    result = process_job_page(TEST_URL)

    assert result.description is None
    assert result.extraction_method is None
    assert result.status_code == 200


def test_process_job_page_propagates_url_validation_error(
    mock_retrieve_job_page,
    mock_extract_job_description,
):
    mock_retrieve_job_page.side_effect = ValueError(
        "Only HTTP and HTTPS URLs are supported."
    )

    with pytest.raises(
        ValueError,
        match="Only HTTP and HTTPS URLs",
    ):
        process_job_page(TEST_URL)

    mock_retrieve_job_page.assert_called_once_with(TEST_URL)
    mock_extract_job_description.assert_not_called()


def test_process_job_page_propagates_http_error(
    mock_retrieve_job_page,
    mock_extract_job_description,
):
    request = httpx.Request("GET", TEST_URL)

    mock_retrieve_job_page.side_effect = httpx.ConnectError(
        "Connection failed",
        request=request,
    )

    with pytest.raises(httpx.ConnectError):
        process_job_page(TEST_URL)

    mock_retrieve_job_page.assert_called_once_with(TEST_URL)
    mock_extract_job_description.assert_not_called()


