import logging

from khl import Bot, Message, MessageTypes, PublicMessage

from bot.configs.bot_config import settings
from bot.databases.rss_queries import get_feed, get_rss_list, rss_subscribe, rss_unsubscribe
from bot.messages.card_messages_basic import exception_card_msg, help_card_msg, rss_card_msg_from_entry
from bot.utils.bot_utils import BotLogger
from bot.utils.bot_utils import BotUtils
from bot.utils.rss_utils import RssUtils

bot_settings = settings
logger = logging.getLogger(__name__)
cmd_logger = BotLogger(logger)


def reg_rss_cmd(bot: Bot):
    @bot.command(name='rss', case_sensitive=False)
    async def cmd_rss(msg: Message, *args):
        # not public message
        if not isinstance(msg, PublicMessage):
            return

        # TODO maybe check if valid rss

        # no permission
        ss = msg.channel.id
        perm = await BotUtils.has_admin_and_manage(bot, msg.author_id, msg.guild.id)
        if not perm:
            return

        # switch case
        switch = {
            "sub": sub,
            "unsub": un_sub,
            "unsuball": un_sub_all,
            "list": list_subs,
        }
        try:
            if args and len(args) > 0:
                option = args[0]
                result = switch.get(option, rss_help)
                await result(msg, *args[1:])
            else:
                await rss_help(msg, *args)

            cmd_logger.log_msg(msg)
        except Exception as e:
            await msg.reply(content=exception_card_msg(e), type=MessageTypes.CARD)
            logger.exception(f"Failed {msg.content} for U:{msg.author_id}. {e}")

    async def rss_help(msg: PublicMessage, *args):
        await msg.reply(content=help_card_msg('rss'), type=MessageTypes.CARD)

    async def sub(msg: PublicMessage, *args):
        if len(args) == 0:
            await rss_help(msg, *args)
            return

        success = await rss_subscribe(msg.channel.id, msg.guild.id, *args)
        if not success:
            return

        url = args[0]
        feed = await get_feed(url)
        # Check if the feed was parsed successfully
        if feed.bozo:
            logger.error(f"Feed is bozo {url}. {feed}")
        if feed is None or len(feed.entries) == 0:
            raise ValueError(f"feed is None or len(feed.entries) == 0")

        feed_title = RssUtils.parse_feed_title(feed)
        entry = feed.entries[0]
        content = rss_card_msg_from_entry(feed_title, entry)
        try:
            await msg.add_reaction('🆗')
            await msg.reply(content=content, type=MessageTypes.CARD)
        except Exception as e:
            # issue, sometimes the image link leads to 403 or broken, solution remove image
            logger.info(f"Failed reply, retry compatibility mode. {e}")
            content = rss_card_msg_from_entry(feed_title, entry, True)
            await msg.reply(content=content, type=MessageTypes.CARD)

    async def un_sub(msg: PublicMessage, *args):
        if len(args) == 0:
            await rss_help(msg, args)
            return
        wildcard = {
            '*',
            'all'
        }
        if args[0] in wildcard:
            await un_sub_all(msg)
        else:
            result = await rss_unsubscribe(msg.channel.id, *args)
            if result:
                await msg.add_reaction('⭕')

    async def un_sub_all(msg: PublicMessage, *args):
        rss_url_list = await get_rss_list(msg.channel.id)
        await un_sub(msg, *rss_url_list)

    async def list_subs(msg: PublicMessage, *args):
        rss_url_list = await get_rss_list(msg.channel.id)
        encapsule_and_joined = '\n'.join([f'`{string}`' for string in rss_url_list])
        await msg.reply(f"🔖 已订阅列表:\n{encapsule_and_joined}")
