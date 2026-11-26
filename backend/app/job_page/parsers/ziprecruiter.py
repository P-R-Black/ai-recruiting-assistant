from __future__ import annotations

import re
from abc import abstractmethod

from bs4 import BeautifulSoup

from app.job_page.parsers.base import BaseJobPageExtractor
from app.job_page.parsers.helpers.common import (
    Candidate,
    build_candidates,
    clean_text,
    find_job_posting,
)
from app.job_page.schema import JobPageResponse


class ScoredJobPageExtractor(BaseJobPageExtractor):
    """Shared pipeline: gather description sources (JSON-LD, DOM), run every parser
    strategy over each, score the results and keep the best.
 
    A board subclass only supplies its DOM selectors via the ``_dom_*`` hooks."""
 
    # ---- hooks for subclasses -------------------------------------------- #
    @abstractmethod
    def _dom_description_html(self, soup: BeautifulSoup) -> str | None: ...
 
    @abstractmethod
    def _dom_title(self, soup: BeautifulSoup) -> str | None: ...
 
    @abstractmethod
    def _dom_company(self, soup: BeautifulSoup) -> str | None: ...
 
    @abstractmethod
    def _dom_location(self, soup: BeautifulSoup) -> str | None: ...
 
    # ---- pipeline ---------------------------------------------------------- #
    def extract(self, page: JobPageResponse) -> JobPageResponse:
        if page.status_code != 200 or not page.html:
            return page
 
        soup = BeautifulSoup(page.html, "html.parser")
        posting = find_job_posting(soup)
        candidates = self.candidates(soup, posting)
        best = max(candidates, key=lambda c: c.score) if candidates else None  # ties -> first
 
        updates = {
            "title": self._title(soup, posting) or page.title,
            "company": self._company(soup, posting) or page.company,
            "location": self._location(soup, posting) or page.location,
            "extraction_method": best.method if best else None,
        }
        if best:
            updates.update(
                description=best.parsed.description,
                responsibilities=best.parsed.responsibilities,
                required_qualifications=best.parsed.required_qualifications,
                preferred_qualifications=best.parsed.preferred_qualifications,
            )
        return page.model_copy(update=updates)
 
    def candidates(self, soup: BeautifulSoup, posting: dict | None) -> list[Candidate]:
        """Every (source x strategy) result with its score. Useful for debugging."""
        sources: list[tuple[str, str]] = []
        if posting and posting.get("description"):
            sources.append(("json-ld", posting["description"]))
        if html := self._dom_description_html(soup):
            sources.append(("dom", html))
        return build_candidates(sources)
 
    def _title(self, soup, posting) -> str | None:
        if posting and posting.get("title"):
            return clean_text(posting["title"])
        return self._dom_title(soup)
 
    def _company(self, soup, posting) -> str | None:
        org = (posting or {}).get("hiringOrganization") or {}
        if isinstance(org, dict) and org.get("name"):
            return clean_text(org["name"])
        return self._dom_company(soup)
 
    def _location(self, soup, posting) -> str | None:
        # The on-page text is usually more precise than JSON-LD ("Eden Prairie, MN" vs "Minnesota").
        if loc := self._dom_location(soup):
            return loc
        place = (posting or {}).get("jobLocation")
        place = place[0] if isinstance(place, list) and place else place
        address = (place or {}).get("address") or {}
        parts = [address.get("addressLocality"), address.get("addressRegion")]
        return ", ".join(p for p in parts if p) or None
 
    @staticmethod
    def _text(node) -> str | None:
        return clean_text(node.get_text(" ")) if node else None
    

class ZipRecruiterJobPageExtractor(ScoredJobPageExtractor):
    """ZipRecruiter's job-details pane (Next.js, Tailwind classes) has no JSON-LD in the
    pages we've seen, so everything comes from the DOM. Utility classes are unstable;
    anchor on ``data-testid`` attributes and on the "Job description" heading instead.
 
    Pane layout:
        [data-testid=serp-job-details-title] > h2      title
        <p> right after the title block                 "Chicago, IL • Remote"
        [data-testid=employer-details-header] span      company (first span)
        <h2>Job description</h2> + next <div>           body (may be followed by an
                                                        <h3>Company Description</h3> block)
    """
    _TITLE_SELECTOR = '[data-testid="serp-job-details-title"]'
    _COMPANY_SELECTOR = '[data-testid="employer-details-header"] span'
    # _DESCRIPTION_LABEL = re.compile(r"^\s*job description\s*$", re.I)
    _DESCRIPTION_LABEL = re.compile(r"^\s*job\s+description\s*$", re.I)
 
    def _dom_description_html(self, soup):
        for heading in soup.find_all(["h2", "h3"]):
            if self._DESCRIPTION_LABEL.match(heading.get_text()):
                if box := heading.find_next_sibling("div"):
                    return box.decode_contents()
        return None
 
    def _dom_title(self, soup):
        return self._text(soup.select_one(self._TITLE_SELECTOR))
 
    def _dom_company(self, soup):
        return self._text(soup.select_one(self._COMPANY_SELECTOR))
 
    def _dom_location(self, soup):
        node = soup.select_one(self._TITLE_SELECTOR)
        for _ in range(3):  # the location <p> is a sibling of the title block or of its parent
            if node is None:
                break
            if p := node.find_next_sibling("p"):
                return self._text(p)
            node = node.parent
        return None
 
 
# --------------------------------------------------------------------------- #
# Dispatch by domain (same idea as the email normalizers)
# --------------------------------------------------------------------------- #
 
# _EXTRACTORS: dict[str, type[BaseJobPageExtractor]] = {
#     "glassdoor.com": GlassdoorJobPageExtractor,
#     "ziprecruiter.com": ZipRecruiterJobPageExtractor,
# }
 
 
# def get_job_page_extractor(url: str) -> BaseJobPageExtractor | None:
#     host = (urlparse(url).hostname or "").lower()
#     for domain, cls in _EXTRACTORS.items():
#         if host == domain or host.endswith("." + domain):
#             return cls()
#     return None