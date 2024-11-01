#
# Copyright (C) 2024 by TheTeamVivek@Github, < https://github.com/TheTeamVivek >.
#
# This file is part of < https://github.com/TheTeamVivek/YukkiMusic > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TheTeamVivek/YukkiMusic/blob/master/LICENSE >
#
# All rights reserved.
#

import asyncio
import os
import time
from datetime import datetime, timedelta
from typing import Union

import aiohttp
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Voice

import config
from config import lyrical
from YukkiMusic import app

from ..utils.formatters import convert_bytes, get_readable_time, seconds_to_min

from telethon import events
from telethon.tl.types import (
    DocumentAttributeFilename,
    DocumentAttributeAudio,
    DocumentAttributeVideo,
    MessageMediaAudio,
    MessageMediaVideo,
    MessageMediaDocument,

)


downloader = {}


class TeleAPI:
    def __init__(self):
        self.chars_limit = 4096
        self.sleep = config.TELEGRAM_DOWNLOAD_EDIT_SLEEP

    async def send_split_text(self, message, string):
        n = self.chars_limit
        out = [(string[i : i + n]) for i in range(0, len(string), n)]
        j = 0
        for x in out:
            if j <= 2:
                j += 1
                await message.reply_text(x)
        return True

    async def get_link(self, event):
        chat = await event.get_chat()
        if chat.username:
            link = f"https://t.me/{chat.username}/{event.message.reply_to.reply_to_msg_id}"
        else:
            xf = str((event.chat_id))[4:]
            link = f"https://t.me/c/{xf}/{event.message.reply_to.reply_to_msg_id}"
        return link

    async def get_filename(self, event: events.NewMessage, audio: Union[bool, str] = None):
        try:
            if event.message.media and event.message.media.document:
                file_name = None
                for attribute in event.message.media.document.attributes:
                    if isinstance(attribute, DocumentAttributeFilename):
                        file_name = attribute.file_name
                        break
                
                if file_name is None:
                    file_name = "Telegram audio file" if audio else "Telegram video file"
            else:
                file_name = "Telegram audio file" if audio else "Telegram video file"
        
        except Exception:
            file_name = "Telegram audio file" if audio else "Telegram video file"
        
        return file_name

    async def get_duration(self, event: events.NewMessage):
        try:
            duration = None
            if event.message.media and event.message.media.document:
                for attribute in event.message.media.document.attributes:
                    if isinstance(attribute, (DocumentAttributeAudio, DocumentAttributeVideo)):
                        duration = attribute.duration
                        break
            dur = seconds_to_min(duration) if duration is not None else "Unknown"
        except Exception:
            dur = "Unknown"
        return dur

    async def get_filepath(self, event: events.NewMessage.Event) -> str:
        file_name = ""

        if event.media:
            if isinstance(event.media, MessageMediaAudio):
                audio = event.media
                file_name = f"{audio.document.id}.ogg"  # Assuming OGG for audio

            elif isinstance(event.media, MessageMediaVideo):
                video = event.media
                file_name = f"{video.document.id}.{video.document.mime_type.split('/')[-1]}"  # Use the correct extension

            elif isinstance(event.media, MessageMediaDocument):
                document = event.media.document
                if document.mime_type.startswith('audio/'):
                    file_name = f"{document.id}.{document.mime_type.split('/')[-1]}"
                elif document.mime_type.startswith('video/'):
                    file_name = f"{document.id}.{document.mime_type.split('/')[-1]}"

            downloads_dir = os.path.realpath("downloads")

            file_name = os.path.join(downloads_dir, file_name)

        return file_name
    
    async def is_streamable_url(self, url: str) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        content_type = response.headers.get("Content-Type", "")
                        if (
                            "application/vnd.apple.mpegurl" in content_type
                            or "application/x-mpegURL" in content_type
                        ):
                            return True
                        if any(
                            keyword in content_type
                            for keyword in [
                                "audio",
                                "video",
                                "mp4",
                                "mpegurl",
                                "m3u8",
                                "mpeg",
                            ]
                        ):
                            return True
                        if url.endswith((".m3u8", ".index", ".mp4", ".mpeg", ".mpd")):
                            return True
        except aiohttp.ClientError:
            pass
        return False

    async def download(self, _, message, mystic, fname):
        left_time = {}
        speed_counter = {}
        if os.path.exists(fname):
            return True

        async def down_load():
            async def progress(current, total):
                if current == total:
                    return
                current_time = time.time()
                start_time = speed_counter.get(message.id)
                check_time = current_time - start_time
                upl = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="🚦 ᴄᴀɴᴄᴇʟ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ",
                                callback_data="stop_downloading",
                            ),
                        ]
                    ]
                )
                if datetime.now() > left_time.get(message.id):
                    percentage = current * 100 / total
                    percentage = str(round(percentage, 2))
                    speed = current / check_time
                    eta = int((total - current) / speed)
                    downloader[message.id] = eta
                    eta = get_readable_time(eta)
                    if not eta:
                        eta = "0 sec"
                    total_size = convert_bytes(total)
                    completed_size = convert_bytes(current)
                    speed = convert_bytes(speed)
                    text = f"""
**{app.mention} ᴛᴇʟᴇɢʀᴀᴍ ᴍᴇᴅɪᴀ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ**

**ᴛᴏᴛᴀʟ ғɪʟᴇ sɪᴢᴇ:** {total_size}
**ᴄᴏᴍᴘʟᴇᴛᴇᴅ:** {completed_size} 
**ᴘᴇʀᴄᴇɴᴛᴀɢᴇ:** {percentage[:5]}%

**sᴘᴇᴇᴅ:** {speed}/s
**ᴇʟᴘᴀsᴇᴅ ᴛɪᴍᴇ:** {eta}"""
                    try:
                        await mystic.edit_text(text, reply_markup=upl)
                    except:
                        pass
                    left_time[message.id] = datetime.now() + timedelta(
                        seconds=self.sleep
                    )

            speed_counter[message.id] = time.time()
            left_time[message.id] = datetime.now()

            try:
                await app.download_media(
                    message.reply_to_message,
                    file_name=fname,
                    progress=progress,
                )
                await mystic.edit_text(
                    "sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ...\n ᴘʀᴏᴄᴇssɪɴɢ ғɪʟᴇ ɴᴏᴡ"
                )
                downloader.pop(message.id, None)
            except:
                await mystic.edit_text(_["tg_2"])

        if len(downloader) > 10:
            timers = []
            for x in downloader:
                timers.append(downloader[x])
            try:
                low = min(timers)
                eta = get_readable_time(low)
            except:
                eta = "Unknown"
            await mystic.edit_text(_["tg_1"].format(eta))
            return False

        task = asyncio.create_task(down_load(), name=f"download_{message.chat.id}")
        lyrical[mystic.id] = task
        await task
        downloaded = downloader.get(message.id)
        if downloaded:
            downloader.pop(message.id)
            return False
        verify = lyrical.get(mystic.id)
        if not verify:
            return False
        lyrical.pop(mystic.id)
        return True
