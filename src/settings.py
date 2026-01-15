import logging
from enum import Enum

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


logger = logging.getLogger("uvicorn.error")


class EnvironmentEnum(str, Enum):
    local = "local"
    dev = "dev"
    prod = "prod"


class MailConfig(BaseModel):
    username: str = Field(default="username", validation_alias="MAIL_USERNAME")
    password: SecretStr = Field(default=SecretStr("***"), validation_alias="MAIL_PASSWORD")
    mail_from: str = Field(default="test@email.com", validation_alias="MAIL_FROM")
    port: int = Field(default=465, validation_alias="MAIL_PORT")
    server: str = Field(default="mail server", validation_alias="MAIL_SERVER")
    starttls: bool = Field(default=False, validation_alias="MAIL_STARTTLS")
    ssl_tls: bool = Field(default=True, validation_alias="MAIL_SSL_TLS")
    use_credentials: bool = Field(default=True, validation_alias="MAIL_USE_CREDENTIALS")
    validate_certs: bool = Field(default=True, validation_alias="MAIL_VALIDATE_CERTS")


class S3Config(BaseModel):
    region: str = Field(default="us-east-1", validation_alias="S3_REGION")
    prefix: str = Field(default="files", validation_alias="S3_PREFIX")
    bucket: str = Field(default="bucket", validation_alias="S3_BUCKET")


class Settings(BaseSettings):
    environment: EnvironmentEnum = Field(
        default=EnvironmentEnum.local,
        validation_alias="ENV"
    )
    database_url: str = Field(
        default="postgresql+psycopg2://postgres:postgres@postgres:5432/postgres",
        validation_alias="DATABASE_URL",
    )
    redis_url: str = Field(
        default="redis://redis:6379",
        validation_alias="REDIS_URL",
    )

    secret_key: str = Field(
        default="4843fc4c71f819615787dc7a8a028d550aab28cfd97c187737962f660c3060ce",
        validation_alias="SECRET_KEY",
    )
    algorithm: str = Field(default="HS256", validation_alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30,
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )

    mail_conf: MailConfig = MailConfig()

    s3_conf: S3Config = S3Config()

    model_config = SettingsConfigDict(extra="ignore")


settings = Settings()
