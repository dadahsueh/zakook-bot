import configparser
from typing import List

from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    """
    Reads values from .env, also allows extras
    print(settings.model_dump()) to see the all values.
    Will read from ENV values on Docker
    """
    token: str = ''
    container_name: str = 'zakook-runner'
    admin_users: List[str] = []

    BOT_NAME: str = 'ZAKOOK'
    BOT_VERSION: str = 'v0.0.1'

    music_status: List[str] = []
    music_status_idx: int = 0

    lock: bool = False

    # Cloudflare Worker URL
    cf: str = ''
    cf_enabled: bool = False
    # Prioritize using Cloudflare Workers or prioritize vanilla and fallback to Cloudflare Workers
    cf_priority: bool = False

    openai_key: str = ''

    class Config:
        env_file = '.env'
        # allow, ignore, forbid
        extra = 'allow'


settings = BotSettings()

riddlesolver_config = configparser.ConfigParser()
riddlesolver_config.read_dict({
    'openai': {
        'api_key': settings.openai_key,
        'model': 'openchat/openchat-7b:free',  # https://openrouter.ai/models
        'base_url': 'https://openrouter.ai/api/v1'
    },
    'general': {
        'cache_dir': '~/.cache/repo_cache',
        'cache_duration': '7'
    },
    'github': {
        'access_token': '',
    },
})
