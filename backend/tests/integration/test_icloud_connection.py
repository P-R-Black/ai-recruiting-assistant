import pytest

from app.core.config import settings
from app.mail.imap import connect_imap
from app.mail.providers.icloud import create_icloud_settings

if not settings.icloud_username:
    pytest.skip("iCloud credentials not configured")
else:
    def test_connect_to_real_icloud():

        icloud_settings = create_icloud_settings(
            username=settings.icloud_username,
            password=settings.icloud_password,
        )
        
        print("icloud_settings:", icloud_settings)

        connection = connect_imap(icloud_settings)

        print("Connected!")

        connection.logout()

        print("Logged out!")



"""
Run individual tests
uv run pytest tests/test_jobs_api.py
make test TEST=tests/test_jobs_api.py
uv run pytest -s (to show print statements for passing tests)
uv run pytest -s tests/test_jobs_api.py (to show print statements for passing tests)
uv run pytest tests/test_mail_service.py::test_detect_job_email_true (to run specific test)
"""