from khl import Bot

from bot.tasks import task_general, task_git, task_rss

"""
Add tasks that need to be registered here
"""


def register_tasks(bot: Bot):
    task_general.reg_general_task(bot)
    task_rss.reg_rss_task(bot)
    task_git.reg_git_task(bot)
