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

from bs4 import BeautifulSoup

from app.job_page.normalizer.normalizer import normalize_parsed_description
from app.job_page.parsers.base import BaseJobPageExtractor
from app.job_page.parsers.helpers.common import (
    Candidate,
    build_candidates,
    clean_text,
    find_job_posting,
)
from app.job_page.schema import JobPageResponse

# --------------------------------------------------------------------------- #
# Extractor interface + Glassdoor implementation
# --------------------------------------------------------------------------- #

class GlassdoorJobPageExtractor(BaseJobPageExtractor):
    # Glassdoor's CSS classes are hashed (JobDetails_jobDescription__uW_fK), so
    # match on the stable prefix / data-test attributes instead of full class names.
    _DESCRIPTION_SELECTOR = '[class*="JobDetails_jobDescription"]'
    _LOCATION_SELECTOR = '[data-test="location"]'
    _TITLE_SELECTOR = 'h1[id^="jd-job-title"]'
    _COMPANY_SELECTOR = '[class*="EmployerProfile_employerNameHeading"] h4'
 
    def extract(self, page: JobPageResponse) -> JobPageResponse:
        if page.status_code != 200 or not page.html:
            return page
 
        soup = BeautifulSoup(page.html, "html.parser")
        posting = find_job_posting(soup)
        candidates = self.candidates(soup, posting)
        
        # ties -> first
        best = max(candidates, key=lambda c: c.score) if candidates else None  

        # Normalize only the winning candidate's description, if any. This is important because the
        # normalization process can be lossy, and we don't want to lose any information from the
        # other candidates.
   
        parsed = (
            normalize_parsed_description(best.parsed)
            if best
            else None
        )


        updates = {
            "title": self._title(soup, posting) or page.title,
            "company": self._company(soup, posting) or page.company,
            "location": self._location(soup, posting) or page.location,
            "extraction_method": best.method if best else None,
        }
        if parsed:
            updates.update(
                description=parsed.description,
                responsibilities=parsed.responsibilities,
                required_qualifications=parsed.required_qualifications,
                preferred_qualifications=parsed.preferred_qualifications,
            )

    
        return page.model_copy(update=updates)
 
    def candidates(self, soup: BeautifulSoup, posting: dict | None) -> list[Candidate]:
        """Every (source x strategy) result with its score. Useful for debugging."""
        sources: list[tuple[str, str]] = []
        if posting and posting.get("description"):
            sources.append(("json-ld", posting["description"]))
        if node := soup.select_one(self._DESCRIPTION_SELECTOR):
            sources.append(("dom", node.decode_contents()))
        
        return build_candidates(sources)
 
    def _title(self, soup, posting) -> str | None:
        if posting and posting.get("title"):
            return clean_text(posting["title"])
        node = soup.select_one(self._TITLE_SELECTOR)
        return clean_text(node.get_text()) if node else None
 
    def _company(self, soup, posting) -> str | None:
        org = (posting or {}).get("hiringOrganization") or {}
        if isinstance(org, dict) and org.get("name"):
            return clean_text(org["name"])
        node = soup.select_one(self._COMPANY_SELECTOR)
        return clean_text(node.get_text()) if node else None
 
    def _location(self, soup, posting) -> str | None:
        # Prefer the on-page badge ("Eden Prairie, MN"); JSON-LD only has the
        # full state name ("Minnesota").
        if node := soup.select_one(self._LOCATION_SELECTOR):
            return clean_text(node.get_text())
        place = (posting or {}).get("jobLocation")
        place = place[0] if isinstance(place, list) and place else place
        address = (place or {}).get("address") or {}
        parts = [address.get("addressLocality"), address.get("addressRegion")]
        return ", ".join(p for p in parts if p) or None

