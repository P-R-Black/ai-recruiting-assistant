import logging

from app.core.config import settings
from app.core.database import SessionLocal
from app.orchestrator.orchestrator import run_mail_ingestion

logger = logging.getLogger(__name__)


def main():
    db = SessionLocal()

    try:
        run_mail_ingestion(
            db=db,
            outlook_application_id=settings.application_id,
            outlook_client_secret=settings.client_secret,
            icloud_username=settings.icloud_username,
            icloud_password=settings.icloud_password
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()


# /Users/paulblack/VS Code/ai-recruiting-assistant/backend/app/scripts/run_mail_ingestion.py