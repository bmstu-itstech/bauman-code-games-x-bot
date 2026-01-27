from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_uri: str
    telegram_token: str
    log_level: str = "debug"
    pd_policy_url: str = ""


settings = Settings()  # type: ignore[call-arg]
