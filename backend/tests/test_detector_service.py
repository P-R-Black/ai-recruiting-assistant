from datetime import datetime, timezone

from app.mail.detector import (
    calculate_job_board_sender_score,
    calculate_job_keyword_score,
    calculate_recruiter_sender_score,
    calculate_rejection_score,
    calculate_unsubscribe_score,
    detect_job_email,
)
from app.mail.models import EmailProvider
from app.mail.schemas import EmailCreate
from app.mail.service import JOB_EMAIL_THRESHOLD


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



def test_job_keyword_score_application():
    text = "Your application has been received."

    assert calculate_job_keyword_score(text) >= 1


def test_job_keyword_score_interview():
    text = "Interview Invitation"

    assert calculate_job_keyword_score(text) >= 1


def test_job_keyword_score_non_job():
    text = "Amazon Order Confirmation"

    assert calculate_job_keyword_score(text) == 0


def test_job_keyword_score_empty():
    assert calculate_job_keyword_score("") == 0

def test_recruiter_sender_score_company_recruiter():
    sender = "Talent Team <talent@google.com>"

    assert calculate_recruiter_sender_score(sender) >= 3


def test_recruiter_sender_score_company_employee():
    sender = "Jane Smith <jane@google.com>"

    assert calculate_recruiter_sender_score(sender) == 1


def test_recruiter_sender_score_gmail():
    sender = "John <john@gmail.com>"

    assert calculate_recruiter_sender_score(sender) == 0


def test_recruiter_sender_score_recruiter_gmail():
    sender = "Recruiter <recruiter@gmail.com>"

    assert calculate_recruiter_sender_score(sender) == 2

def test_job_board_score_linkedin():
    sender = "LinkedIn <jobs@linkedin.com>"

    assert calculate_job_board_sender_score(sender) == 5


def test_job_board_score_subdomain():
    sender = "LinkedIn <alerts@mail.linkedin.com>"

    assert calculate_job_board_sender_score(sender) == 5


def test_job_board_score_greenhouse():
    sender = "Greenhouse <jobs@greenhouse.io>"

    assert calculate_job_board_sender_score(sender) == 4


def test_job_board_score_unknown():
    sender = "Apple <jobs@apple.com>"

    assert calculate_job_board_sender_score(sender) == 0


def test_detect_job_email_true():
    email = EmailCreate(
        provider=EmailProvider.APPLE,
        message_id="1",
        subject="Interview Invitation",
        sender="Talent Team <talent@google.com>",
        recipient="paul@example.com",
        received_at=datetime.now(timezone.utc),
        raw_body="We would like to schedule an interview.",
    )

    result = detect_job_email(email)

    assert result.is_job is True
    assert result.score >= 3


def test_detect_job_email_false():
    email = EmailCreate(
        provider=EmailProvider.APPLE,
        message_id="1",
        subject="Amazon Order Confirmation",
        sender="orders@amazon.com",
        recipient="paul@example.com",
        received_at=datetime.now(timezone.utc),
        raw_body="Your package has shipped.",
    )

    result = detect_job_email(email)

    assert result.is_job is False
    assert result.score < 3


def test_detect_job_email_returns_reasons():
    email = EmailCreate(
        provider=EmailProvider.APPLE,
        message_id="<123@example.com>",
        subject="Software Engineer",
        sender="jobs@linkedin.com",
        recipient="paul@example.com",
        received_at=datetime.now(timezone.utc),
        raw_body="Apply now",
    )

    result = detect_job_email(email)

    assert len(result.reasons) > 0
    assert any("Job board" in reason for reason in result.reasons)

def test_detect_job_email_linkedin():
    email = EmailCreate(
        provider=EmailProvider.APPLE,
        message_id="<123@example.com>",
        subject="Junior Python Developer",
        sender="LinkedIn <jobs-noreply@linkedin.com>",
        recipient="paul@example.com",
        received_at=datetime.now(timezone.utc),
        raw_body="Apply now!",
    )

    result = detect_job_email(email)

    assert result.is_job is True
    assert result.score >= JOB_EMAIL_THRESHOLD
    assert len(result.reasons) > 0


def test_detect_job_email_linkedin_jobalerts():
    email = EmailCreate(
        provider=EmailProvider.APPLE,
        message_id="<123@example.com>",
        subject="Junior Python Developer",
        sender="LinkedIn <jobalerts-noreply@linkedin.com>",
        recipient="paul@example.com",
        received_at=datetime.now(timezone.utc),
        raw_body="Apply now!",
    )

    result = detect_job_email(email)

    assert result.is_job is True
    assert result.score >= JOB_EMAIL_THRESHOLD
    assert any(
        "Job board" in reason
        for reason in result.reasons
    )

def test_detect_job_email_glassdoor():
    email = EmailCreate(
        provider=EmailProvider.APPLE,
        message_id="<123@example.com>",
        subject="Software Engineer",
        sender="Glassdoor <jobs@glassdoor.com>",
        recipient="paul@example.com",
        received_at=datetime.now(timezone.utc),
        raw_body="Apply now!",
    )

    result = detect_job_email(email)

    assert result.is_job is True
    assert result.score >= JOB_EMAIL_THRESHOLD
    assert any(
        "Job board" in reason
        for reason in result.reasons
    )
    


def test_detect_job_email_indeed():
    email = EmailCreate(
        provider=EmailProvider.APPLE,
        message_id="<123@example.com>",
        subject="Junior Software Engineer",
        sender="Indeed <donotreply@match.indeed.com>",
        recipient="paul@example.com",
        received_at=datetime.now(timezone.utc),
        raw_body="Apply now!",
    )

    result = detect_job_email(email)

    assert result.is_job is True
    assert result.score >= JOB_EMAIL_THRESHOLD
    assert len(result.reasons) > 0


def test_detect_job_email_recruiter():
    email = EmailCreate(
        provider=EmailProvider.APPLE,
        message_id="<123@example.com>",
        subject="Frontend Developer",
        sender="Talent Team <talent@google.com>",
        recipient="paul@example.com",
        received_at=datetime.now(timezone.utc),
        raw_body="Apply now!",
    )

    result = detect_job_email(email)

    assert result.is_job is True
    assert result.score >= JOB_EMAIL_THRESHOLD
    assert len(result.reasons) > 0


def test_detect_job_email_false_positive():
    email = EmailCreate(
        provider=EmailProvider.APPLE,
        message_id="<123@example.com>",
        subject="Amazon Order Confirmation",
        sender="orders@amazon.com",
        recipient="paul@example.com",
        received_at=datetime.now(timezone.utc),
        raw_body="Your package has shipped",
    )

    result = detect_job_email(email)

    assert result.is_job is False
    assert result.score < JOB_EMAIL_THRESHOLD


def test_detect_job_email_empy():
    email = EmailCreate(
        provider=EmailProvider.APPLE,
        message_id="<123@example.com>",
        subject="",
        sender="",
        recipient="paul@example.com",
        received_at=datetime.now(timezone.utc),
        raw_body="",
    )

    result = detect_job_email(email)

    assert result.is_job is False
    assert result.score < JOB_EMAIL_THRESHOLD


def test_threshold_job_threshold():
    email = EmailCreate(
        provider=EmailProvider.APPLE,
        message_id="<123@example.com>",
        subject="Junior Frontend Developer",
        sender="Talent Team <talent@google.com>",
        recipient="paul@example.com",
        received_at=datetime.now(timezone.utc),
        raw_body="",
    )
    result = detect_job_email(email)

    assert result.score == JOB_EMAIL_THRESHOLD
    assert result.is_job is True


def test_calculate_rejection_score():
    email = sample_job_email()

    searchable = " ".join([
        email.subject,
        email.raw_body,
    ])

    result = calculate_rejection_score(searchable)
    
    assert result == 0


def test_calculate_unsubscribe_score():
    email = sample_job_email()

    searchable = " ".join([
        email.subject,
        email.raw_body,
    ])

    result = calculate_unsubscribe_score(searchable)
    
    assert result == 0

