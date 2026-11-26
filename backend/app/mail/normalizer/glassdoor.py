
from bs4 import BeautifulSoup

from app.mail.normalizer.base import BaseEmailNormalizer, NormalizedJob, ParsedEmail, email_metadata


class GlassdoorNormalizer(BaseEmailNormalizer):
    def normalize(
            self,
            email: ParsedEmail,
    ) -> list[NormalizedJob]:
 
        if email.html_body is None:
            return []
        
        return extract_glassdoor_jobs(email)



def extract_glassdoor_jobs(email: ParsedEmail) -> list[NormalizedJob]:

    soup = BeautifulSoup(email.html_body, "html.parser")
    metadata = email_metadata(email)
    jobs = []

  
    for link in soup.find_all("a", href=True):
        if "jobListing.htm" not in link["href"]:
            continue  # skip "related jobs" links, footer links, etc.

        p_tags = link.find_all("p")
        if not p_tags:
            continue

        title = p_tags[0].get_text(strip=True)
        location = p_tags[1].get_text(strip=True) if len(p_tags) > 1 else None
        salary = p_tags[2].get_text(strip=True) if len(p_tags) > 2 else None
       
        company = None
        for span in link.find_all("span"):
            text = span.get_text(strip=True)
            if not text or "★" in text:
                continue
            company = text
            break

        jobs.append(
            NormalizedJob(
                title=title,
                company=company,
                location=location,
                salary=salary,
                job_url=link["href"],
                **metadata
            )
        )
    return jobs


def matches_keywords(title: str, keywords: list[str]) -> bool:
    title_lower = title.lower()
    return any(kw.lower() in title_lower for kw in keywords)


# Map sender domain -> board identifier
KNOWN_JOB_BOARDS = {
    "glassdoor.com": "glassdoor",
    "linkedin.com": "linkedin",
    "indeed.com": "indeed",
    "match.indeed.com":"indeed",
    # Indeed sometimes sends from this domain instead
    "indeedemail.com": "indeed",      
    "ziprecruiter.com": "ziprecruiter",

}
