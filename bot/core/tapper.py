import asyncio
from random import randint
from typing import Any
from urllib.parse import unquote
from http import HTTPStatus

from aiohttp import ClientSession, ClientTimeout
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import AuthKeyUnregistered, FloodWait, Unauthorized, UserDeactivated
from pyrogram.raw.functions.messages.request_web_view import RequestWebView

from bot.config import InvalidSession, settings
from .headers import headers
from bot.utils import logger


class Tapper:
    def __init__(self, tg_client: Client) -> None:
        self.session_name = tg_client.name
        self.tg_client = tg_client

    async def get_tg_web_data(self, proxy: str | None) -> str:
        if proxy:
            proxy: Proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            with_tg = True

            if not self.tg_client.is_connected:
                with_tg = False
                try:
                    await self.tg_client.connect()
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            while True:
                try:
                    peer = await self.tg_client.resolve_peer('GHArenaBot')
                    break
                except FloodWait as fl:
                    fls = fl.value

                    logger.warning(f"{self.session_name} | FloodWait {fl}")
                    logger.info(f"{self.session_name} | Sleep {fls}s")

                    await asyncio.sleep(fls + 3)

            web_view = await self.tg_client.invoke(RequestWebView(
                peer=peer,
                bot=peer,
                platform='android',
                from_bot_menu=False,
                url='https://game.gh-arena.com/base/'
            ))

            auth_url = web_view.url
            query = unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])

            if with_tg is False:
                await self.tg_client.disconnect()

            return query

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error during Authorization: {error}")
            await asyncio.sleep(delay=3)

    async def login(self, http_client: ClientSession, tg_web_data: str) -> bool:
        try:
            http_client.headers['Authorization'] = tg_web_data

            return True
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error while Login: {error}")
            await asyncio.sleep(delay=3)

    async def get_me(self, http_client: ClientSession) -> dict:
        try:
            response = await http_client.get(url='https://game.gh-arena.com/user/')
            response.raise_for_status()

            return await response.json()
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when get user: {error}")
            await asyncio.sleep(delay=3)

    async def change_settings(self, http_client: ClientSession, key: str, value: bool | Any) -> True:
        try:
            response = await http_client.post(url='https://game.gh-arena.com/settings/',
                                              json={key: value})
            response.raise_for_status()

            return await response.json()
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when change settings: {error}")
            await asyncio.sleep(delay=3)

    async def get_quests(self, http_client: ClientSession) -> list[dict]:
        try:
            response = await http_client.get(url='https://game.gh-arena.com/quests/')
            response.raise_for_status()

            return await response.json()
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when get quests: {error}")
            await asyncio.sleep(delay=3)

    async def get_quest_tasks(self, http_client: ClientSession, quest_id: int) -> dict:
        try:
            response = await http_client.get(url=f'https://game.gh-arena.com/quest/{quest_id}/tasks/')
            response.raise_for_status()

            return await response.json()
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when get quest tasks: {error}")
            await asyncio.sleep(delay=3)

    async def complete_task(self, http_client: ClientSession, task_id: int) -> dict:
        try:
            response = await http_client.post(url=f'https://game.gh-arena.com/task/{task_id}/complete/')

            return await response.json()
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when complete task: {error}")
            await asyncio.sleep(delay=3)

    async def complete_quest(self, http_client: ClientSession, quest_id: int) -> dict:
        try:
            response = await http_client.post(url=f'https://game.gh-arena.com/quest/{quest_id}/complete/')

            return await response.json()
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when complete quest: {error}")
            await asyncio.sleep(delay=3)

    async def check_proxy(self, http_client: ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=ClientTimeout(5))
            ip = (await response.json()).get('origin')
            logger.info(f"{self.session_name} | Proxy IP: {ip}")
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")

    async def run(self, proxy: str | None) -> None:
        """Пока что только выполняет задания"""

        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

        async with ClientSession(headers=headers, connector=proxy_conn) as http_client:
            if proxy:
                await self.check_proxy(http_client=http_client, proxy=proxy)


            tg_web_data = await self.get_tg_web_data(proxy=proxy)
            login = await self.login(http_client=http_client, tg_web_data=tg_web_data)
            user = await self.get_me(http_client)
            balance_gold = user['balance']
            balance_gem = user['gem']
            logger.success(f"{self.session_name} | Login! Balance: {balance_gold} gold | {balance_gem} gems")
            await asyncio.sleep(0.5)
            await self.change_settings(http_client, 'skipTutorial', True)

            attempt = 1
            while login is not True:
                sleep_time = randint(*settings.RELOGIN_DELAY)
                logger.info(f"{self.session_name} | Problems when login, sleep {sleep_time}s before attempt #{attempt + 1}")
                await asyncio.sleep(sleep_time)
                tg_web_data = await self.get_tg_web_data(proxy=proxy)
                login = await self.login(http_client=http_client, tg_web_data=tg_web_data)
                attempt += 1
                if attempt > 5:
                    return logger.info(f"{self.session_name} | All login attempts spent")


            quests = await self.get_quests(http_client)
            await asyncio.sleep(1)
            for quest in quests:
                quest_name = quest['name']
                quest_rewards = quest['gold'] if quest['gold'] is not None else quest['gem']
                quest_rewards_type = 'gems' if quest['gem'] is not None else 'gold'
                quest_tasks = (await self.get_quest_tasks(http_client, quest_id=quest['id'])).get('tasks')
                await asyncio.sleep(1.5)
                for task in quest_tasks:
                    task_name = task['name']
                    if task['completed'] is True:
                        logger.info(f"{self.session_name} | Task '{task_name}' is already completed, Skip..")
                        continue
                    complete = await self.complete_task(http_client, task_id=task['id'])
                    sleep_time = randint(*settings.SLEEP_BETWEEN_TASK)
                    await asyncio.sleep(sleep_time)
                    if (complete_error := complete.get('error', None)) is not None:
                        logger.warning(f"{self.session_name} | Error when complete task '{task_name}': '{complete_error}'")
                    else:
                        logger.success(f"{self.session_name} | Successfully completed task '{task_name}'!")
                
                complete_quest = await self.complete_quest(http_client, quest_id=quest['id'])
                sleep_time = randint(*settings.SLEEP_BETWEEN_TASK)
                await asyncio.sleep(sleep_time)
                if (complete_error := complete_quest.get('error', None)) is not None:
                    logger.warning(f"{self.session_name} | Problems when complete quest '{quest_name}': '{complete_error}'")
                else:
                    logger.success(f"{self.session_name} | Successfully completed quest '{quest_name}'! +{quest_rewards} {quest_rewards_type}")


async def run_tapper(tg_client: Client, proxy: str | None):
    try:
        await Tapper(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")
