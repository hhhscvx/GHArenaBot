import asyncio
from typing import Any
from urllib.parse import unquote

from aiohttp import ClientSession
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import AuthKeyUnregistered, FloodWait, Unauthorized, UserDeactivated
from pyrogram.raw.functions.messages.request_web_view import RequestWebView

from bot.config import InvalidSession
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
                    peer = await self.tg_client.resolve_peer('Yumify_Bot')
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
        """TODO skipTutorial:true"""
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
