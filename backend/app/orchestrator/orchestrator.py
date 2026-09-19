from sqlalchemy.orm import Session

import logging

from app.jobs.jobs_services.service import persist_normalized_jobs

from app.mail.models import EmailProvider

from app.mail.normalizer.base import ParsedEmail
from app.mail.normalizer.glassdoor import GlassdoorNormalizer
from app.mail.normalizer.linkedin import LinkedInNormalizer
from app.mail.normalizer.indeed import IndeedNormalizer
from app.mail.normalizer.zip_recruiter import ZipRecruiterNormalizer

from app.mail.mail_services.parsers.mime_parser import build_parsed_email
from app.mail.mail_services.parsers.graph_parser import build_parsed_email_from_graph_message

from app.mail.filters.job_board_filter import (
    is_job_board_email, 
    identify_job_board
    )

from app.mail.mail_services.deleters.mail_deleter import delete_email
from app.mail.mail_services.parsers.parser import parse_email

from app.mail.connectors.outlook_connector import create_outlook_settings
from app.mail.providers.outlook import (
    connect_outlook, 
    fetch_outlook_messages,
    search_folder, 
    graph_headers)


from app.mail.providers.icloud import (
    create_icloud_settings,
    fetch_imap_message, 
    fetch_imap_messages, 
    search_imap_messages)

from app.mail.connectors.imap_connector import connect_imap


JOB_BOARD_PARSERS = {
    "glassdoor": GlassdoorNormalizer(),
    "linkedin": LinkedInNormalizer(),   
    "indeed": IndeedNormalizer(),
    "ziprecruiter": ZipRecruiterNormalizer(),
}

logger = logging.getLogger(__name__)

def run_imap_ingestion(
        db: Session,
        username: str,
        password: str,
    ) -> None:

    # iCloud flow
    # connect
    settings = create_icloud_settings(
        username=username,
        password=password,
    )

    icloud_connection = connect_imap(settings)
    
    ids = search_imap_messages(icloud_connection)
    

    if ids:
        for imap_uid in ids[-200:]:
            try:
                raw_email = fetch_imap_message(icloud_connection, imap_uid)
            except Exception as e:
                print(f'raw_email Exception: {e}')

            parsed_email = build_parsed_email(raw_email, EmailProvider.ICLOUD)
        
            if not parsed_email:
                continue

            process_email(
                db=db,
                email=parsed_email,
                imap_connection=icloud_connection,
                imap_uid=imap_uid
            )
            




def run_outlook_ingestion(
        db: Session,
        application_id: str,
        client_secret: str,
    ) -> str:

    # Outlook flow
    # connect
    settings = create_outlook_settings(
        application_id = application_id,
        client_secret = client_secret
    )
    access_token = connect_outlook(settings)
   
    # fetch messages
    headers = graph_headers(access_token)
    folder_name = 'Inbox'
    target_folder = search_folder(headers, folder_name)
    if target_folder is None:
        raise RuntimeError("Outlook Inbox folder was not found.")
    
    folder_id = target_folder['id']

    try:
        messages = fetch_outlook_messages(
            access_token, 
            folder_id=folder_id, 
            top=50, 
            max_results=200
            )
    except Exception as e:
        return f"Error Retrieving Messages Due to {e}"


    if messages:
        for message in messages:
            # parse messages
            parsed_email = build_parsed_email_from_graph_message(message, EmailProvider.OUTLOOK)
            if not parsed_email:
                continue

            process_email(
                db=db, 
                email=parsed_email,
                outlook_headers=headers,
                outlook_message_id=message["id"],
                )
                    
    


def process_email(
    db: Session,
    email: ParsedEmail,
    *,
    outlook_headers: dict[str, str] | None = None,
    outlook_message_id: str | None = None,
    imap_connection = None,
    imap_uid: bytes | None = None,
    ) -> None:

    job_board = identify_job_board(email.sender)
    # I think this should be this code below
    # job_board = is_job_board_email(email)

    if job_board is None:
        return
    
    normalizer = JOB_BOARD_PARSERS.get(job_board)
    
    if normalizer is None:
        return []
    
    jobs = normalizer.normalize(email)
    if not jobs:
        return
    
    created_jobs = persist_normalized_jobs(db, jobs)

    if not created_jobs:
        return

    delete_email(
        provider=email.provider,
        outlook_headers=outlook_headers,
        outlook_message_id=outlook_message_id,
        imap_connection=imap_connection,
        imap_uid=imap_uid
    )



def run_mail_ingestion(
    db: Session,
    outlook_application_id: str,
    outlook_client_secret: str,
    icloud_username: str,
    icloud_password: str,
    ) -> None:
    logger.debug("Mail ingestion started")
    try:
        logger.debug("Outlook ingestion started")
        run_outlook_ingestion(
            db=db,
            application_id=outlook_application_id,
            client_secret=outlook_client_secret,
        )
        logger.debug("Outlook ingestion Completed")
    except Exception:
        logger.exception("Outlook Mail Ingestion Failed")
    try:
        logger.debug("ICloud ingestion started")
        run_imap_ingestion(
            db=db,
            username=icloud_username,
            password=icloud_password,
        )
        logger.debug("ICloud ingestion Completed")
    except Exception:
        logger.exception("ICloud Mail Ingestion Failed")
    logger.debug("Mail ingestion Completed")