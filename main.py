import logging

from khl import Bot

from bot.commands import reg_cmds
from bot.configs.bot_config import settings
from bot.tasks import reg_tasks

logger = logging.getLogger(settings.BOT_NAME)

# 日志信息
logging.basicConfig(level=logging.INFO, format='%(asctime)s -%(name)-24s:%(levelname)-8s-%(message)s')
logger.info(f'{settings.BOT_NAME} version {settings.BOT_VERSION}')

bot = Bot(token=settings.token)

reg_cmds.register_cmds(bot)
reg_tasks.register_tasks(bot)

if __name__ == '__main__':
    bot.run()
