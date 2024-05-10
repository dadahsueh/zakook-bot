from khl import Bot

from bot.commands import cmd_general, cmd_rss, cmd_git

"""
Add commands that need to be registered here
"""


def register_cmds(bot: Bot):
    cmd_general.reg_general_cmd(bot)
    cmd_rss.reg_rss_cmd(bot)
    cmd_git.reg_git_cmd(bot)
