
from email.message import EmailMessage

from app.mail.models import EmailProvider
from app.mail.mail_services.parser import (
    extract_html, extract_message_body, extract_plain_text, parse_email)



"""
All Test
 1. test_parse_email
 2. test_extract_plain_text
 3. test_extract_message_body_prefers_plain_text
 4. test_extract_message_body_uses_html_when_no_plain
 5. test_extract_html
"""


def test_parse_email():
    raw_email = (
    b"From: recruiter@example.com\r\n"
    b"To: paul@example.com\r\n"
    b"Subject: Python Developer\r\n"
    b"Message-ID: <123@example.com>\r\n"
    b"Date: Sat, 19 Jul 2026 15:30:00 +0000\r\n"
    b"Content-Type: text/plain; charset=utf-8\r\n"
    b"\r\n"
    b"We would like to interview you."
    )
    email = parse_email(raw_email, EmailProvider.APPLE)


    assert email.provider == EmailProvider.APPLE
    assert email.message_id == "<123@example.com>"
    assert email.subject == "Python Developer"
    assert email.sender == "recruiter@example.com"
    assert email.recipient == "paul@example.com"
    assert "interview" in email.raw_body

def test_extract_plain_text():
    msg = EmailMessage()
    msg.set_content("Hello from plain text")
    text = extract_plain_text(msg)

    assert text.strip() == "Hello from plain text"


def test_extract_message_body_prefers_plain_text():
    msg = EmailMessage()

    msg.set_content("Plain text body")

    msg.add_alternative(
        "<html><body>HTML Body</body></html>",
        subtype="html",
    )

    body = extract_message_body(msg)

    assert body.strip() == "Plain text body"


def test_extract_message_body_uses_html_when_no_plain():
    msg = EmailMessage()

    msg.add_alternative(
        "<html><body>Only HTML</body></html>",
        subtype="html",
    )

    body = extract_message_body(msg)

    assert "Only HTML" in body


def test_extract_html():
    msg = EmailMessage()
    msg.add_alternative(
        "<html><body><h1>Hello HTML</h1></body></html>", subtype="html",
    )

    html = extract_html(msg)
    assert "<h1>Hello HTML</h1>" in html