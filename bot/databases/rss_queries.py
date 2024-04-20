import logging
import time
from datetime import datetime, timezone
from typing import List

from feedparser import FeedParserDict

from bot.databases.rss_schema import RSSKookChannel, RSSSubscription
from bot.databases.sql import get_session
from bot.utils.log_utils import BotLogger
from bot.utils.rss_utils import RssUtils

logger = logging.getLogger(__name__)
cmd_logger = BotLogger(logger)

"""
This module contains all RSS queries
"""


# for testing
def rss_delete_all():
    session = get_session()
    session.query(RSSKookChannel).delete()
    session.query(RSSSubscription).delete()
    session.commit()


async def rss_subscribe(feed_title, raw_url, channel_id, guild_id) -> bool:
    try:
        url = RssUtils.extract_url(raw_url)

        session = get_session()

        channel = session.query(RSSKookChannel).filter_by(channel_id=channel_id).first()
        already_subbed = False
        commit = False
        if channel is None:
            channel = RSSKookChannel(channel_id, guild_id)
            # add
            session.add(channel)
            commit = commit or True
        else:
            for sub in channel.rss_subs:
                if url == sub.url:
                    already_subbed = True
                    break

        if not already_subbed:
            rss_sub = session.query(RSSSubscription).filter_by(url=url).first()
            if rss_sub is None:
                rss_sub = RSSSubscription(url, feed_title)
                rss_sub.kook_channels.append(channel)
                # add
                session.add(rss_sub)
            else:
                # associate
                channel.rss_subs.append(rss_sub)

            commit = commit or True

        if commit:
            session.commit()
            return True
        else:
            # both exist and associated
            session.close()
            return False

    except Exception as e:
        logger.exception(f"Failed subscribe {raw_url}. {e}")
        return False


async def get_subs_to_notify() -> dict[FeedParserDict:List[str]]:
    session = get_session()
    current_date = datetime.now(timezone.utc)
    subs_to_notify = {}
    # all rss subscriptions
    rss_subs = session.query(RSSSubscription).all()
    for sub in rss_subs:
        try:
            # parse subscription and append
            channel_id_list = []
            feed = await RssUtils.parse_feed_with_retry(sub.url)

            latest_date_parsed = feed.entries[0].get('published_parsed',
                                                     feed.get('updated_parsed', feed.feed.get('updated_parsed', '')))
            if latest_date_parsed is None:
                raise ValueError(f"latest_date_parsed is None for {sub.url}")

            # check if newer than last_update
            first_entry_date = datetime.utcfromtimestamp(time.mktime(latest_date_parsed))
            # is new
            if sub.update_date < first_entry_date:
                for channel in sub.kook_channels:
                    channel_id_list.append(channel.channel_id)
                subs_to_notify[feed] = channel_id_list
                sub.update_date = current_date
        except Exception as e:
            logger.exception(f"Failed to parse subscription {sub.url}. {e}")

    if len(subs_to_notify) > 0:
        session.commit()
    else:
        session.close()

    return subs_to_notify


async def get_rss_list(channel_id) -> List[str]:
    session = get_session()
    channel = session.query(RSSKookChannel).filter_by(channel_id=channel_id).first()
    str_list = []
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
