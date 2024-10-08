from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel


BASE_DIR = Path(__file__).parent

private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"


class PostgresDatabaseSettings(BaseModel):
    host: str
    port: str
    name: str
    user: str
    password: str
    url: str

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

class PostgresTestDatabaseSettings(BaseModel):
    host: str
    port: str
    name: str
    user: str
    password: str
    url: str


class AuthJWT(BaseModel):
    private_key: str = private_key_path.read_text()
    public_key: str = public_key_path.read_text()
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 60 * 24 * 30
    # refresh_token_expire_minutes: int = 60 * 24 * 30
    refresh_token_expire_days: int = 60 * 24 * 30


class SMTPSettings(BaseModel):
    user: str
    password: str
    host: str
    port: str


class AWSSettings(BaseModel):
    bucket_name: str


class RedisSettings(BaseModel):
    host: str
    port: str
    first_db: str
    second_db: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_nested_delimiter="__"
    )
    auth_jwt: AuthJWT = AuthJWT()
    db: PostgresDatabaseSettings
    aws: AWSSettings
    smtp: SMTPSettings
    redis: RedisSettings
    db_test: PostgresTestDatabaseSettings


settings: Settings = Settings()