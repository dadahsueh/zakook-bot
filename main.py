import argparse
import logging
import sys

from khl import Bot

from bot.commands import reg_cmds
from bot.configs.bot_config import settings
from bot.tasks import reg_tasks


def debugger_is_active() -> bool:
    debug = hasattr(sys, 'gettrace') and sys.gettrace() is not None
    return debug


# Parse arguments
parser = argparse.ArgumentParser(
    description="Simple template KOOK bot.",
    epilog="Check the repo for details: https://github.com/dadahsueh/zakook-bot")
parser.add_argument('-t', '--token', type=str, help='Authentication token')
parser.add_argument('-v', '--verbose', action='count', default=0, help='Increase verbosity level (e.g., -v, -vv, -vvv)')
args = parser.parse_args()

# Configure logging
log_level = logging.WARNING

if debugger_is_active or args.verbose >= 2:
    log_level = logging.DEBUG
elif args.verbose == 1:
    log_level = logging.INFO

logger = logging.getLogger(settings.BOT_NAME)

logging.basicConfig(level=log_level, format='%(asctime)s -%(name)-24s:%(levelname)-8s-%(message)s')
logger.info(f'{settings.BOT_NAME} version {settings.BOT_VERSION} {log_level}')

# Check token
if args.token:
    token = args.token  # Use token from command line argument if provided
else:
    token = settings.token  # Use default token from settings module
bot = Bot(token=token)

reg_cmds.register_cmds(bot)
reg_tasks.register_tasks(bot)

if __name__ == '__main__':
    bot.run()
