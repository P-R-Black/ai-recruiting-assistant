import socket

import httpx
import pytest

from app.job_page.retriever import retrieve_job_page


TEST_URL = "https://jobs.example.com/listing/123"
REDIRECT_URL = "https://jobs.example.com/listing/456"
HTML = "<html><body><h1>Software Engineer</h1></body></html>"

PUBLIC_IP = "93.184.216.34"


@pytest.fixture
def mock_dns(monkeypatch):
    """Resolve hostnames to a public IP without making DNS requests."""

    def fake_getaddrinfo(host, port, type):
        return [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                (PUBLIC_IP, port),
            )
        ]

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)


@pytest.fixture
def mock_httpx_client(monkeypatch):
    """Replace the retriever's HTTPX client with a mocked transport."""

    def install(handler):
        transport = httpx.MockTransport(handler)
        client = httpx.Client(transport=transport)

        monkeypatch.setattr(
            "app.job_page.retriever.httpx.Client",
            lambda **kwargs: client,
        )

        return client

    return install


def test_retrieve_job_page_success(mock_dns, mock_httpx_client):
    def handler(request):
        return httpx.Response(
            status_code=200,
            text=HTML,
            request=request,
        )


    mock_httpx_client(handler)

    result = retrieve_job_page(TEST_URL)

    assert result.requested_url == TEST_URL
    assert result.final_url == TEST_URL
    assert result.status_code == 200
    assert result.html == HTML


def test_retrieve_job_page_follows_redirect(mock_dns, mock_httpx_client):
    def handler(request):
        if str(request.url) == TEST_URL:
            return httpx.Response(
                status_code=302,
                headers={"Location": REDIRECT_URL},
                request=request,
            )

        return httpx.Response(
            status_code=200,
            text=HTML,
            request=request,
        )

    mock_httpx_client(handler)

    result = retrieve_job_page(TEST_URL)

    assert result.requested_url == TEST_URL
    assert result.final_url == REDIRECT_URL
    assert result.status_code == 200
    assert result.html == HTML


def test_retrieve_job_page_redirects_to_private_ip_are_rejected(
    mock_dns,
    mock_httpx_client,
):
    def handler(request):
        return httpx.Response(
            status_code=302,
            headers={"Location": "http://127.0.0.1/admin"},
            request=request,
        )

    mock_httpx_client(handler)

    with pytest.raises(ValueError, match="private or internal"):
        retrieve_job_page(TEST_URL)


def test_retrieve_job_page_too_many_redirects(
    mock_dns,
    mock_httpx_client,
):
    def handler(request):
        return httpx.Response(
            status_code=302,
            headers={"Location": TEST_URL},
            request=request,
        )

    mock_httpx_client(handler)

    with pytest.raises(httpx.TooManyRedirects):
        retrieve_job_page(TEST_URL)


def test_retrieve_job_page_rejects_invalid_scheme():
    with pytest.raises(ValueError, match="Only HTTP and HTTPS"):
        retrieve_job_page("ftp://jobs.example.com/listing/123")


def test_retrieve_job_page_rejects_private_ip(mock_dns):
    with pytest.raises(ValueError, match="private or internal"):
        retrieve_job_page("http://192.168.1.10/listing/123")


def test_retrieve_job_page_dns_failure(monkeypatch):
    def failing_getaddrinfo(*args, **kwargs):
        raise socket.gaierror("DNS lookup failed")

    monkeypatch.setattr(socket, "getaddrinfo", failing_getaddrinfo)

    with pytest.raises(ValueError, match="hostname could not be resolved"):
        retrieve_job_page(TEST_URL)


def test_retrieve_job_page_http_error(mock_dns, mock_httpx_client):
    def handler(request):
        return httpx.Response(
            status_code=404,
            request=request,
        )

    mock_httpx_client(handler)

    with pytest.raises(httpx.HTTPStatusError):
        retrieve_job_page(TEST_URL)


def test_retrieve_job_page_timeout(mock_dns, mock_httpx_client):
    def handler(request):
        raise httpx.ConnectTimeout(
            "Connection timed out",
            request=request,
        )

    mock_httpx_client(handler)

    with pytest.raises(httpx.TimeoutException):
        retrieve_job_page(TEST_URL)


def test_retrieve_job_page_connection_error(
    mock_dns,
    mock_httpx_client,
):
    def handler(request):
        raise httpx.ConnectError(
            "Connection failed",
            request=request,
        )

    mock_httpx_client(handler)

    with pytest.raises(httpx.RequestError):
        retrieve_job_page(TEST_URL)