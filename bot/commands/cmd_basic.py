import asyncio
import logging
import re

from khl import Bot, Message, MessageTypes, PublicMessage

from bot.configs.bot_config import settings
from bot.messages.card_messages_basic import help_card_msg
from bot.utils.bot_utils import BotUtils
from bot.utils.bot_utils import BotLogger

bot_settings = settings
logger = logging.getLogger(__name__)
cmd_logger = BotLogger(logger)


def reg_basic_cmd(bot: Bot):
    @bot.command(name='help', case_sensitive=False)
    async def cmd_help(msg: Message):
        if not isinstance(msg, PublicMessage):
            return
        try:
            cmd_logger.log_msg(msg)
            await msg.reply(content=help_card_msg(), type=MessageTypes.CARD)
        except Exception as e:
            logger.exception(f"Failed {msg.content} for U:{msg.author_id}. {e}", exc_info=False)

    @bot.command(name='jini', case_sensitive=False)
    async def cmd_hello(msg: Message):
        if not isinstance(msg, PublicMessage):
            return
        try:
            cmd_logger.log_msg(msg)
            await msg.add_reaction('🐔')
            await msg.add_reaction('🍐')
            await msg.add_reaction('🌞')
            await msg.add_reaction('🍓')
            await msg.reply("实在太美～")
        except Exception as e:
            logger.exception(f"Failed {msg.content} for U:{msg.author_id}. {e}", exc_info=False)

    @bot.command(name='clear', case_sensitive=False)
    async def cmd_clear(msg: Message):
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
                cmd_logger.log_msg(msg)
                await bot.client.add_reaction(msg, '👌')
                await asyncio.sleep(2)
                msgs_dict = await msg.channel.list_messages()
                msgs = msgs_dict.items()
                for payload in msgs:
                    regex = r"'id': '([\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12})'"
                    found = re.findall(regex, str(payload[1]))
                    for ids in found:
                        # cmd_logger.logging_msg(ids)
                        msg._msg_id = ids
                        await msg.delete()
            except Exception as e:
                logger.exception(f"Failed {msg.content} for U:{msg.author_id}. {e}", exc_info=False)
