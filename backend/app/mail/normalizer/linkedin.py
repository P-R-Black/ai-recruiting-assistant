
import re

from bs4 import BeautifulSoup

from app.mail.normalizer.base import BaseEmailNormalizer, NormalizedJob, ParsedEmail, email_metadata

LINKEDIN_JOB_URL_PATTERN = re.compile(r"/jobs/view/(\d+)/")


class LinkedInNormalizer(BaseEmailNormalizer):
    def normalize(
            self,
            email: ParsedEmail,
    ) -> list[NormalizedJob]:

        
        if email.html_body is None:
            return []

        return extract_linkedin_jobs(email)


def extract_linkedin_jobs(email: ParsedEmail) -> list[NormalizedJob]:
    if email is None or email.html_body is None:
        return []

    soup = BeautifulSoup(email.html_body, "html.parser")
    metadata = email_metadata(email)
    jobs = []
    seen_job_ids = set()

    for link in soup.find_all("a", href=True):
        match = LINKEDIN_JOB_URL_PATTERN.search(link["href"])
        if not match:
            continue

        job_id = match.group(1)
        if job_id in seen_job_ids:
            continue

        # Only claim this job_id once we've confirmed this anchor actually
        # contains the title - a company-logo-only anchor (present in the
        # jobalerts-noreply template) will fail this check and get skipped,
        # letting the real card anchor right after it get picked up instead.
        title_el = link.find(class_="font-bold")
        if title_el is None:
            continue
        seen_job_ids.add(job_id)

        title = title_el.get_text(strip=True)
        job_link = title_el.get("href") or link["href"]

        company, location = None, None
        info_p = link.find("p", class_="text-system-gray-100")
        if info_p:
            parts = [p.strip() for p in info_p.get_text(strip=True).split("·")]
            company = parts[0] if len(parts) > 0 else None
            location = parts[1] if len(parts) > 1 else None

        salary_p = link.find("p", class_="text-system-gray-70")
        salary_raw = salary_p.get_text(strip=True) if salary_p else None
        # parsed_salary = parse_salary(salary_raw)

        jobs.append(
             NormalizedJob(
                title=title,
                company=company,
                location=location,
                salary=salary_raw,
                job_url=job_link,
                **metadata
                )
        )
    return jobs

    # if email is None or email.html_body is None:
    #     return []

    # soup = BeautifulSoup(email.html_body, "html.parser")
    # metadata = email_metadata(email)
    # jobs = []

    # for card in soup.find_all("td", attrs={"data-test-id": "job-card"}):
    #     title_link = card.find("a", class_="font-bold")
    #     if title_link is None:
    #         continue

    #     title = title_link.get_text(strip=True)
    #     job_url = title_link.get("href")

    #     company, location = None, None
    #     info_p = card.find("p", class_="text-system-gray-100")
    #     if info_p:
    #         # LinkedIn separates company/location with a middle dot "·"
    #         # (U+00B7) - distinct from ZipRecruiter's bullet "•" (U+2022)
    #         parts = [p.strip() for p in info_p.get_text(strip=True).split("·")]
    #         company = parts[0] if len(parts) > 0 else None
    #         location = parts[1] if len(parts) > 1 else None

    #     salary_p = card.find("p", class_="text-system-gray-70")
    #     salary_raw = salary_p.get_text(strip=True) if salary_p else None
    #     if salary_raw:
    #         parsed_salary = parse_salary(salary_raw)
    #     else:
    #         parsed_salary ="?"
    #     # print('parsed_salary', parsed_salary if salary_raw else "No Salary Data")

        # jobs.append(
        #      NormalizedJob(
        #         title=title,
        #         company=company,
        #         location=location,
        #         salary=salary_raw,
        #         job_url=job_url,
        #         **metadata
        #         )
        # )
    # return jobs








# def extract_linkedin_jobs_two(email: ParsedEmail) -> list[NormalizedJob]:
#     if email is None or email.html_body is None:
#         return []

#     soup = BeautifulSoup(email.html_body, "html.parser")
#     metadata = email_metadata(email)
#     jobs = []
#     seen_job_ids = set()

#     for link in soup.find_all("a", href=True):
#         match = LINKEDIN_JOB_URL_PATTERN.search(link["href"])
#         print('match:', match)
#         if not match:
#             continue

#         job_id = match.group(1)
#         if job_id in seen_job_ids:
#             # Some LinkedIn templates nest a second <a> (the title link) with
#             # the same job id inside the outer card-wrapping <a> - keep only
#             # the first (outer) occurrence, which contains the full card.
#             continue
#         seen_job_ids.add(job_id)

#         # Title is an <a> in some templates, a <div> in others - both use
#         # the same "font-bold" class, so search by class with no tag restriction
#         title_el = link.find(class_="font-bold")
#         if title_el is None:
#             continue
#         title = title_el.get_text(strip=True)
#         job_link = title_el.get("href") or link["href"]

#         company, location = None, None
#         info_p = link.find("p", class_="text-system-gray-100")
#         if info_p:
#             parts = [p.strip() for p in info_p.get_text(strip=True).split("·")]
#             company = parts[0] if len(parts) > 0 else None
#             location = parts[1] if len(parts) > 1 else None

#         salary_p = link.find("p", class_="text-system-gray-70")
#         salary_raw = salary_p.get_text(strip=True) if salary_p else None
#         parsed_salary = parse_salary(salary_raw)

#         jobs.append(
#             NormalizedJob(
#             title=title,
#             company=company,
#             location=location,
#             salary=salary_raw,
#             job_url=job_link,
#             **metadata
#             )
#         )
#     return jobs