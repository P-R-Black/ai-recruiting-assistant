# --------------------------------------------------------------------------- #
# Dispatch by domain (same idea as the email normalizers)
# --------------------------------------------------------------------------- #
from urllib.parse import urlparse

from app.job_page.parsers.base import BaseJobPageExtractor
from app.job_page.parsers.glassdoor import GlassdoorJobPageExtractor

_EXTRACTORS: dict[str, type[BaseJobPageExtractor]] = {
    "glassdoor.com": GlassdoorJobPageExtractor,
}


def get_job_page_extractor(url: str) -> BaseJobPageExtractor | None:
    host = (urlparse(url).hostname or "").lower()
    for domain, cls in _EXTRACTORS.items():
        if host == domain or host.endswith("." + domain):
            return cls()
    return None