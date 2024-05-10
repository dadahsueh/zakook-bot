import logging

from khl import Bot, Message, MessageTypes, PublicMessage

from bot.databases.git_queries import get_all_git_list, get_git_list, git_subscribe, git_unsubscribe
from bot.messages.card_messages_basic import exception_card_msg, help_card_msg
from bot.utils.bot_utils import BotLogger
from bot.utils.bot_utils import BotUtils

logger = logging.getLogger(__name__)
cmd_logger = BotLogger(logger)


def reg_git_cmd(bot: Bot):
    @bot.command(name='git', case_sensitive=False)
    async def cmd_git(msg: Message, *args):
        # not public message
        if not isinstance(msg, PublicMessage):
            return

        # no permission
        perm = await BotUtils.has_admin_and_manage(bot, msg.author_id, msg.guild.id)
        if not perm:
            return

        # switch case
        switch = {
            "sub": sub,
            "unsub": un_sub,
            "unsuball": un_sub_all,
            "list": list_subs,
            "dump": list_all_subs,
        }
        try:
            if args and len(args) > 0:
                option = args[0]
                result = switch.get(option, git_help)
                await result(msg, *args[1:])
            else:
                await git_help(msg, *args)

            cmd_logger.log_msg(msg)
        except Exception as e:
            await msg.reply(content=exception_card_msg(e), type=MessageTypes.CARD)
            logger.exception(f"Failed {msg.content} for U:{msg.author_id}. {e}")

    async def git_help(msg: PublicMessage, *args):
        await msg.reply(content=help_card_msg('git'), type=MessageTypes.CARD)

    async def sub(msg: PublicMessage, *args):
        if len(args) < 2:
            await git_help(msg, *args)
            return
        repo_url = args[0]
        update_interval = 7

        try:
            update_interval = int(args[1])
        except Exception as e:
            logger.exception(f"Invalid input: '{args[1]}'. {e}")

        sub_result = await git_subscribe(msg.channel.id, msg.guild.id, repo_url, update_interval, *args[2:])
        if not sub_result.success:
            return

        try:
            await msg.add_reaction('🆗')
            await msg.reply(sub_result.summary)
        except Exception as e:
            # issue, sometimes the image link leads to 403 or broken, solution remove image
            logger.warning(f"Failed reply, retry compatibility mode. {e}")

    async def un_sub(msg: PublicMessage, *args):
        if len(args) == 0:
            await git_help(msg, args)
            return
        wildcard = {
            '*',
            'all'
        }
        if args[0] in wildcard:
            await un_sub_all(msg)
        else:
            result = await git_unsubscribe(msg.channel.id, *args)
            if result:
                await msg.add_reaction('⭕')

    async def un_sub_all(msg: PublicMessage, *args):
        git_url_list = await get_git_list(msg.channel.id)
        await un_sub(msg, *git_url_list)

    async def list_subs(msg: PublicMessage, *args):
        git_url_list = await get_git_list(msg.channel.id)
        encapsule_and_joined = '\n'.join([f'`{string}`' for string in git_url_list])
        await msg.reply(f"🔖 Git已订阅列表:\n{encapsule_and_joined}")

    async def list_all_subs(msg: PublicMessage, *args):
        git_url_list = await get_all_git_list()
        encapsule_and_joined = '\n'.join([f'`{string}`' for string in git_url_list])
        await msg.reply(f"🔖 Git全部订阅列表:\n{encapsule_and_joined}")
