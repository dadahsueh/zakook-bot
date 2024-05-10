import logging

from khl import Bot

from bot.configs.bot_config import settings

logger = logging.getLogger(__name__)


# if there are too many tasks, combine tasks with similar intervals
def reg_general_task(bot: Bot):
    @bot.task.add_date()
    async def boot_task():
        logger.info(f"I'm alive!")

    @bot.task.add_interval(minutes=10)
    async def update_bot_status():
        if settings.lock:
            return
        else:
            settings.lock = True

        try:
            if len(settings.music_status) == 0:
                return
            music_parts = settings.music_status[settings.music_status_idx].split(';')
            settings.music_status_idx = (settings.music_status_idx + 1) % len(settings.music_status)
            if music_parts[0] == '':
                await bot.client.stop_listening_music()
            else:
                await bot.client.update_listening_music(music_parts[0], music_parts[1], 'cloudmusic')
            settings.lock = False
        except Exception as e:
            settings.lock = False
            logger.error(f"Failed update_bot_status: {e}")
