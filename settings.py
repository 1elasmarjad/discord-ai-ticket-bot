from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    discord_bot_token: str = Field(validation_alias="DISCORD_BOT_TOKEN")


settings = Settings()
