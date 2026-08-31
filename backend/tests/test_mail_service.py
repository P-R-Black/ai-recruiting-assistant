
from datetime import datetime, timezone

from app.mail.models import EmailProvider
from app.mail.schemas import EmailCreate


"""
All Test
 1. sample_job_email
"""

def sample_job_email() -> EmailCreate:
    return EmailCreate(
        provider=EmailProvider.APPLE,
        message_id="<123@example.com>",
        subject="Junior Frontend Developer",
        sender="Talent Team <talent@google.com>",
        recipient="paul@example.com",
        received_at=datetime.now(timezone.utc),
        raw_body="""
            Junior Frontend Developer

            OpenAI

            Orlando, FL

            Salary: $180,000 - $220,000

            Apply here:
            https://jobs.openai.com/12345
            """,
                )




"""
Run individual tests
uv run pytest tests/test_jobs_api.py
make test TEST=tests/test_jobs_api.py
uv run pytest -s (to show print statements for passing tests)
uv run pytest -s tests/test_jobs_api.py (to show print statements for passing tests)
uv run pytest tests/test_mail_service.py::test_detect_job_email_true (to run specific test)
"""