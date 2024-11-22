[<img src="https://img.shields.io/badge/Telegram-%40Me-orange">](https://t.me/hhhscvx)

## Functionality

| Functional                                                             | Supported |
| ---------------------------------------------------------------------- | :-------: |
| Multithreading                                                         |    ✅     |
| Binding a proxy to a session                                           |    ✅     |
| Auto Task complete                                                     |    ✅     |
| Random sleep time between complete tasks                               |    ✅     |

## [Change Settings](https://github.com/hhhscvx/GHArenaBot/blob/master/bot/config/config.py)

| Settings              | Description                                                             |
| --------------------- | ----------------------------------------------------------------------- |
| **API_ID / API_HASH** | Platform data from which to launch a Telegram session (stock - Android) |

## Installation

You can download [**Repository**](https://github.com/hhhscvx/GHArenaBot) by cloning it to your system and installing the necessary dependencies:

```shell
~ >>> git clone https://github.com/hhhscvx/GHArenaBot.git
~ >>> cd GHArenaBot

#Linux
~/GHArenaBot >>> python3 -m venv venv
~/GHArenaBot >>> source venv/bin/activate
~/GHArenaBot >>> pip3 install -r requirements.txt
~/GHArenaBot >>> cp .env-example .env
~/GHArenaBot >>> nano .env # Here you must specify your API_ID and API_HASH , the rest is taken by default
~/GHArenaBot >>> python3 main.py

#Windows
~/GHArenaBot >>> python -m venv venv
~/GHArenaBot >>> venv\Scripts\activate
~/GHArenaBot >>> pip install -r requirements.txt
~/GHArenaBot >>> copy .env-example .env
~/GHArenaBot >>> # Specify your API_ID and API_HASH, the rest is taken by default
~/GHArenaBot >>> python main.py
```

[You can change bot settings here](https://github.com/hhhscvx/GHArenaBot/blob/master/bot/config/config.py)

Also for quick launch you can use arguments, for example:
```shell
~/GHArenaBot >>> python3 main.py --action (1/2/3)
# Or
~/GHArenaBot >>> python3 main.py -a (1/2/3)

#1 - Create session
#2 - Run clicker
```