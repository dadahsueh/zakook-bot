﻿import logging

from khl.card import Card, CardMessage, Element, Module, Types

from bot.configs.bot_config import settings
from bot.utils.rss_utils import RssUtils

logger = logging.getLogger(__name__)

"""
This module only builds the card messages
"""


def help_card_msg(specification=None) -> CardMessage:
    logger.info(f"Build help card message")
    card_msg = CardMessage()
    card = Card(theme=Types.Theme.INFO)
    card.append(Module.Header(f"💩  {settings.BOT_NAME} 使用攻略"))
    card.append(Module.Context(f"版本: {settings.BOT_VERSION} | 一个没有什么卵用的Bot"))
    card.append(Module.Divider())

    help_str = ""
    help_str += f"`/help`: get usage.\n"
    help_str += f"`/jini`: ping pong check.\n"
    help_str += f"`/clear`: clears all messages of a text channel.\n"
    help_str += f"`/rss sub [url]`: subscribes the current channel to a rss feed, immediately posts the newest entry and periodically posts new entries.\n"
    help_str += f"`/rss unsub [url]`: unsubscribes the current channel from a rss feed.\n"
    help_str += f"`/rss list`: see a list of rss feeds the current channel is subscribed to.\n"
    help_str += f"`/rss unsub [all/*]` or `/rss unsuball`: unsubscribes the current channel from all rss feeds.\n"

    card.append(Module.Section(Element.Text(help_str)))
    card.append(Module.Divider())

    bottom_str = f"TODO 清理屎山 谁来帮我改改 🤡"
    card.append(Module.Context(Element.Text(bottom_str)))
    card_msg.append(card)
    return card_msg


def exception_card_msg(e: Exception) -> CardMessage:
    logger.info(f"Build exception card message {e}")
    card_msg = CardMessage()
    card = Card(theme=Types.Theme.SECONDARY, size=Types.Size.SM)
    card.append(Module.Header(f"Oops."))
    card.append(Module.Context(Element.Text(f"```\n{e}```", type=Types.Text.KMD)))
    card_msg.append(card)
    return card_msg


def rss_card_msg_from_entry(feed_title, entry, compatibility_mode=False) -> CardMessage:
    title = RssUtils.parse_title(entry)
    date = RssUtils.parse_date(entry)
    link = RssUtils.parse_link(entry)
    image = ''
    if not compatibility_mode:
        image = RssUtils.parse_image(entry)
    summary = RssUtils.parse_summary(entry)
    tags = RssUtils.parse_tags(entry)
    return rss_card_msg(feed_title, title, date, link, image, summary, tags)


def rss_card_msg(feed_title, title, date, link, image, summary, tags) -> CardMessage:
    logger.debug(f"Build RSS card message {feed_title} {title} {link} {image} {summary}")
    card_msg = CardMessage()
    card = Card(color=RssUtils.color_code_from_string(feed_title))
    card.append(Module.Header(f"{title}"))
    if len(date) > 0:
        card.append(Module.Context(f"{date}"))
    if len(tags) > 0:
        card.append(Module.Context(f"{tags}"))
    card.append(Module.Divider())
    if len(image) > 0:
        if len(summary) > 0:
            card.append(
                Module.Section(Element.Text(summary), Element.Image(image, size=Types.Size.LG),
                               mode=Types.SectionMode.RIGHT))
        else:
            card.append(
                Module.Container(Element.Image(src=image)))
    else:
        card.append(
            Module.Section(Element.Text(summary)))
    card.append(
        Module.Section('', Element.Button(text='让我康康', value=link, click=Types.Click.LINK, theme=Types.Theme.INFO)))
    card.append(Module.Divider())
    if len(feed_title) > 0:
        card.append(Module.Context(Element.Text(f"`{feed_title}`", type=Types.Text.KMD)))
    card_msg.append(card)
    return card_msg
