
from app.mail.models import EmailProvider
from app.mail.providers.icloud import delete_imap_message
from app.mail.providers.outlook import delete_outlook_message


def delete_email(
    provider: EmailProvider,
    *,
    outlook_headers: dict | None = None,
    outlook_message_id: str | None = None,
    imap_connection=None,
    imap_uid: bytes | None = None,
) -> None:

    if provider == EmailProvider.OUTLOOK:
        delete_outlook_message(
            headers=outlook_headers,
            message_id=outlook_message_id,
        )

    if provider == EmailProvider.ICLOUD:
        delete_imap_message(
            connection=imap_connection,
            uid=imap_uid,
        )

    if provider == EmailProvider.APPLE:
            delete_imap_message(
                connection=imap_connection,
                uid=imap_uid,
            )