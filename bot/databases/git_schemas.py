from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from bot.databases.git_db import Base

MIN_INTERVAL = 3
MAX_INTERVAL = 30


class GitChannelSub(Base):
    __tablename__ = 'git_channel_sub'

    id = Column(Integer, primary_key=True)

    channel_id = Column(String(256), nullable=False)
    guild_id = Column(String(256), nullable=False)

    repo_url = Column(String(256), nullable=False)
    repo_sub_filter = Column(String(256), nullable=False)  # json dump, {"branch": "main", "author": "john@example.com"}
    update_interval = Column(Integer, primary_key=False)  # in days, 7 for weekly summary
    update_date = Column(DateTime, default=datetime.now(timezone.utc))

    def __init__(self, channel_id, guild_id, repo_url, repo_sub_filter, update_interval, update_date):
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.repo_url = repo_url
        self.repo_sub_filter = repo_sub_filter
        self.update_interval = min(max(update_interval, MIN_INTERVAL), MAX_INTERVAL)
        self.update_date = update_date
