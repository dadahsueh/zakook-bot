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

                if feed is None or len(feed.entries) == 0:
                    raise ValueError(f"feed is None or len(feed.entries) == 0 for {url}")

                return feed
            except Exception as e:
                logger.info(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)

        raise ValueError(f"All retries failed to parse {url}")

    @staticmethod
    def extract_url(raw_url):
        try:
            url_pattern = r'(https?:\/\/[^\s()\[\]]+)'
            match = re.search(url_pattern, raw_url)
            if match is None:
                raise ValueError(f"could not parse url from > {raw_url}")
            url = match.group(1)
            return url
        except Exception as e:
            logger.error(f"Failed extract url from {raw_url}. {e}")
            raise

    @staticmethod
    def string_truncate(string, max_length):
        if len(string) > max_length:
            return string[:max_length] + '…'
        else:
            return string

    @staticmethod
    def parse_feed_title(feed, max_length=42):
        if 'feed' not in feed:
            return ''
        feed_title = feed.feed.get('title', '')
        return RssUtils.string_truncate(feed_title, max_length)

    @staticmethod
    def parse_title(entry: dict, max_length=64):
        raw_title = entry.get('plaintitle', entry.get('title', ''))
        pattern = r'\/[^\/]*\/|\[[^\]]*\]'
        title = re.sub(pattern, '', raw_title)
        title.strip()
        return RssUtils.string_truncate(title, max_length)

    @staticmethod
    def parse_date(entry: dict):
        if 'published_parsed' not in entry:
            return ''
        beijing_utc_timedelta = timedelta(hours=8)
        entry_date = datetime.utcfromtimestamp(time.mktime(entry['published_parsed'])) + beijing_utc_timedelta
        date_format = "%Y-%m-%d %H:%M:%S"

        date = entry_date.strftime(date_format)
        return date

    @staticmethod
    def parse_link(entry: dict):
        if 'link' not in entry:
            return ''
        link = entry['link']
        return link

    @staticmethod
    def parse_image(entry: dict):
        image = ''
        if 'media_thumbnail' in entry:
            r = re.search(r'(https?://\S+?\.(?:jpg|gif|png))', str(entry['media_thumbnail']))
            image = r.group(1) if r else ''

        if len(image) != 0:
            return image

        if 'summary' in entry:
            r = re.search(r'(?:<img[^>]*src="([^"]+)"[^>]*\/?>)', entry['summary'])
        else:
            return ''

        image = r.group(1) if r else ''
        return image

    @staticmethod
    def parse_summary(entry: dict, max_length=296):
        if 'summary' not in entry:
            return ''
        pattern = r'(?<=<p>).*?(?=<\/p>)'
        r = re.search(pattern, entry['summary'])
        parsed_summary = r.group(0) if r else entry['summary']
        pattern = r'<\/?[^>]+>|<img[^>]+\/?>'
        parsed_summary = re.sub(pattern, '', parsed_summary)
        # prevent consecutive line breaks
        parsed_summary = re.sub(r'[\n\s]+', '\n', parsed_summary)
        return RssUtils.string_truncate(parsed_summary, max_length)

    @staticmethod
    def parse_tags(entry: dict):
        if 'title' not in entry:
            return []
        pattern = r'\/([^\/]*?)\/|\[([^\[\]]*?)\]'
        tags_list = re.findall(pattern, entry['title'])
        tags_list = [match[0] if match[0] else match[1] for match in tags_list]
        tags = ', '.join(tag for tag in tags_list)
        return tags
