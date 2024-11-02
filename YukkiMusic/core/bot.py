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

from telethon import events, TelegramClient

from telethon.errors import (
    ChatSendPhotosForbiddenError,
    ChatWriteForbiddenError
    FloodWaitError,
    MessageIdInvalidError,
)
from telethon.tl.types import (
    BotCommand,
    BotCommandScopeUsers,
    BotCommandScopeChats,
    BotCommandScopeChatAdmins,
)
from telethon.tl.functions.bots import SetBotCommandsRequest

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
            parse_mode='markdown',
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
        await super().start(bot_token=config.BOT_TOKEN)
        get_me = await self.get_me()
        self.username = get_me.username
        self.id = get_me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.mention = f"[{self.name}](tg://user?id={self.id})"
        try:
            await self.send_message(
                config.LOG_GROUP_ID,
                text=f"<u><b>{self.mention} Bot Started :</b><u>\n\nId : <code>{self.id}</code>\nName : {self.name}\nUsername : @{self.username}",
                parse_mode='html',
            )
        except:
            LOGGER(__name__).error(
                "Bot has failed to access the log group. Make sure that you have added your bot to your log channel and promoted as admin!"
            )
            # sys.exit()
        if config.SET_CMDS == str(True):
            try:
                await self(SetBotCommandsRequest(
                        scope=BotCommandScopeUsers(),
                        commands=[
                            BotCommand("start", "Start the bot"),
                            BotCommand("help", "Get the help menu"),
                            BotCommand("ping", "Check if the bot is alive or dead"),
                        ],
                        lang_code="",
                ))
                await self(BotCommandScopeChats(
                    commands=[
                        BotCommand("play", "Start playing requested song"),
                    ],
                    lang_code="",
                    scope=BotCommandScopeChats(),
                ))
                await self(
                    BotCommandScopeChats(
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
                        lang_code="",
                        scope=BotCommandScopeChatAdmins(),
                    )
                        
                )
            except:
                pass
        else:
            pass
        try:
            a = await self.get_permissions(config.LOG_GROUP_ID, self.id)
            if not a.is_admin:
                LOGGER(__name__).error("Please promote bot as admin in logger group")
                sys.exit()
        except ValueError:
            LOGGER(__name__).error("Please promote bot as admin in logger group")
            sys.exit()
        except Exception:
            pass
        
        LOGGER(__name__).info(f"MusicBot started as {self.name}")

    
    def on_message(self, pattern):

        def decorator(func):
            self.add_event_handler(func, events.NewMessage(pattern=f"^.{pattern} .*"))
            return func

        return decorator