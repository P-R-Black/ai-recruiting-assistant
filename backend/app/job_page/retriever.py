import ipaddress
import socket
import time
from urllib.parse import urljoin, urlparse

import httpx

from app.job_page.schema import JobPageResponse

TIMEOUT = httpx.Timeout(20.0, connect=10.0)
REQUEST_DELAY_SECONDS = 4

HEADERS = {
    "User-Agent": 
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) / "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        )
}

MAX_REDIRECTS = 5

def validate_url(url: str) -> str:
    """Validate a URL before making an HTTP request."""
    parsed_url = urlparse(url)

    if parsed_url.scheme not in {"http", "https"}:
        raise ValueError("Only HTTP and HTTPS URLs are supported.")

    hostname = parsed_url.hostname

    if not hostname:
        raise ValueError("The URL must contain a hostname.")

    if parsed_url.username or parsed_url.password:
        raise ValueError("URLs containing credentials are not allowed.")

    try:
        # Check literal IP addresses directly.
        ip = ipaddress.ip_address(hostname)
        addresses = [ip]

    except ValueError:
        # Hostname is not a literal IP; resolve it through DNS.
        try:
            resolved_addresses = socket.getaddrinfo(
                hostname,
                parsed_url.port
                or (443 if parsed_url.scheme == "https" else 80),
                type=socket.SOCK_STREAM,
            )
        except socket.gaierror as exc:
            raise ValueError(
                "The URL hostname could not be resolved."
            ) from exc

        addresses = [
            ipaddress.ip_address(address[4][0])
            for address in resolved_addresses
        ]

    for ip in addresses:
        if not ip.is_global:
            raise ValueError(
                "Requests to private or internal addresses are not allowed."
            )

    return url


def retrieve_job_page(url: str) -> JobPageResponse:
    """
    Retrieve a job listing page and return its HTTP response information.

    Raises:
        ValueError: If the URL is invalid or unsafe.
        httpx.HTTPError: If the request fails.
    """
    try:
        requested_url = validate_url(url)
        print("requested_url hit:", requested_url)
    except ValueError as e:
        print(f"DEBUG - Error occurred while validating URL: {e}")
        raise

    current_url = requested_url
    

    with httpx.Client(
        timeout=TIMEOUT,
        headers=HEADERS,
        follow_redirects=False,
    ) as client:
        

        for redirect_count in range(MAX_REDIRECTS + 1):
           
            # validate_url(current_url)

            try:
                response = client.get(current_url)
            finally:
                time.sleep(REQUEST_DELAY_SECONDS)
            print('DEBUG - Response status code:', response.status_code)
            print("DEBUG - Retry-After:", response.headers.get("Retry-After"),)
            if response.is_redirect:
                location = response.headers.get("location")

                if not location:
                    raise httpx.HTTPStatusError(
                        "Redirect response did not include a Location header.",
                        request=response.request,
                        response=response,
                    )

                # Resolve relative redirects and validate the destination
                # before checking the redirect limit.
                redirect_url = urljoin(current_url, location)
                validate_url(redirect_url)

                if redirect_count == MAX_REDIRECTS:
                    raise httpx.TooManyRedirects(
                        "The maximum number of redirects was exceeded.",
                        request=response.request,
                    )

                current_url = redirect_url
                continue
            # if response.is_redirect:
            #     if redirect_count == MAX_REDIRECTS:
            #         raise httpx.TooManyRedirects(
            #             "The maximum number of redirects was exceeded.",
            #             request=response.request,
            #         )

            #     location = response.headers.get("location")

            #     if not location:
            #         raise httpx.HTTPStatusError(
            #             "Redirect response did not include a Location header.",
            #             request=response.request,
            #             response=response,
            #         )

            #     current_url = urljoin(current_url, location)
            #     continue

            response.raise_for_status()

            return JobPageResponse(
                requested_url=requested_url,
                final_url=str(response.url),
                status_code=response.status_code,
                html=response.text,
            )
