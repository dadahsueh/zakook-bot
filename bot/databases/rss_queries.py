import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List

from feedparser import FeedParserDict

from bot.databases.rss_db import get_session
from bot.databases.rss_schemas import RSSKookChannel, RSSSubscription
from bot.utils.rss_utils import RssUtils

logger = logging.getLogger(__name__)

"""
This module contains all RSS queries
"""


# for testing
def rss_delete_all():
    with get_session() as session:
        session.query(RSSKookChannel).delete()
        session.query(RSSSubscription).delete()
        session.commit()


async def get_subs_to_notify() -> dict[FeedParserDict:List[str]]:
    """
    Could have SQLite concurrency issues, very slow
    """
    current_date = datetime.now(timezone.utc)
    subs_to_notify = {}

    with get_session() as session:
        # all rss subscriptions
        rss_subs = session.query(RSSSubscription).all()
        for sub in rss_subs:
            try:
                # parse subscription and append
                channel_id_list = []
                feed = await RssUtils.parse_feed_with_retry(sub.url)

                # Check if the feed was parsed successfully
                if feed.bozo:
                    logger.error(f"Feed is bozo {sub.url}. {feed}")

                if feed is None or len(feed.entries) == 0:
                    raise ValueError(f"feed is None or len(feed.entries) == 0")

                # get latest entry date, if no date try get feed update date or feed.feed update date
                latest_date_parsed = feed.entries[0].get('published_parsed',
                                                         feed.get('updated_parsed',
                                                                  feed.feed.get('updated_parsed', None)))
                if latest_date_parsed is None:
                    raise ValueError(f"latest_date_parsed is None for {sub.url}")

                # latest_date_parsed is utc
                latest_entry_date = datetime.fromtimestamp(time.mktime(latest_date_parsed))

                # update_date and first_entry_date are both utc
                # is new
                if sub.update_date < latest_entry_date:
                    # iterate and filter feed entries
                    for i in range(len(feed.entries)):
                        entry_parsed_date = feed.entries[i].get('published_parsed', feed.get('updated_parsed',
                                                                                             feed.feed.get(
                                                                                                 'updated_parsed',
                                                                                                 None)))
                        entry_utc_date = datetime.fromtimestamp(time.mktime(entry_parsed_date))
                        # if entry is older than update date
                        if sub.update_date > entry_utc_date:
                            # slice at first old entry, exclusive
                            feed.entries = feed.entries[:i]

                    for channel in sub.kook_channels:
                        channel_id_list.append(channel.channel_id)
                    subs_to_notify[feed] = channel_id_list
                    sub.update_date = current_date
            except Exception as e:
                logger.exception(f"Failed to parse subscription {sub.url}. {e}")

        if len(subs_to_notify) > 0:
            session.commit()

    return subs_to_notify


async def get_all_rss_list() -> List[str]:
    str_list = []
    with get_session() as session:
        rss_subs = session.query(RSSSubscription).all()
        if rss_subs:
            for sub in rss_subs:
                str_list.append(sub.url)
    return str_list


async def get_rss_list(channel_id) -> List[str]:
    str_list = []
    with get_session() as session:
        channel = session.query(RSSKookChannel).filter_by(channel_id=channel_id).first()
        if channel:
            for sub in channel.rss_subs:
                str_list.append(sub.url)
    return str_list


async def get_feed(raw_url):
    try:
        url = RssUtils.extract_url(raw_url)

        feed = await RssUtils.parse_feed_with_retry(url)
        return feed
    except Exception as e:
        logger.exception(f"Failed get_feed. {e}")
        raise


@dataclass
class RSSSubscribeResult:
    success: bool
    feed: str


async def rss_subscribe(channel_id, guild_id, *args) -> RSSSubscribeResult:
    """
    :param channel_id:
    :param guild_id:
    :param args:
    :return: True if subscribed by this call, False if already subbed
    """
    commited = False
    feed = None
    with get_session() as session:
        subscribe_list = []
        channel = session.query(RSSKookChannel).filter_by(channel_id=channel_id).first()
        if channel is None:
            channel = RSSKookChannel(channel_id, guild_id)
            # add, don't commit if none associated
            session.add(channel)

        for arg in args:
            try:
                subscribe_list.append(RssUtils.extract_url(arg))
            except Exception as e:
                logger.error(f"Unable to extract url {arg}. {e}")

            if len(subscribe_list) == 0:
                raise ValueError(f"unable to extract any rss url")

        for url in subscribe_list:
            try:
                rss_sub = session.query(RSSSubscription).filter_by(url=url).first()
                if rss_sub is None:
                    feed = await get_feed(url)
                    # Check if the feed was parsed successfully
                    if feed.bozo:
                        logger.error(f"Feed is bozo {url}. {feed}")

                    if feed is None or len(feed.entries) == 0:
                        raise ValueError(f"feed is None or len(feed.entries) == 0")

                    feed_title = RssUtils.parse_feed_title(feed)
                    rss_sub = RSSSubscription(url, feed_title)
                    # channel.rss_subs.append(rss_sub)
                    rss_sub.kook_channels.append(channel)
                    session.add(rss_sub)
                    commited = True
                elif rss_sub not in channel.rss_subs:
                    # associate
                    channel.rss_subs.append(rss_sub)
                    commited = True
            except Exception as e:
                logger.error(f"Failed sub {url}. {e}")

        if commited:
            session.commit()
    return RSSSubscribeResult(commited, feed)


async def rss_unsubscribe(channel_id, *args) -> bool:
    """
    :param channel_id:
    :param args:
    :return: True if unsubscribed by this call, False otherwise
    """
    with get_session() as session:
        channel = session.query(RSSKookChannel).filter_by(channel_id=channel_id).first()
        if channel is None:
            return False

        dirty = False
        rss_remove_list = []
        unsubscribe_list = []
        for arg in args:
            try:
                unsubscribe_list.append(RssUtils.extract_url(str(arg)))
            except Exception as e:
                logger.error(f"Unable to extract url {arg}. {e}")

        for rss in channel.rss_subs:
            if rss.url in unsubscribe_list:
                rss_remove_list.append(rss)

        for rss in rss_remove_list:
            dirty = True
            channel.rss_subs.remove(rss)
            if len(rss.kook_channels) == 0:
                session.delete(rss)

        if len(channel.rss_subs) == 0:
            dirty = True
            session.delete(channel)

        if dirty:
            session.commit()
            return True

    return False
