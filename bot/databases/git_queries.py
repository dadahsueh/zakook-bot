import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from riddlesolver.repository import fetch_commits
from riddlesolver.summary import generate_summary

from bot.configs.bot_config import riddlesolver_config, settings
from bot.databases.git_db import get_session
from bot.databases.git_schemas import GitChannelSub
from bot.utils.bot_utils import BotLogger
from bot.utils.rss_utils import RssUtils

logger = logging.getLogger(__name__)
cmd_logger = BotLogger(logger)


# for testing
def git_delete_all():
    with get_session() as session:
        session.query(GitChannelSub).delete()
        session.commit()


@dataclass
class NotifyResult:
    channel_id: str
    git_summary: str


async def get_subs_to_notify() -> List[NotifyResult]:
    notify_results = []
    current_date = datetime.now()
    dirty = False

    with get_session() as session:
        # all git subscriptions
        git_subs = session.query(GitChannelSub).all()
        for sub in git_subs:
            try:
                last_should_update_date = current_date - timedelta(days=sub.update_interval)
                if sub.update_date < last_should_update_date:
                    # update
                    filter_dict = json.loads(sub.repo_sub_filter)
                    branch = filter_dict.get('branch', None)
                    author = filter_dict.get('author', None)
                    repo_type = 'remote'

                    batched_commits = fetch_commits(sub.repo_url, sub.update_date, current_date, repo_type=repo_type,
                                                    branch=branch, author=author, config=riddlesolver_config)
                    summary = generate_summary(batched_commits, riddlesolver_config)
                    notify_results.append(NotifyResult(sub.channel_id, summary))

                    sub.update_date = current_date
                    dirty = True
            except Exception as e:
                logger.exception(f"Failed to parse subscription {sub.url}. {e}")

        if dirty:
            session.commit()

    return notify_results


async def get_all_git_list() -> List[str]:
    str_list = []
    with get_session() as session:
        subscriptions = session.query(GitChannelSub).all()
        if subscriptions:
            for sub in subscriptions:
                str_list.append(sub.repo_url)
    return str_list


async def get_git_list(channel_id) -> List[str]:
    str_list = []
    with get_session() as session:
        subscriptions = session.query(GitChannelSub).filter_by(channel_id=channel_id).all()
        if subscriptions:
            for sub in subscriptions:
                str_list.append(sub.repo_url)
    return str_list


@dataclass
class SubscribeResult:
    success: bool
    summary: str


async def git_subscribe(channel_id, guild_id, repo_url, update_interval, *args) -> SubscribeResult:
    git_delete_all()
    if len(settings.openai_key) == 0:
        return SubscribeResult(False, '')
    parsed_url = RssUtils.extract_url(repo_url)
    repo_filter = {}
    if len(args) > 0:
        repo_filter['branch'] = args[0]
    if len(args) > 1:
        repo_filter['author'] = args[1]

    filter_string = json.dumps(repo_filter)

    # add
    with get_session() as session:
        query_result = session.query(GitChannelSub).filter_by(channel_id=channel_id, repo_url=parsed_url).first()
        # already subbed
        if query_result is not None:
            return SubscribeResult(False, '')

        subscription = GitChannelSub(channel_id, guild_id, parsed_url, filter_string, update_interval, datetime.now())
        session.add(subscription)
        session.commit()

    # notify
    end_date = datetime.now()
    start_date = end_date - timedelta(days=update_interval)
    repo_type = 'remote'
    branch = repo_filter.get('branch', None)
    author = repo_filter.get('author', None)

    batched_commits = fetch_commits(parsed_url, start_date, end_date, repo_type=repo_type,
                                    branch=branch, author=author, config=riddlesolver_config)
    summary = generate_summary(batched_commits, riddlesolver_config)

    return SubscribeResult(True, summary)


async def git_unsubscribe(channel_id, *args) -> bool:
    with get_session() as session:
        subscriptions = session.query(GitChannelSub).filter_by(channel_id=channel_id).all()
        if subscriptions is None:
            return False

        dirty = False
        unsubscribe_list = []
        for arg in args:
            try:
                unsubscribe_list.append(RssUtils.extract_url(str(arg)))
            except Exception as e:
                logger.error(f"Unable to extract url {arg}. {e}")

        for sub in subscriptions:
            if sub.repo_url in unsubscribe_list:
                session.delete(sub)
                dirty = True

        if dirty:
            session.commit()
            return True

    return False
