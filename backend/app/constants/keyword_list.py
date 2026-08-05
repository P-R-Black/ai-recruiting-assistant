import re

REMOTE_KEYWORDS = [
    "remote",
    "work from home",
    "fully remote",
    "100% remote",
    "WFM",
]

HYBRID_KEYWORDS = [
    "hybrid",
    "hybrid schedule",
    "hybrid work",
]

ONSITE_KEYWORDS = [
    "on-site",
    "onsite",
    "in office",
    "office based",
]

JOB_KEYWORDS = [
    "job",
    "jobs",
    "position",
    "opportunity",
    "career",
    "careers",
    "apply",
    "application",
    "interview",
    "recruiter",
    "recruiting",
    "hiring",
]

JOB_SITE_PREFIXES = [
    "jobs",
    "positions",
    "opportunities",
    "careers",
    "apply",
    "recruit",
    "recruiting",
    "hiring",
    "email"
]

FREE_EMAIL_PROVIDERS = [
    "gmail.com",
    "hotmail.com",
    "outlook.com",
    "icloud.com",
    "me.com",
    "yahoo.com",
    "aol.com",
]

RECRUITER_KEYWORDS = [
    "recruit",
    "recruiter",
    "talent",
    "career",
    "careers",
    "hiring",
    "jobs",
    "staffing",
    "hr",
    "humanresources",
    
]

RECRUITER_TITLE_KEYWORDS = [
    "recruiter",
    "talent acquisition",
    "talent partner",
    "technical recruiter",
    "senior recruiter",
    "staff recruiter",
    "recruiting coordinator",
    "human resources",
    "hr",
]

JOB_BOARD_DOMAINS = {
    "linkedin.com": 5,
    "indeed.com": 5,
    "glassdoor.com": 5,
    "greenhouse.io": 4,
    "lever.co": 4,
    "ashbyhq.com": 4,
    "workday.com": 3,
}


SALARY_KEYWORDS = [
    "salary",
    "$",
    "usd",
    "per year",
    "/year",
    "annual",
    "compensation",
]

REJECTION_KEYWORDS = [
    "unfortunately",
    "we regret",
    "not moving forward",
    "another candidate",
    "other candidates",
    "position has been filled",
    "thank you for your interest",
    "we appreciate your interest",
    "we have decided",
    "we will not",
    "declined",
]

UNSUBSCRIBE_KEYWORDS = [
    "unsubscribe",
    "manage preferences",
    "email preferences",
    "stop receiving",
    "opt out",
]

FULL_TIME_KEYWORDS = [
    "full time",
    "full-time",
]

PART_TIME_KEYWORDS = [
    "part time",
    "part-time",
]

CONTRACT_KEYWORDS = [
    "contract",
    "contractor",
]

TEMPORARY_KEYWORDS = [
    "temporary",
    "temp",
]

INTERNSHIP_KEYWORDS = [
    "intern",
    "internship",
]

FREELANCE_KEYWORDS = [
    "freelance",
]


APPLY_URL_KEYWORDS = {
    "apply",
    "job",
    "jobs",
    "career",
    "careers",
    "position",
    "opening",
    "opportunity",
}

NON_APPLY_URL_KEYWORDS = {
    "unsubscribe",
    "privacy",
    "preferences",
    "settings",
    "facebook",
    "twitter",
    "linkedin",
    "instagram",
    "view",
    "browser",
}

NON_PERSON_WORDS = {
    "Team",
    "Careers",
    "Recruiting",
    "Hiring",
    "Talent",
    "Human",
    "Resources",
}


JOB_EMAIL_THRESHOLD = 3
URL_PATTERN = re.compile(r"https?://\S+")