from khl import Bot

from bot.tasks import task_basic

"""
Add tasks that need to be registered here
"""


def register_tasks(bot: Bot):
    task_basic.reg_basic_task(bot)
    task_basic.reg_rss_task(bot)
