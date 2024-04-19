from khl import Bot

from bot.tasks import task_basic


def register_tasks(bot: Bot):
    task_basic.reg_basic_task(bot)
    task_basic.reg_rss_task(bot)
