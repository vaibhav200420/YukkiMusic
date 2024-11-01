#
# Copyright (C) 2024 by TheTeamVivek@Github, < https://github.com/TheTeamVivek >.
#
# This file is part of < https://github.com/TheTeamVivek/YukkiMusic > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TheTeamVivek/YukkiMusic/blob/master/LICENSE >
#
# All rights reserved.
#
import uvloop

uvloop.install()


import sys

from telethon import TelegramClient
from pyrogram.enums import ChatMemberStatus

from telethon.errors import (
    ChatSendPhotosForbiddenError,
    ChatWriteForbiddenError
    FloodWaitError,
    MessageIdInvalidError,
)

from pyrogram.types import (
    BotCommand,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
)

import config

from ..logging import LOGGER


class YukkiBot(TelegramClient):
    def __init__(self):
        LOGGER(__name__).info(f"Starting Bot")
        super().__init__(
            "YukkiMusic",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            flood_sleep_threshold=240,
        )

    async def edit_message(self, *args, **kwargs):
        try:
            return await super().edit_message(*args, **kwargs)
        except FloodWaitError as e:
            time = int(e.seconds)
            await asyncio.sleep(time)
            if time < 25:
                return await self.edit_message_text(self, *args, **kwargs)
        except MessageIdInvalidError:
            pass

    async def send_message(self, *args, **kwargs):
        if kwargs.get("send_direct", False):
            kwargs.pop("send_direct", None)
            return await super().send_message(*args, **kwargs)

        try:
            return await super().send_message(*args, **kwargs)
        except FloodWaitError as e:
            time = int(e.seconds)
            await asyncio.sleep(time)
            if time < 25:
                return await self.send_message(self, *args, **kwargs)
        except ChatWriteForbiddenError:
            chat_id = kwargs.get("chat_id") or args[0]
            if chat_id:
                await self.leave_chat(chat_id)
                

    async def send_file(self, *args, **kwargs):
        try:
            return await super().send_file(*args, **kwargs)
        except FloodWaitError as e:
            time = int(e.seconds)
            await asyncio.sleep(time)
            if time < 25:
                return await self.send_file(self, *args, **kwargs)

    async def start(self):
        await super().start()
        get_me = await self.get_me()
        self.username = get_me.username
        self.id = get_me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.mention = self.me.mention

        try:
            await self.send_message(
                config.LOG_GROUP_ID,
                text=f"<u><b>{self.mention} Bot Started :</b><u>\n\nId : <code>{self.id}</code>\nName : {self.name}\nUsername : @{self.username}",
            )
        except:
            LOGGER(__name__).error(
                "Bot has failed to access the log group. Make sure that you have added your bot to your log channel and promoted as admin!"
            )
            # sys.exit()
        if config.SET_CMDS == str(True):
            try:
                await self.set_bot_commands(
                    commands=[
                        BotCommand("start", "Start the bot"),
                        BotCommand("help", "Get the help menu"),
                        BotCommand("ping", "Check if the bot is alive or dead"),
                    ],
                    scope=BotCommandScopeAllPrivateChats(),
                )
                await self.set_bot_commands(
                    commands=[
                        BotCommand("play", "Start playing requested song"),
                    ],
                    scope=BotCommandScopeAllGroupChats(),
                )
                await self.set_bot_commands(
                    commands=[
                        BotCommand("play", "Start playing requested song"),
                        BotCommand("skip", "Move to next track in queue"),
                        BotCommand("pause", "Pause the current playing song"),
                        BotCommand("resume", "Resume the paused song"),
                        BotCommand("end", "Clear the queue and leave voicechat"),
                        BotCommand("shuffle", "Randomly shuffles the queued playlist."),
                        BotCommand(
                            "playmode",
                            "Allows you to change the default playmode for your chat",
                        ),
                        BotCommand(
                            "settings",
                            "Open the settings of the music bot for your chat.",
                        ),
                    ],
                    scope=BotCommandScopeAllChatAdministrators(),
                )
            except:
                pass
        else:
            pass
        try:
            a = await self.get_chat_member(config.LOG_GROUP_ID, self.id)
            if a.status != ChatMemberStatus.ADMINISTRATOR:
                LOGGER(__name__).error("Please promote bot as admin in logger group")
                sys.exit()
        except Exception:
            pass
        if get_me.last_name:
            self.name = get_me.first_name + " " + get_me.last_name
        else:
            self.name = get_me.first_name
        LOGGER(__name__).info(f"MusicBot started as {self.name}")

    async def stop(self):
        await super().stop()
