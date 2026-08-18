
from bs4 import BeautifulSoup

from app.mail.normalizer.base import BaseEmailNormalizer, NormalizedJob, ParsedEmail


class IndeedNormalizer(BaseEmailNormalizer):
    def normalize(
            self,
            email: ParsedEmail,
    ) -> list[NormalizedJob]:

        if email.html_body is None:
            return []
        
        return extract_indeed_jobs(email.html_body)

    

def extract_indeed_jobs(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    # Indeed tags the job title link with this specific class
    title_links = soup.find_all("a", class_="strong-text-link")

    for title_link in title_links:
        title = title_link.get_text(strip=True)
        url = title_link.get("href")

        company, location = None, None
        h2 = title_link.find_parent("h2")
        if h2:
            title_row = h2.find_parent("tr")
            # company/location live in the very next table row
            info_row = title_row.find_next_sibling("tr") if title_row else None
            if info_row:
                p_tags = info_row.find_all("p")
                company = p_tags[0].get_text(strip=True) if len(p_tags) > 0 else None
                location = p_tags[1].get_text(strip=True) if len(p_tags) > 1 else None

        # jobs.append({
        #     "title": title,
        #     "company": company,
        #     "location": location,
        #     "url": url,
        # })
        jobs.append(
            NormalizedJob(
                title=title,
                company=company,
                location=location,
                salary=None,
                job_url=url,
            )
        )

    return jobs

"""
Indeed Example 1 Email
[NormalizedJob(
title='Staff Frontend Software Engineer', 
company='Clerk AI', 
location='Remote', 
salary=None, 
job_url='https://cts.indeed.com...')]
"""