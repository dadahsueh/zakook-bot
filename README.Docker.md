# `docker pull dadahsueh/zakook-bot`

#### [Zakook Docker Image](https://hub.docker.com/r/dadahsueh/zakook-bot)


## 📝 Table of Contents

- [Prerequisites](#prerequisites)
- [Running](#running)
- [Building](#building)
- [Resources](#resources)

## 1️⃣ Prerequisites <a name = "prerequisites"></a>
Need to have docker desktop installed [Mac](https://docs.docker.com/desktop/install/mac-install/) / [Windows](https://docs.docker.com/desktop/install/windows-install/) / [Linux](https://docs.docker.com/desktop/install/linux-install/).

Need the `.env` file or manually enter `--env xxx=xxx`

If you want to clone the repo or you can just `touch .env` at the working directory:
```
git clone https://github.com/dadahsueh/zakook-bot.git
cd zakook-bot
mv .env.template .env
```

Configure the `.env` if you are want to use the `--env-file` method
```
TOKEN=BOT_TOKEN_HERE
CONTAINER_NAME=zakook-bot-runner
ADMIN_USERS=["635507656"]
BOT_NAME=ZAKOOK
BOT_VERSION=v0.0.1
MUSIC_STATUS=[";"]
```

## 🎈 Running <a name = "running"></a>

Pull the docker image
```
docker pull dadahsueh/zakook-bot
```

use configured file
```
docker run -i --env-file .env --name zakook-bot-container zakook-bot
```
or manually set `--env xxx=xxx` or short `-e xxx=xxx`
```
docker run -i --env TOKEN=Your_Token_Here --name zakook-bot-container zakook-bot
```

optional `--restart always`, for more info check [Docker Manual](https://docs.docker.com/manuals/).

## 🔨 Building <a name = "building"></a>

Clone git repo
```
git clone https://github.com/dadahsueh/zakook-bot.git
cd zakook-bot
mv .env.template .env
```
Build
```
docker build --no-cache=true -t zakook-bot:latest .
```
Then go see [Running](#running) if you want to run the bot.

<br>

### (Optional) Push tag
if you want to push to a docker repo, rename to your repo:tag
```
docker image tag zakook-bot:latest dadahsueh/zakook-bot:latest
```
push to your repo:tag
```
docker push dadahsueh/zakook-bot:latest
```
remove image with old name
```
docker rmi zakook-bot
```

<br>

## 💭 Resources <a name = "resources"></a>

- [Docker Manual](https://docs.docker.com/manuals/)
