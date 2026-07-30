import pytest

from app.core.config import settings
from app.mail.detector import detect_job_email
from app.mail.imap import connect_imap, fetch_message, search_messages
from app.mail.models import EmailProvider
from app.mail.parser import parse_email
from app.mail.providers.icloud import create_icloud_settings


@pytest.fixture
def icloud_connection():
    settings_obj = create_icloud_settings(
        username=settings.icloud_username,
        password=settings.icloud_password,
    )

    connection = connect_imap(settings_obj)

    yield connection

    try:
        connection.logout()
    except Exception:
        pass

    
@pytest.mark.integration
@pytest.mark.skipif(settings.icloud_username is None, reason="iCloud credentials not configured")
def test_connect_to_real_icloud(icloud_connection):


    assert icloud_connection is not None
    assert icloud_connection.state == "AUTH"




@pytest.mark.integration
@pytest.mark.skipif(
    settings.icloud_username is None,
    reason="iCloud credentials not configured",
)

def test_mailbox_search_after_connection(icloud_connection):
   
    ids = search_messages(icloud_connection)

    assert isinstance(ids, list)
    assert len(ids) > 0

    assert isinstance(ids[0], bytes)



@pytest.mark.integration
@pytest.mark.skipif(
    settings.icloud_username is None,
    reason="iCloud credentials not configured",
)
def test_message_fetch_after_connection(icloud_connection):
   
    ids = search_messages(icloud_connection)

    raw_email = fetch_message(icloud_connection, ids[0])

    assert isinstance(raw_email, bytes)
    assert len(raw_email) > 0

    email = parse_email(
        raw_email,
        EmailProvider.ICLOUD,
    )

    assert email is not None
    assert email.provider == EmailProvider.ICLOUD
    assert email.message_id
    assert email.sender
    assert email.received_at


@pytest.mark.integration
@pytest.mark.skipif(
    settings.icloud_username is None,
    reason="iCloud credentials not configured",
)
def test_detect_real_email(icloud_connection):
   
    ids = search_messages(icloud_connection)

    raw_email = fetch_message(icloud_connection, ids[0])

    email = parse_email(
        raw_email,
        EmailProvider.ICLOUD,
    )

    result = detect_job_email(email)

    assert result is not None
    assert isinstance(result.is_job, bool)
    assert isinstance(result.score, int)
    



"""
Run individual tests
uv run pytest tests/test_jobs_api.py
make test TEST=tests/test_jobs_api.py
uv run pytest -s (to show print statements for passing tests)
uv run pytest -s tests/test_jobs_api.py (to show print statements for passing tests)
uv run pytest tests/test_mail_service.py::test_detect_job_email_true (to run specific test)
"""