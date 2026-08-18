
import hashlib

from app.mail.mail_services.service import ExtractJob


def normalize_for_fingerprint(value: str | None) -> str:
    if not value:
        return ""

    return " ".join(value.lower().split())


def calculate_job_fingerprint(extracted: ExtractJob) -> str:
    parts = [
        normalize_for_fingerprint(extracted.company),
        normalize_for_fingerprint(extracted.title),
        normalize_for_fingerprint(extracted.location),
        extracted.employment_type.value,
        extracted.work_location.value,
    ]

    fingerprint_source = "|".join(parts)
    return hashlib.sha256(
        fingerprint_source.encode("utf-8")
    ).hexdigest()
