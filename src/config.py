from pydantic_settings import BaseSettings
from fastapi_mail import ConnectionConfig

class Settings(BaseSettings):
    # ... ваши текущие настройки
    SECRET_KEY: str = "your-secret-key"
    RESET_TOKEN_EXPIRE_HOURS: int = 1
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_HOST: str
    SMTP_PORT: int

    @property
    def email_conf(self):
        return ConnectionConfig(
            MAIL_USERNAME=self.SMTP_USER,
            MAIL_PASSWORD=self.SMTP_PASSWORD,
            MAIL_FROM=self.SMTP_USER,
            MAIL_PORT=self.SMTP_PORT,
            MAIL_SERVER=self.SMTP_HOST,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
        )