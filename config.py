import os
from pathlib import Path
from pydantic import Field
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Secrets(BaseSettings):
    """Configuration class for API keys and settings using Pydantic BaseSettings."""

    # Google Cloud settings
    GOOGLE_CLOUD_PROJECT: str | None = Field(default=None, env="GOOGLE_CLOUD_PROJECT")
    GOOGLE_CLOUD_LOCATION: str = Field(default="global", env="GOOGLE_CLOUD_LOCATION")
    GOOGLE_CLOUD_SA_PATH: str | None = Field(default=None, env="GOOGLE_CLOUD_SA_PATH")
