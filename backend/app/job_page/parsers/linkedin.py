"""
Phase 2: extract structured details from a fetched job page.
 
Mirrors the email normalizers: one extractor per job board, chosen by domain.
 
Extraction order for each page:
  1. JSON-LD ``JobPosting`` block (stable, machine-readable)  -> extraction_method="json-ld"
  2. Rendered description container in the DOM (fallback)     -> extraction_method="dom"
 
The description HTML is then split into sections by heading text
("Primary Responsibilities:", "Required Qualifications:", ...), and the <li>
items under each heading become list entries.
"""
from __future__ import annotations

import re

from bs4 import BeautifulSoup

from app.job_page.parsers.base import BaseJobPageExtractor
from app.job_page.parsers.helpers.common import (
    Candidate,
    build_candidates,
    clean_text,
    find_job_posting,
)
from app.job_page.schema import JobPageResponse


class LinkedInJobPageExtractor(BaseJobPageExtractor):
    """Public (logged-out) LinkedIn job page: /jobs/view/<id>.
 
    The guest page has no JSON-LD in the snapshot we tested, so the on-page
    description block is the main source; JSON-LD is still tried first in case
    LinkedIn serves it. Headings there are <strong>Responsibilities</strong>
    followed by <ul><li>...</li></ul>, which the shared HTML parser handles.
    """
 
    _DESCRIPTION_SELECTORS = (
        ".show-more-less-html__markup",
        ".description__text--rich",
        ".description__text",
        # signed-in layout (untested)
        ".jobs-description__content .jobs-box__html-content",
        "#job-details",
    )
    _TITLE_SELECTORS = ("h1.top-card-layout__title", "h1.topcard__title", "h1.t-24", "h1")
    _COMPANY_SELECTORS = (
        "a.topcard__org-name-link", ".topcard__flavor:not(.topcard__flavor--bullet)",
                          ".job-details-jobs-unified-top-card__company-name"
                          )
    _LOCATION_SELECTORS = (".topcard__flavor--bullet",)
    _OG_TITLE = re.compile(
        r"^(?P<title>.+?) at (?P<company>.+?)(?: [—–-] (?P<location>.+?))? \| LinkedIn", re.S
        )
    # _DESCRIPTION_LABEL = re.compile(r"^\s*job description\s*$", re.I)
    _DESCRIPTION_LABEL = re.compile(r"^\s*job\s+description\s*$", re.I)
 
    def extract(self, page: JobPageResponse) -> JobPageResponse:
        if page.status_code != 200 or not page.html:
            return page
 
        soup = BeautifulSoup(page.html, "html.parser")
        posting = find_job_posting(soup)
        candidates = self.candidates(soup, posting)
        best = max(candidates, key=lambda c: c.score) if candidates else None  # ties -> first
 
        og = self._og_title(soup)
        updates = {
            "title": self._first_text(soup, self._TITLE_SELECTORS) or (posting or {}).get("title")
                     or og.get("title") or page.title,
            "company": self._first_text(soup, self._COMPANY_SELECTORS)
                       or ((posting or {}).get("hiringOrganization") or {}).get("name")
                       or og.get("company") or page.company,
            "location": self._location(soup) or og.get("location") or page.location,
            "extraction_method": best.method if best else None,
        }
        updates = {k: (clean_text(v) if isinstance(v, str) else v) for k, v in updates.items()}
        if best:
            updates.update(
                description=best.parsed.description,
                responsibilities=best.parsed.responsibilities,
                required_qualifications=best.parsed.required_qualifications,
                preferred_qualifications=best.parsed.preferred_qualifications,
            )
        return page.model_copy(update=updates)
 
    # def candidates(self, soup: BeautifulSoup, posting: dict | None) -> list[Candidate]:
    #     sources: list[tuple[str, str]] = []
    #     if posting and posting.get("description"):
    #         sources.append(("json-ld", posting["description"]))
    #     for selector in self._DESCRIPTION_SELECTORS:
    #         if node := soup.select_one(selector):
    #             sources.append(("dom", node.decode_contents()))
    #             break
    #     return build_candidates(sources)
    
    def candidates(self, soup: BeautifulSoup, posting: dict | None) -> list[Candidate]:
        sources: list[tuple[str, str]] = []

        if posting and posting.get("description"):
            sources.append(("json-ld", posting["description"]))

        if description_html := self._dom_description_html(soup):
            sources.append(("dom", description_html))

        return build_candidates(sources)

    @staticmethod
    def _first_text(soup, selectors) -> str | None:
        for selector in selectors:
            for node in soup.select(selector):
                if text := clean_text(node.get_text(" ")):
                    return text
        return None
 
    def _location(self, soup) -> str | None:
        for node in soup.select(self._LOCATION_SELECTORS[0]):
            text = clean_text(node.get_text(" "))
            if text and "applicant" not in text.lower():
                return text
        return None
 
    def _og_title(self, soup) -> dict:
        meta = soup.find("meta", attrs={"property": "og:title"})
        m = self._OG_TITLE.match(clean_text(meta.get("content", ""))) if meta else None
        return {k: v for k, v in (m.groupdict() if m else {}).items() if v}


    # def _dom_description_html(self, soup):
    #     for heading in soup.find_all(["h2", "h3"]):
    #         if self._DESCRIPTION_LABEL.match(heading.get_text()):
    #             if box := heading.find_next_sibling("div"):
    #                 return box.decode_contents()
    #     return None

    def _dom_description_html(self, soup: BeautifulSoup) -> str | None:
        about_heading = next(
            (
                heading
                for heading in soup.find_all("h2")
                if clean_text(heading.get_text()) == "About the job"
            ),
            None,
        )

        if about_heading is None:
            return None

        description_container = about_heading.parent.parent
        paragraph = description_container.find("p", recursive=False)

        if paragraph is None:
            return None

        expandable = paragraph.select_one(
            '[data-testid="expandable-text-box"]'
        )

        if expandable is None:
            return None

        expand_button = expandable.select_one(
            '[data-testid="expandable-text-button"]'
        )

        if expand_button is not None:
            expand_button.decompose()

        return expandable.decode_contents()
 
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
#     "linkedin.com": LinkedInJobPageExtractor,
#     "ziprecruiter.com": ZipRecruiterJobPageExtractor,
# }
 
 
# def get_job_page_extractor(url: str) -> BaseJobPageExtractor | None:
#     host = (urlparse(url).hostname or "").lower()
#     for domain, cls in _EXTRACTORS.items():
#         if host == domain or host.endswith("." + domain):
#             return cls()
#     return None