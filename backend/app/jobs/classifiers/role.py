from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel

from app.mail.normalizer.base import NormalizedJob

if TYPE_CHECKING:
    pass


SOFTWARE_KEYWORDS = (
    "application developer",
    "application engineer",
    "frontend developer",
    "full stack developer",
    "full-stack developer",
    "software developer",
    "software engineer",
    "web developer",
    "web engineer",
   
)

FRONTEND_KEYWORDS = (
    "frontend",
    "front end",
    "front-end",
    "react",
    "ui developer",
    "ui engineer"

)

BACKEND_KEYWORDS = (
    "api developer",
    "api engineer",
    "backend",
    "back end",
    "django developer",
    "node developer",
    "node.js developer",
    "python developer",
    "python engineer",
    "server developer",
    "server engineer",
    "server-side",
)

NON_SOFTWARE_KEYWORDS = (
    "civil engineer",
    "civil-engineer",
    "industrial designer",
    "industrial-designer",
    "graphic designer",
    "graphic-designer"
)

class JobRoleType(str, Enum):
    NON_SOFTWARE = "non_software"
    FRONTEND = "frontend"
    BACKEND = "backend"
    FULL_STACK = "full_stack"
    SOFTWARE = "software"
    SOFTWARE_ENGINEER = "software_engineer"
    UNKNOWN = "unknown"


class ResumeRecommendation(str, Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    FULL_STACK = "full_stack"
    NON_SOFTWARE = "non_software"
    UNKNOWN = "unknown"



class JobClassification(BaseModel):
    is_relevant: bool
    role_type: JobRoleType
    recommended_resume: ResumeRecommendation


def classify_job_title(title:str) -> JobRoleType:
    title = title.lower()

    if any(term in title for term in FRONTEND_KEYWORDS):
        return JobRoleType.FRONTEND

    if any(term in title for term in BACKEND_KEYWORDS):
        return JobRoleType.BACKEND

    if "full stack" in title or "full-stack" in title:
        return JobRoleType.FULL_STACK
    
    if any(term in title for term in SOFTWARE_KEYWORDS):
        return JobRoleType.SOFTWARE_ENGINEER

    if any(term in title for term in NON_SOFTWARE_KEYWORDS):
            return JobRoleType.NON_SOFTWARE
    


    return JobRoleType.UNKNOWN


def classify_job(normalized: NormalizedJob) -> JobClassification:
    role_type = classify_job_title(normalized.title)
    print('role_type:', role_type)

    resume_map = {
        JobRoleType.FRONTEND: ResumeRecommendation.FRONTEND,
        JobRoleType.BACKEND: ResumeRecommendation.BACKEND,
        JobRoleType.FULL_STACK: ResumeRecommendation.FULL_STACK,
        JobRoleType.SOFTWARE_ENGINEER: ResumeRecommendation.FULL_STACK,
        JobRoleType.SOFTWARE: ResumeRecommendation.FULL_STACK,
        JobRoleType.NON_SOFTWARE: ResumeRecommendation.NON_SOFTWARE,
    }

    recommendation = resume_map.get(
        role_type,
        ResumeRecommendation.UNKNOWN,
    )

    return JobClassification(
        is_relevant=role_type not in {
            JobRoleType.NON_SOFTWARE,
            JobRoleType.UNKNOWN,
        },
        role_type=role_type,
        recommended_resume=recommendation,
    )
        