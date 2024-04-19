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
    def parse_title(entry: dict):
        try:
            raw_title = entry['plaintitle'] if entry.has_key('plaintitle') else entry[
                'title'] if entry.has_key('title') else ''
            pattern = r'\/[^\/]*\/|\[[^\]]*\]'
            title = re.sub(pattern, '', raw_title)
            title.strip()
            return title
        except Exception as e:
            logger.exception(f"Failed. {e}", exc_info=False)
            return ''

    @staticmethod
    def parse_date(entry: dict):
        try:
            if not entry.has_key('published_parsed'):
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
            if not entry.has_key('link'):
                return ''
            link = entry['link']
            return link
        except Exception as e:
            logger.exception(f"Failed. {e}", exc_info=False)
            return ''

    @staticmethod
    def parse_image(entry: dict):
        try:
            if not entry.has_key('summary'):
                return ''
            pattern = r'https?://\S+?\.(?:jpg|gif|png)'
            r = re.search(pattern, entry['summary'])
            image = r.group(0) if r else ''
            return image
        except Exception as e:
            logger.exception(f"Failed. {e}", exc_info=False)
            return ''

    @staticmethod
    def parse_summary(entry: dict):
        try:
            if not entry.has_key('summary'):
                return ''
            pattern = r'(?<=<p>).*?(?=<\/p>)'
            r = re.search(pattern, entry['summary'])
            parsed_summary = r.group(0) if r else entry['summary']
            pattern = r'<\/?[^>]+>|<img[^>]+\/?>'
            parsed_summary = re.sub(pattern, '', parsed_summary)
            return parsed_summary
        except Exception as e:
            logger.exception(f"Failed. {e}", exc_info=False)
            return ''

    @staticmethod
    def parse_tags(entry: dict):
        try:
            if not entry.has_key('title'):
                return []
            pattern = r'\/([^\/]*?)\/|\[([^\[\]]*?)\]'
            tags_list = re.findall(pattern, entry['title'])
            tags_list = [match[0] if match[0] else match[1] for match in tags_list]
            tags = ', '.join(tag for tag in tags_list)
            return tags
        except Exception as e:
            logger.exception(f"Failed. {e}", exc_info=False)
            return []
