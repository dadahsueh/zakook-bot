import asyncio
import logging
import re
import time
from datetime import datetime, timedelta

import feedparser

logger = logging.getLogger(__name__)


class RssUtils(object):
    @staticmethod
    async def parse_feed_with_retry(url, max_retries=3, retry_delay=1):
        for attempt in range(max_retries):
            try:
                feed = feedparser.parse(url)
                return feed
            except Exception as e:
                print(f"Attempt {attempt + 1} failed:", e)
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)

        # If all retries fail, return None or raise an exception, as needed
        return None

    @staticmethod
    def string_truncate(string, max_length):
        if len(string) > max_length:
            return string[:max_length] + '…'
        else:
            return string

    @staticmethod
    def parse_feed_title(feed, max_length=32):
        try:
            if 'feed' not in feed:
                return ''
            feed_title = feed.feed.get('title', '')
            return RssUtils.string_truncate(feed_title, max_length)
        except Exception as e:
            logger.exception(f"Failed. {e}", exc_info=False)
            return ''

    @staticmethod
    def parse_title(entry: dict, max_length=32):
        try:
            raw_title = entry.get('plaintitle', entry.get('title', ''))
            pattern = r'\/[^\/]*\/|\[[^\]]*\]'
            title = re.sub(pattern, '', raw_title)
            title.strip()
            return RssUtils.string_truncate(title, max_length)
        except Exception as e:
            logger.exception(f"Failed. {e}", exc_info=False)
            return ''

    @staticmethod
    def parse_date(entry: dict):
        try:
            if 'published_parsed' not in entry:
                return ''
            beijing_utc_timedelta = timedelta(hours=8)
            entry_date = datetime.utcfromtimestamp(time.mktime(entry['published_parsed'])) + beijing_utc_timedelta
            date_format = "%Y-%m-%d %H:%M:%S"

            date = entry_date.strftime(date_format)
            return date
        except Exception as e:
            logger.exception(f"Failed. {e}", exc_info=False)
            return ''

    @staticmethod
    def parse_link(entry: dict):
        try:
            if 'link' not in entry:
                return ''
            link = entry['link']
            return link
        except Exception as e:
            logger.exception(f"Failed. {e}", exc_info=False)
            return ''

    @staticmethod
    def parse_image(entry: dict):
        try:
            pattern = r'https?://\S+?\.(?:jpg|gif|png)'
            image = ''
            if 'media_thumbnail' in entry:
                r = re.search(pattern, str(entry['media_thumbnail']))
                image = r.group(0) if r else ''

            if len(image) != 0:
                return image

            if 'summary' in entry:
                r = re.search(pattern, entry['summary'])
            else:
                return ''

            image = r.group(0) if r else ''
            return image
        except Exception as e:
            logger.exception(f"Failed. {e}", exc_info=False)
            return ''

    @staticmethod
    def parse_summary(entry: dict, max_length=256):
        try:
            if 'summary' not in entry:
                return ''
            pattern = r'(?<=<p>).*?(?=<\/p>)'
            r = re.search(pattern, entry['summary'])
            parsed_summary = r.group(0) if r else entry['summary']
            pattern = r'<\/?[^>]+>|<img[^>]+\/?>'
            parsed_summary = re.sub(pattern, '', parsed_summary)
            return RssUtils.string_truncate(parsed_summary, max_length)
        except Exception as e:
            logger.exception(f"Failed. {e}", exc_info=False)
            return ''

    @staticmethod
    def parse_tags(entry: dict):
        try:
            if 'title' not in entry:
                return []
            pattern = r'\/([^\/]*?)\/|\[([^\[\]]*?)\]'
            tags_list = re.findall(pattern, entry['title'])
            tags_list = [match[0] if match[0] else match[1] for match in tags_list]
            tags = ', '.join(tag for tag in tags_list)
            return tags
        except Exception as e:
            logger.exception(f"Failed. {e}", exc_info=False)
            return []
