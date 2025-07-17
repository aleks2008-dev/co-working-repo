from fastapi_mail import ConnectionConfig


class Settings:
    email_conf = ConnectionConfig(
        MAIL_USERNAME="",
        MAIL_PASSWORD="",
        MAIL_SERVER="localhost",
        MAIL_PORT=1025,
        MAIL_STARTTLS=False,
        MAIL_SSL_TLS=False,
        MAIL_FROM="noreply@example.com",
        USE_CREDENTIALS=False,
        VALIDATE_CERTS=False
    )
