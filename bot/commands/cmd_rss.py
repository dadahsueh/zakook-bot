import logging

from khl import Bot, Message, MessageTypes, PublicMessage

from bot.configs.bot_config import settings
from bot.databases.rss_queries import get_feed, get_rss_list, rss_subscribe
from bot.messages.card_messages_basic import exception_card_msg, rss_card_msg_from_entry
from bot.utils.bot_utils import BotUtils
from bot.utils.log_utils import BotLogger
from bot.utils.rss_utils import RssUtils

bot_settings = settings
logger = logging.getLogger(__name__)
cmd_logger = BotLogger(logger)


def reg_rss_cmd(bot: Bot):
    # TODO maybe combine rss commands to /rss sub /rss list /rss unsub /rss unsuball etc
    @bot.command(name='rsssub', case_sensitive=False)
    async def cmd_rss_sub(msg: Message, url: str = None):
        try:
            if not isinstance(msg, PublicMessage):
                return
            if not url:
                # hint help
                logger.info(f"No url entered")
                return

            # TODO maybe check if valid rss

            perm = await BotUtils.has_admin_and_manage(bot, msg.author_id, msg.guild.id)
            if not perm:
                return

            feed = await get_feed(url)
            if feed is None or len(feed.entries) == 0:
                return

            feed_title = RssUtils.parse_feed_title(feed)
            success = await rss_subscribe(feed_title, url, msg.channel.id, msg.guild.id)
            if not success:
                return

            entry = feed.entries[0]
            await msg.reply(content=rss_card_msg_from_entry(feed_title, entry), type=MessageTypes.CARD)
            cmd_logger.logging_msg(msg)
        except Exception as e:
            await msg.reply(content=exception_card_msg(e), type=MessageTypes.CARD)
            logger.exception(f"Failed {msg.content} for U:{msg.author_id}. {e}", exc_info=False)

    # TODO
    @bot.command(name='rssunsub', case_sensitive=False)
    async def cmd_rss_unsub_all(msg: Message, url: str = None):
        try:
            if not isinstance(msg, PublicMessage):
                return
            if not url:
                # hint help
                logger.info(f"No url entered")
                return

            perm = await BotUtils.has_admin_and_manage(bot, msg.author_id, msg.guild.id)
            if not perm:
                return

            rss_url_list = await get_rss_list(msg.channel.id)
            encapsule_and_joined = '\n'.join([f'`{string}`' for string in rss_url_list])
            await msg.reply(f"The current channel is subscribed to:\n{encapsule_and_joined}")
            cmd_logger.logging_msg(msg)
        except Exception as e:
            await msg.reply(content=exception_card_msg(e), type=MessageTypes.CARD)
            logger.exception(f"Failed {msg.content} for U:{msg.author_id}. {e}", exc_info=False)

    # TODO
    @bot.command(name='rssunsuball', case_sensitive=False)
    async def cmd_rss_unsub_all(msg: Message):
        try:
            if not isinstance(msg, PublicMessage):
                return

            perm = await BotUtils.has_admin_and_manage(bot, msg.author_id, msg.guild.id)
            if not perm:
                return
            rss_url_list = await get_rss_list(msg.channel.id)
            encapsule_and_joined = '\n'.join([f'`{string}`' for string in rss_url_list])
            await msg.reply(f"The current channel is subscribed to:\n{encapsule_and_joined}")
            cmd_logger.logging_msg(msg)
        except Exception as e:
            await msg.reply(content=exception_card_msg(e), type=MessageTypes.CARD)
            logger.exception(f"Failed {msg.content} for U:{msg.author_id}. {e}", exc_info=False)

    @bot.command(name='rsslist', case_sensitive=False)
    async def cmd_rss_list(msg: Message):
        try:
            if not isinstance(msg, PublicMessage):
                return

            perm = await BotUtils.has_admin_and_manage(bot, msg.author_id, msg.guild.id)
            if not perm:
                return
            rss_url_list = await get_rss_list(msg.channel.id)
            encapsule_and_joined = '\n'.join([f'`{string}`' for string in rss_url_list])
            # TODO card
            await msg.reply(f"The current channel is subscribed to:\n{encapsule_and_joined}")
            cmd_logger.logging_msg(msg)
        except Exception as e:
            await msg.reply(content=exception_card_msg(e), type=MessageTypes.CARD)
            logger.exception(f"Failed {msg.content} for U:{msg.author_id}. {e}", exc_info=False)
