from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    discord_bot_token: str = Field(validation_alias="DISCORD_BOT_TOKEN")

    dev_mode: bool = Field(validation_alias="DEV_MODE", default=False)

    openrouter_api_key: str = Field(validation_alias="OPENROUTER_API_KEY")

    @field_validator("dev_mode", mode="before")
    @classmethod
    def parse_bool(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)


settings = Settings()
