from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from bot.databases.rss_db import Base

# Bi-Directional Many-to-many
RSSChannelSub = Table(
    'RSSChannelSub', Base.metadata,
    Column('rss_kook_ch_id', Integer, ForeignKey('rss_kook_channel.id')),
    Column('rss_sub_id', Integer, ForeignKey('rss_subscription.id'))
)


class RSSKookChannel(Base):
    __tablename__ = 'rss_kook_channel'

    id = Column(Integer, primary_key=True)
    channel_id = Column(String(256), nullable=False)
    guild_id = Column(String(256), nullable=False)

    rss_subs = relationship('RSSSubscription', secondary=RSSChannelSub, back_populates='kook_channels')

    def __init__(self, channel_id, guild_id):
        self.channel_id = channel_id
        self.guild_id = guild_id


class RSSSubscription(Base):
    __tablename__ = 'rss_subscription'

    id = Column(Integer, primary_key=True)
    url = Column(String(256), nullable=False)
    title = Column(String(256), nullable=False)  # some has feed.feed.image.url
    update_date = Column(DateTime, default=datetime.now(timezone.utc))

    kook_channels = relationship('RSSKookChannel', secondary=RSSChannelSub, back_populates='rss_subs')

    def __init__(self, url, title):
        self.url = url
        self.title = title
