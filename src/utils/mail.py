import asyncio
from fastapi_mail import (
    ConnectionConfig,
    FastMail,
    MessageSchema,
    MessageType,
    NameEmail
)

from src.settings import EnvironmentEnum, settings, logger


conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_conf.username,
    MAIL_PASSWORD=settings.mail_conf.password,
    MAIL_FROM=settings.mail_conf.mail_from,
    MAIL_PORT=settings.mail_conf.port,
    MAIL_SERVER=settings.mail_conf.server,
    MAIL_STARTTLS=settings.mail_conf.starttls,
    MAIL_SSL_TLS=settings.mail_conf.ssl_tls,
    USE_CREDENTIALS=settings.mail_conf.use_credentials,
    VALIDATE_CERTS=settings.mail_conf.validate_certs,
)


class EmailInterface:
    @staticmethod
    async def send(subject: str, recipients: list[NameEmail], body: str):
        ...


class SMTPEmail(EmailInterface):
    @staticmethod
    async def send(subject: str, recipients: list[NameEmail], body: str):
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body,
            subtype=MessageType.html)

        fm = FastMail(conf)
        await fm.send_message(message)


class ConsoleEmail(EmailInterface):
    @staticmethod
    async def send(subject: str, recipients: list[NameEmail], body: str):
        mail = """
            ------ console mail

            Subject: {}
            recipients: {}

            {}

            ------
        """.format(subject, recipients, body)

        print(mail)


def get_email_sender() -> type[EmailInterface]:
    if settings.environment == EnvironmentEnum.prod:
        return SMTPEmail

    return ConsoleEmail


email_manager = get_email_sender()

