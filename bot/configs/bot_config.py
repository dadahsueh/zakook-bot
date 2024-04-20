import logging
from typing import ClassVar, List

from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    """
    Reads values from .env, also allows extras
    print(settings.model_dump()) to see the all values.
    Will read from ENV values on Docker
    """
    token: str = ''
    container_name: str = 'kookie-runner'
    admin_users: List[str] = []

    BOT_NAME: str = 'KOOKIE'
    BOT_VERSION: str = 'v0.0.1'
    LOG_LEVEL: ClassVar = logging.INFO

    music_status: List[str] = []
    music_status_idx: int = 0

    lock: bool = False

    class Config:
        env_file = '.env'
        # allow, ignore, forbid
        extra = 'allow'


settings = BotSettings()
