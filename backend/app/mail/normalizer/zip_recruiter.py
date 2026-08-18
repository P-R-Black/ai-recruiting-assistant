
from bs4 import BeautifulSoup

from app.mail.normalizer.base import BaseEmailNormalizer, NormalizedJob, ParsedEmail


class ZipRecruiterNormalizer(BaseEmailNormalizer):
    def normalize(
            self,
            email: ParsedEmail,
    ) -> list[NormalizedJob]:

        if email.html_body is None:
            return []
        
        return extract_ziprecruiter_jobs(email.html_body)
    

def extract_ziprecruiter_jobs(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    # ZipRecruiter marks every job title link with this exact class -
    # it's the most reliable anchor in their template
    title_links = soup.find_all("a", class_="no-inline--job-title-link-a")

    for title_link in title_links:
        title = title_link.get_text(strip=True)
        url = title_link.get("href")

        # Walk up to the card container that also holds company/location/salary
        job_card = title_link.find_parent("div", class_="no-inline--two-col-jc")
        if job_card is None:
            continue

        # "Company • Location • Type" lives in the first <p> in the card
        info_p = job_card.find("p")
        company, location = None, None
        if info_p:
            parts = [p.strip() for p in info_p.get_text(strip=True).split("•")]
            company = parts[0] if len(parts) > 0 else None
            location = parts[1] if len(parts) > 1 else None

        # Salary is optional - not every listing has one
        salary_p = job_card.find("p", style=lambda s: s and "padding-right:4px" in s)
        salary = salary_p.get_text(strip=True) if salary_p else None

        # jobs.append({
        #     "title": title,
        #     "company": company,
        #     "location": location,
        #     "salary": salary,
        #     "url": url,
        # })
        jobs.append(
            NormalizedJob(
                title=title,
                company=company,
                location=location,
                salary=salary,
                job_url=url,
            )
        )

    return jobs