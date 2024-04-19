import logging

from khl.card import Card, CardMessage, Element, Module, Types

from bot.configs.bot_config import settings
from bot.utils.rss_utils import RssUtils

logger = logging.getLogger(__name__)


def help_card_msg() -> CardMessage:
    logger.debug(f"Build help card message")
    card_msg = CardMessage()
    card = Card(theme=Types.Theme.INFO)
    card.append(Module.Header(f"💩  {settings.BOT_NAME} 使用攻略"))
    card.append(Module.Context(f"版本: {settings.BOT_VERSION}"))
    card.append(Module.Divider())
    help_str = f"""一个没有什么卵用的Bot
- `/help`: get usage.
- `/jini`: ping pong check.
- `/clear`: clears all messages of a text channel.
- `/rsssub [url]`: subscribes the current channel to a rss feed, immediately posts the newest entry and periodically posts new entries.
- `/rssunsub [url]`: unsubscribes the current channel from a rss feed.
- `/rsslist`: see a list of rss feeds the current channel is subscribed to.
- `/rssunsuball`: unsubscribes the current channel from all rss feeds.
"""
    card.append(Module.Section(Element.Text(help_str)))
    card.append(Module.Divider())
    bottom_str = f"""TODO清理屎山。谁来帮我改改🤡
"""
    card.append(Module.Context(Element.Text(bottom_str)))
    card_msg.append(card)
    return card_msg


def rss_card_msg_from_entry(entry) -> CardMessage:
    title = RssUtils.parse_title(entry)
    date = RssUtils.parse_date(entry)
    link = RssUtils.parse_link(entry)
    image = RssUtils.parse_image(entry)
    summary = RssUtils.parse_summary(entry)
    tags = RssUtils.parse_tags(entry)
    return rss_card_msg(title, date, link, image, summary, tags)


def rss_card_msg(title, date, link, image, summary, tags) -> CardMessage:
    logger.debug(f"Build RSS card message")
    card_msg = CardMessage()
    card = Card(theme=Types.Theme.INFO)
    card.append(Module.Header(f"{title}"))
    card.append(Module.Context(f"📅  {date}"))
    if len(tags) > 0:
        card.append(Module.Context(f"{tags}"))
    card.append(Module.Divider())
    card.append(
        Module.Section(Element.Text(summary), Element.Image(image, size=Types.Size.LG), mode=Types.SectionMode.RIGHT))
    # card.append(
    #     Module.Section(Struct.Paragraph(3, "**昵称**\n怪才君", "**服务器**\n活动中心", "**在线时间**\n9:00-21:00")))
    card.append(
        Module.Section('', Element.Button(text='让我康康', value=link, click=Types.Click.LINK, theme=Types.Theme.INFO)))
    card_msg.append(card)
    return card_msg
