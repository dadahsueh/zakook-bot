import logging
from typing import ClassVar, List

from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    token: str = ''
    container_name: str = ''
    admin_users: List[str] = []

    BOT_NAME: str = ''
    BOT_VERSION: str = ''
    LOG_LEVEL: ClassVar = logging.INFO

    music_status: List[str] = []
    music_status_idx: int = 0

    lock: bool = False

    class Config:
        env_file = '.env'
        # allow, ignore, forbid
        extra = 'allow'


settings = BotSettings()
