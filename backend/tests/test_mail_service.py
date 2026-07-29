import uuid
import pytest
from uuid import UUID

from copy import deepcopy
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from email.message import EmailMessage
from app.mail.schemas import EmailCreate, EmailProvider
from app.mail.models import EmailProvider

from app.mail.crud import (
    create_email, get_email, list_emails, update_email, 
    delete_email, get_email_by_message_id, mark_email_processed,
)


from app.mail.service import (
    IMAPSettings, JOB_EMAIL_THRESHOLD
    )



# from app.mail.detector import
# from app.mail.importer import
# from app.mail.imap import
# from app.mail.gmail import connect_gmail

"""
All Test


 6. 


 9. test_job_keyword_score_application
10. test_job_keyword_score_interview
11. test_job_keyword_score_non_job
12. test_job_keyword_score_empty
13. test_recruiter_sender_score_company_recruiter
14. test_recruiter_sender_score_company_employee
15. test_recruiter_sender_score_gmail
16. test_recruiter_sender_score_recruiter_gmail
17. test_job_board_score_linkedin
18. test_job_board_score_subdomain
19. test_job_board_score_greenhouse
20. test_job_board_score_unknown


25. test_search_messages
26. test_search_messages_empty
27. test_search_messages_select_failure
28. test_fetch_message
29. test_fetch_message_failure
30. test_fetch_message_empty
31. test_fetch_imap_messages
32. test_detect_job_email_linkedin
33. test_detect_job_email_linkedin_jobalerts
34. test_detect_job_email_glassdoor
35. test_detect_job_email_indeed
36. test_detect_job_email_recruiter
37. test_detect_job_email_false_positive
38. test_detect_job_email_empy
39. test_threshold_job_threshold

48.
49.
50.
51.
52.
53.
54.
55.
56.
57.
58.
59.
60.
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