import logging
import os
from logging import Logger
from logging.handlers import TimedRotatingFileHandler

from khl import Bot, Event, Message

from bot.configs.bot_config import settings

logger = logging.getLogger(__name__)


class BotUtils(object):
    @staticmethod
    async def has_admin_and_manage(bot: Bot, user_id, guild_id) -> bool:
        try:
            if user_id in settings.admin_users:
                return True

            guild = await bot.client.fetch_guild(guild_id)
            user_roles = (await guild.fetch_user(user_id)).roles
            guild_roles = await (await bot.client.fetch_guild(guild_id)).fetch_roles()
            # 遍历服务器身分组
            for role in guild_roles:
                # 查看当前遍历到的身分组是否在用户身分组内且是否有管理员权限
                if role.id in user_roles and role.has_permission(0) or role.has_permission(5):
                    return True
            # 由于腐竹可能没给自己上身分组，但是依旧拥有管理员权限
            if user_id == guild.master_id:
                return True
            return False
        except Exception as e:
            logger.exception(f"Failed to get permissions for U:{user_id},G:{guild_id}). {e}", exc_info=False)
            return False


class BotLogger(object):
    def __init__(self, logger: Logger):
        self.logger = logger

    def log_msg(self, msg: Message):
        """
        记录消息日志
        :param msg:
        :return:
        """
        self.logger.info(f"Message: G_id({msg.ctx.guild.id})-C_id({msg.ctx.channel.id}) - "
                         f"Au({msg.author_id})-({msg.author.username}#{msg.author.identify_num}) = {msg.content}")

    def log_event(self, event: Event):
        """
        记录事件日志
        :param event:
        :return:
        """
        self.logger.info(f"Event: G_id({event.body['guild_id']})-C_id({event.body['target_id']}) - "
                         f"Au({event.body['user_id']})-"
                         f"({event.body['user_info']['username']}#{event.body['user_info']['identify_num']})"
                         f" = Type({event.event_type})-Body_val({event.body['value']})")

    def create_log_file(self, filename: str):
        """
        将日志记录到日志文件
        :param filename: ./logs/filename
        :return:
        """
        filename = './logs/' + filename

        try:
            # 尝试创建 FileHandler
            fh = logging.FileHandler(filename=filename, encoding='utf-8', mode='a')

        except OSError:
            os.makedirs(os.path.dirname(filename))
            # 再次尝试创建 FileHandler
            fh = logging.FileHandler(filename=filename, encoding='utf-8', mode='a')

        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -%(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        return self.logger

    def create_log_file_by_rotate_handler(self, filename: str):
        filename = './logs/' + filename
        try:
            # 尝试创建 RotatingFileHandler
            fh = TimedRotatingFileHandler(filename, when='D', interval=1, backupCount=7)
            # 设置日志文件的命名规则，按天切分日志文件
            # 'when'参数可以是 'S'、'M'、'H'、'D'、'W0'-'W6'，分别表示秒、分钟、小时、天、周一到周日切分
            # 'interval'参数表示切分的时间间隔
            # 'backupCount'参数表示保留的日志文件的最大数量

        except OSError:
            os.makedirs(os.path.dirname(filename))
            # 再次尝试创建 RotatingFileHandler
            fh = TimedRotatingFileHandler(filename, when='D', interval=1, backupCount=7)

        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -%(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
