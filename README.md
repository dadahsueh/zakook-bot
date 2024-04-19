<h1 align="center">Kookie Bot</h1>

<div align="center">

![GitHub last commit](https://img.shields.io/github/last-commit/dadahsueh/kookie?logo=github&style=for-the-badge)
[![Status](https://img.shields.io/badge/status-active-success.svg?style=for-the-badge)](https://github.com/dadahsueh/kookie)
[![Platform](https://img.shields.io/badge/platform-kook-green?style=for-the-badge)](https://github.com/dadahsueh/kookie)
![github stars](https://img.shields.io/github/stars/dadahsueh/kookie?style=for-the-badge)

</div>

---

<p align="center"> 🤖 Doesn't do much. Simple template bot.
    <br> 
</p>

## 📝 Table of Contents

- [About](#about)
- [Usage](#usage)
- [Getting Started](#getting_started)
- [Deploying your own bot](#deployment)
- [Acknowledgments](#acknowledgement)
- [Resources](#resources)

## 🧐 About <a name = "about"></a>

For educational purposes. ~~Good clean code~~. The bot is intended for Kook, can subscribe to RSS feeds, and ~~definitely~~ ~~probably~~ ~~plausibly~~ maybe scalable. Uses `Python v3.11.9` and [khl.py](https://github.com/TWT233/khl.py).

## 🎈 Usage <a name = "usage"></a>

To begin exploring:

```
/help
```

### Commands

- `/help`: get usage.
- `/jini`: ping pong check.
- `/clear`: clears all messages of a text channel.
- `/rsssub [url]`: subscribes the current channel to a rss feed, immediately posts the newest entry and periodically
  posts new entries.
- `/rssunsub [url]`: unsubscribes the current channel from a rss feed.
- `/rsslist`: see a list of rss feeds the current channel is subscribed to.
- `/rssunsuball`: unsubscribes the current channel from all rss feeds.

## 1️⃣ Getting Started <a name = "getting_started"></a>

These instructions will get you a copy of the project up and running on your local machine for development and testing

### Prerequisites

If you need to clone the repo
```
git clone https://github.com/dadahsueh/kookie.git
cd kookie
mv .env.template .env
```
If you do not see it just manually rename `.env.template` to `.env` and configure the `.env`
```
TOKEN=BOT_TOKEN_HERE

CONTAINER_NAME=kookie-runner

ADMIN_USERS=["635507656"]

BOT_NAME=KOOKIE

BOT_VERSION=v0.0.1

MUSIC_STATUS=["(私人笑声);赛马娘", ";"]
```

### Installing

1. Create activate Python virtual environment

```
virtualenv venv
```
2. Windows or `.venv/Scripts/activate`

```
.venv/Scripts/activate.bat
```

2. Linux/Mac 

```
source venv/bin/activate
```

3. Install dependencies

```
pip install -r requirements.txt
```

4. Annnnnnnnnnd run

```
python main.py
```

## 🚀 Deploying your own bot <a name = "deployment"></a>

TODO - I have no idea how. Yet.

<sup>Beep boop.</sup>

## 🎉 Acknowledgements <a name = "acknowledgement"></a>
- [khl.py Examples](https://github.com/TWT233/khl.py/blob/main/example/README.md)
- [khl.py: Python SDK for KOOK API](https://github.com/TWT233/khl.py)
- [Kook-Source-Query Bot](https://github.com/NyaaaDoge/kook-source-query)
- [Kyouka 镜华 点歌机器人](https://github.com/shuyangzhang/Kyouka/)
- [RSSHub 万物皆可 RSS](https://docs.rsshub.app/zh/)

## 💭 Resources <a name = "resources"></a>
- [Emoji Cheat Sheet](https://www.webfx.com/tools/emoji-cheat-sheet/)
- [Emojipedia](https://emojipedia.org/)
