#
# Copyright (C) 2024 by TheTeamVivek@Github, < https://github.com/TheTeamVivek >.
#
# This file is part of < https://github.com/TheTeamVivek/YukkiMusic > project,
# and is released under the MIT License.
# Please see < https://github.com/TheTeamVivek/YukkiMusic/blob/master/LICENSE >
#
# All rights reserved.
#
from telethon import Button

def botplaylist_markup(_):
    buttons = [
        [
            Button.inline(
                text=_["PL_B_1"],
                data="get_playlist_playmode",
            ),
            Button.inline(text=_["PL_B_8"], data="get_top_playlists"),
        ],
        [
            Button.inline(text=_["PL_B_4"], data="PM"),
            Button.inline(text=_["CLOSE_BUTTON"], data="close"),
        ],
    ]
    return buttons

def top_play_markup(_):
    buttons = [
        [Button.inline(text=_["PL_B_9"], data="SERVERTOP global")],
        [Button.inline(text=_["PL_B_10"], data="SERVERTOP chat")],
        [Button.inline(text=_["PL_B_11"], data="SERVERTOP user")],
        [
            Button.inline(text=_["BACK_BUTTON"], data="get_playmarkup"),
            Button.inline(text=_["CLOSE_BUTTON"], data="close"),
        ],
    ]
    return buttons

def get_playlist_markup(_):
    buttons = [
        [
            Button.inline(text=_["P_B_1"], data="play_playlist a"),
            Button.inline(text=_["P_B_2"], data="play_playlist v"),
        ],
        [
            Button.inline(text=_["BACK_BUTTON"], data="home_play"),
            Button.inline(text=_["CLOSE_BUTTON"], data="close"),
        ],
    ]
    return buttons

def failed_top_markup(_):
    buttons = [
        [
            Button.inline(
                text=_["BACK_BUTTON"],
                data="get_top_playlists",
            ),
            Button.inline(text=_["CLOSE_BUTTON"], data="close"),
        ],
    ]
    return buttons

def warning_markup(_):
    buttons = [
        [
            Button.inline(
                text=_["PL_B_7"],
                data="delete_whole_playlist",
            ),
        ],
        [
            Button.inline(
                text=_["BACK_BUTTON"],
                data="del_back_playlist",
            ),
            Button.inline(
                text=_["CLOSE_BUTTON"],
                data="close",
            ),
        ],
    ]
    return buttons

def close_markup(_):
    buttons = [
        [
            Button.inline(
                text=_["CLOSE_BUTTON"],
                data="close",
            ),
        ]
    ]
    return buttons