import re
import time
from datetime import datetime, timezone
from typing import List

from feedparser import FeedParserDict
from khl import PublicMessage

from bot.databases.rss_schema import RSSKookChannel, RSSSubscription
from bot.databases.sql import get_session
from bot.utils.rss_utils import RssUtils


def rss_delete_all():
    session = get_session()
    session.query(RSSKookChannel).delete()
    session.query(RSSSubscription).delete()
    session.commit()


async def rss_subscribe(raw_url, msg: PublicMessage):
    url_pattern = r'\((http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)\)'
    match = re.search(url_pattern, raw_url)
    if match is None:
        return
    url = match.group(1)

    session = get_session()

    channel = session.query(RSSKookChannel).filter_by(channel_id=msg.channel.id, guild_id=msg.guild.id).first()
    already_subbed = False
    commit = False
    if channel is None:
        channel = RSSKookChannel(msg.channel.id, msg.guild.id)
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
            rss_sub = RSSSubscription(url)
            rss_sub.kook_channels.append(channel)
            # add
            session.add(rss_sub)
        else:
            # associate
            channel.rss_subs.append(rss_sub)

        commit = commit or True

    if commit:
        # if 1 missing
        await msg.reply('subbed')
        session.commit()
    else:
        # both exist and associated
        await msg.reply('already subbed')
        session.close()


async def get_subs_to_notify() -> dict[FeedParserDict:List[str]]:
    # url exists
    session = get_session()
    # use this time to update
    current_date = datetime.now(timezone.utc)
    subs_to_notify = {}
    # all rss subscriptions
    rss_subs = session.query(RSSSubscription).all()
    for sub in rss_subs:
        channel_id_list = []
        feed = await RssUtils.parse_feed_with_retry(sub.url)
        if feed is None:
            print("Failed to parse feed")
            continue

        if len(feed.entries) == 0:
            continue
        # check if newer than last_update
        first_entry_date = datetime.utcfromtimestamp(time.mktime(feed.entries[0].published_parsed))
        # is new
        if sub.update_date < first_entry_date:
            for channel in sub.kook_channels:
                channel_id_list.append(channel.channel_id)
            subs_to_notify[feed] = channel_id_list
            sub.update_date = current_date
            # update date, and notify kook channels
        else:
            # check next rss
            continue

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


async def rss_list(msg: PublicMessage):
    session = get_session()
    channel = session.query(RSSKookChannel).filter_by(channel_id=msg.channel.id, guild_id=msg.guild.id).first()
    if channel is None:
        await msg.reply('NOTHING')
    else:
        str_list = []
        for sub in channel.rss_subs:
            str_list.append(sub.url)
        await msg.reply('subs => ' + '; '.join(link for link in str_list))
