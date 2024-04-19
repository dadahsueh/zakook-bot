import logging

from khl import Bot, MessageTypes

from bot.configs.bot_config import settings
from bot.databases.rss_queries import get_subs_to_notify
from bot.messages.card_messages_basic import rss_card_msg_from_entry
from bot.utils.log_utils import BotLogger

bot_settings = settings
logger = logging.getLogger(__name__)
task_logger = BotLogger(logger)
task_logger.create_log_file_by_rotate_handler('bot_tasks.log')


# if there are too many tasks, combine tasks with similar intervals
def reg_basic_task(bot: Bot):
    @bot.task.add_interval(minutes=1)
    async def update_bot_status():
        if settings.lock:
            return None
        else:
            settings.lock = True

        try:
            music_parts = settings.music_status[settings.music_status_idx].split(';')
            settings.music_status_idx = (settings.music_status_idx + 1) % len(settings.music_status)
            if music_parts[0] == '':
                await bot.client.stop_listening_music()
            else:
                await bot.client.update_listening_music(music_parts[0], music_parts[1], 'cloudmusic')
            settings.lock = False
        except Exception as e:
            settings.lock = False
            logger.exception(e)


# TODO periodic cleaning
def reg_rss_task(bot: Bot):
    @bot.task.add_interval(minutes=30)
    async def check_and_notify_channels(max_entries=3):
        try:
            channel_cache = {}
            subs_to_notify = await get_subs_to_notify()
            for feed, channels in subs_to_notify.items():
                logger.info(f"Notifying {channels}.")
                # parse feed, shorten if too many (some rss feeds are crazy)
                rss_card_list = []
                short_feed = feed.entries[:max_entries]
                for entry in short_feed:
                    rss_card_list.append(rss_card_msg_from_entry(entry))

                # notify channels
                for channel_id in channels:
                    if channel_id in channel_cache:
                        target_channel = channel_cache[channel_id]
                    else:
                        target_channel = await bot.client.fetch_public_channel(channel_id=channel_id)
                        channel_cache[channel_id] = target_channel

                    for card_msg in rss_card_list:
                        await bot.client.send(target=target_channel, type=MessageTypes.CARD, content=card_msg)

        except Exception as e:
            logger.exception(e)
