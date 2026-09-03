from pathlib import Path

from app.core.database import SessionLocal
from app.jobs.jobs_services.service import persist_normalized_jobs
from app.mail.mail_services.mime_parser import build_parsed_email
from app.mail.models import EmailProvider
from app.mail.normalizer.glassdoor import GlassdoorNormalizer

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent

FIXTURES_DIR = (
    BACKEND_DIR
    / "tests"
    / "mail"
    / "normalizer"
    / "fixtures"
    / "emails"
)

print('FIXTURES_DIR:', FIXTURES_DIR)
def load_fixture(filename: str) -> bytes:
    fixture_path = FIXTURES_DIR / filename

    return fixture_path.read_bytes()


def seed_glassdoor_jobs() -> None:
    raw_email = load_fixture(
        "glassdoor_multiple_jobs.eml"
    )

    parsed = build_parsed_email(
        raw_email,
        EmailProvider.ICLOUD,
    )

    jobs = GlassdoorNormalizer().normalize(parsed)

    db = SessionLocal()

    try:
        created_jobs = persist_normalized_jobs(db, jobs)

        print(
            f"Glassdoor: created {len(created_jobs)} jobs"
        )

    finally:
        db.close()


if __name__ == "__main__":
    seed_glassdoor_jobs()


"""
uv run python -m app.scripts.seed_jobs
"""