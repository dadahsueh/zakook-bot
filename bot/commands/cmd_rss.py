import logging

from khl import Bot, Message, PublicMessage

from bot.configs.bot_config import settings
from bot.databases.rss_queries import get_rss_list, rss_subscribe
from bot.utils.bot_utils import BotUtils
from bot.utils.log_utils import BotLogger

bot_settings = settings
logger = logging.getLogger(__name__)
cmd_logger = BotLogger(logger)


def reg_rss_cmd(bot: Bot):
    # TODO maybe combine rss commands to /rss sub /rss list /rss unsub /rss unsuball etc
    @bot.command(name='rsssub', case_sensitive=False)
    async def cmd_rss_sub(msg: Message, url: str = None):
        if not isinstance(msg, PublicMessage):
            return
        if not url:
            logger.info(f"No url entered")
            return

        # TODO maybe check if valid rss
        current_channel_guild_id = msg.ctx.guild.id
        if msg.author_id in settings.admin_users:
            perm = True
        else:
            perm_util = BotUtils()
            perm = await perm_util.has_admin_and_manage(bot, msg.author_id, current_channel_guild_id)
        if perm:
            try:
                await rss_subscribe(url, msg)
                cmd_logger.logging_msg(msg)
            except Exception as e:
                logger.exception(f"Failed {msg.content} for U:{msg.author_id}. {e}", exc_info=False)

    @bot.command(name='rsslist', case_sensitive=False)
    async def cmd_rss_list(msg: Message):
        if not isinstance(msg, PublicMessage):
            return

        current_channel_guild_id = msg.ctx.guild.id
        if msg.author_id in settings.admin_users:
            perm = True
        else:
            perm_util = BotUtils()
            perm = await perm_util.has_admin_and_manage(bot, msg.author_id, current_channel_guild_id)
        if perm:
            try:
                rss_url_list = await get_rss_list(msg.channel.id)
                encapsule_and_joined = '\n'.join([f'`{string}`' for string in rss_url_list])
                await msg.reply(f"The current channel is subscribed to:\n{encapsule_and_joined}")
                cmd_logger.logging_msg(msg)
            except Exception as e:
                logger.exception(f"Failed {msg.content} for U:{msg.author_id}. {e}", exc_info=False)
