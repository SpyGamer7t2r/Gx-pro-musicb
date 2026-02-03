import random
import string

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InputMediaPhoto, Message
from pytgcalls.exceptions import NoActiveGroupCall

import config
from EsproMusic import Apple, Resso, SoundCloud, Spotify, Telegram, YouTube, app
from EsproMusic.core.call import Loy
from EsproMusic.utils import seconds_to_min, time_to_seconds
from EsproMusic.utils.channelplay import get_channeplayCB
from EsproMusic.utils.decorators.language import languageCB
from EsproMusic.utils.decorators.play import PlayWrapper
from EsproMusic.utils.formatters import formats
from EsproMusic.utils.inline import (
    botplaylist_markup,
    livestream_markup,
    playlist_markup,
    slider_markup,
    track_markup,
)
from EsproMusic.utils.logger import play_logs
from EsproMusic.utils.stream.stream import stream
from config import BANNED_USERS, lyrical


# ───────────────────────── PLAY COMMAND ───────────────────────── #

@app.on_message(
    filters.command(
        [
            "play", "vplay", "cplay", "cvplay",
            "playforce", "vplayforce", "cplayforce", "cvplayforce",
        ]
    )
    & filters.group
    & ~BANNED_USERS
)
@PlayWrapper
async def play_commnd(client, message: Message, _, chat_id, video, channel, playmode, url, fplay):

    mystic = await message.reply_text(
        _["play_2"].format(channel) if channel else _["play_1"]
    )

    plist_id = None
    plist_type = None
    slider = False
    spotify = None
    details = None
    img = None
    cap = None

    user_id = message.from_user.id
    user_name = message.from_user.first_name

    # ───── TELEGRAM MEDIA ─────
    reply = message.reply_to_message
    audio = reply.audio if reply and reply.audio else reply.voice if reply and reply.voice else None
    video_tg = reply.video if reply and reply.video else reply.document if reply and reply.document else None

    if audio:
        if audio.file_size > 104857600:
            return await mystic.edit_text(_["play_5"])
        if audio.duration > config.DURATION_LIMIT:
            return await mystic.edit_text(_["play_6"].format(config.DURATION_LIMIT_MIN, app.mention))

        file_path = await Telegram.get_filepath(audio=audio)
        if not await Telegram.download(_, message, mystic, file_path):
            return

        details = {
            "title": await Telegram.get_filename(audio, audio=True),
            "link": await Telegram.get_link(message),
            "path": file_path,
            "dur": await Telegram.get_duration(audio, file_path),
        }

        await stream(_, mystic, user_id, details, chat_id, user_name, message.chat.id, streamtype="telegram", forceplay=fplay)
        await mystic.delete()
        return

    if video_tg:
        if video_tg.file_size > config.TG_VIDEO_FILESIZE_LIMIT:
            return await mystic.edit_text(_["play_8"])

        file_path = await Telegram.get_filepath(video=video_tg)
        if not await Telegram.download(_, message, mystic, file_path):
            return

        details = {
            "title": await Telegram.get_filename(video_tg),
            "link": await Telegram.get_link(message),
            "path": file_path,
            "dur": await Telegram.get_duration(video_tg, file_path),
        }

        await stream(_, mystic, user_id, details, chat_id, user_name, message.chat.id, video=True, streamtype="telegram", forceplay=fplay)
        await mystic.delete()
        return

    # ───── URL / SEARCH ─────
    if url:
        if not await YouTube.exists(url):
            return await mystic.edit_text(_["play_3"])
        details, track_id = await YouTube.track(url)
    else:
        if len(message.command) < 2:
            return await mystic.edit_text(_["play_18"], reply_markup=InlineKeyboardMarkup(botplaylist_markup(_)))
        slider = True
        query = message.text.split(None, 1)[1].replace("-v", "")
        details, track_id = await YouTube.track(query)

    if not details:
        return await mystic.edit_text(_["play_3"])

    img = details.get("thumb")
    cap = _["play_10"].format(details.get("title", "Unknown"), details.get("duration_min", "Live"))

    # ───── DIRECT PLAY ─────
    if str(playmode) == "Direct":
        if details.get("duration_min"):
            if time_to_seconds(details["duration_min"]) > config.DURATION_LIMIT:
                return await mystic.edit_text(_["play_6"].format(config.DURATION_LIMIT_MIN, app.mention))
        else:
            return await mystic.edit_text(
                _["play_13"],
                reply_markup=InlineKeyboardMarkup(
                    livestream_markup(_, track_id, user_id, "v" if video else "a", "c" if channel else "g", "f" if fplay else "d")
                ),
            )

        await stream(_, mystic, user_id, details, chat_id, user_name, message.chat.id, video=video, streamtype="youtube", spotify=spotify, forceplay=fplay)
        await mystic.delete()
        return await play_logs(message, streamtype="youtube")

    # ───── INLINE UI ─────
    if slider:
        buttons = slider_markup(_, track_id, user_id, query, 0, "c" if channel else "g", "f" if fplay else "d")
    else:
        buttons = track_markup(_, track_id, user_id, "c" if channel else "g", "f" if fplay else "d")

    await mystic.delete()
    await message.reply_photo(photo=img, caption=cap, reply_markup=InlineKeyboardMarkup(buttons))
    return await play_logs(message, streamtype="inline")


# ───────────────────────── CALLBACK: MUSICSTREAM ───────────────────────── #

@app.on_callback_query(filters.regex("MusicStream") & ~BANNED_USERS)
@languageCB
async def play_Music(client, CallbackQuery, _):
    data = CallbackQuery.data.split(None, 1)[1]
    vidid, user_id, mode, cplay, fplay = data.split("|")

    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(_["playcb_1"], show_alert=True)

    chat_id, channel = await get_channeplayCB(_, cplay, CallbackQuery)
    await CallbackQuery.message.delete()
    mystic = await CallbackQuery.message.reply_text(_["play_2"].format(channel) if channel else _["play_1"])

    details, track_id = await YouTube.track(vidid, True)
    if not details:
        return await mystic.edit_text(_["play_3"])

    if details.get("duration_min"):
        if time_to_seconds(details["duration_min"]) > config.DURATION_LIMIT:
            return await mystic.edit_text(_["play_6"].format(config.DURATION_LIMIT_MIN, app.mention))
    else:
        return await mystic.edit_text(
            _["play_13"],
            reply_markup=InlineKeyboardMarkup(
                livestream_markup(_, track_id, user_id, mode, "c" if cplay == "c" else "g", "f" if fplay else "d")
            ),
        )

    await stream(_, mystic, user_id, details, chat_id, CallbackQuery.from_user.first_name, CallbackQuery.message.chat.id, video=(mode == "v"), streamtype="youtube", forceplay=(fplay == "f"))
    await mystic.delete()


# ───────────────────────── CALLBACK: PLAYLIST ───────────────────────── #

@app.on_callback_query(filters.regex("LoyPlaylists") & ~BANNED_USERS)
@languageCB
async def play_playlists_command(client, CallbackQuery, _):
    data = CallbackQuery.data.split(None, 1)[1]
    hash_id, user_id, ptype, mode, cplay, fplay = data.split("|")

    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(_["playcb_1"], show_alert=True)

    videoid = lyrical.get(hash_id)
    if not videoid:
        return await CallbackQuery.answer(_["play_3"], show_alert=True)

    chat_id, channel = await get_channeplayCB(_, cplay, CallbackQuery)
    await CallbackQuery.message.delete()
    mystic = await CallbackQuery.message.reply_text(_["play_2"].format(channel) if channel else _["play_1"])

    if ptype == "yt":
        result = await YouTube.playlist(videoid, config.PLAYLIST_FETCH_LIMIT, user_id, True)
        spotify = False
    elif ptype == "spplay":
        result, _ = await Spotify.playlist(videoid)
        spotify = True
    elif ptype == "spalbum":
        result, _ = await Spotify.album(videoid)
        spotify = True
    elif ptype == "spartist":
        result, _ = await Spotify.artist(videoid)
        spotify = True
    elif ptype == "apple":
        result, _ = await Apple.playlist(videoid, True)
        spotify = True
    else:
        return await mystic.edit_text(_["play_3"])

    await stream(_, mystic, user_id, result, chat_id, CallbackQuery.from_user.first_name, CallbackQuery.message.chat.id, video=(mode == "v"), streamtype="playlist", spotify=spotify, forceplay=(fplay == "f"))
    await mystic.delete()


# ───────────────────────── CALLBACK: SLIDER ───────────────────────── #

@app.on_callback_query(filters.regex("slider") & ~BANNED_USERS)
@languageCB
async def slider_queries(client, CallbackQuery, _):
    data = CallbackQuery.data.split(None, 1)[1]
    what, rtype, query, user_id, cplay, fplay = data.split("|")

    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(_["playcb_1"], show_alert=True)

    rtype = int(rtype)
    query_type = rtype + 1 if what == "F" else rtype - 1
    query_type = 0 if query_type > 9 else 9 if query_type < 0 else query_type

    title, duration_min, thumb, vidid = await YouTube.slider(query, query_type)
    buttons = slider_markup(_, vidid, user_id, query, query_type, cplay, fplay)

    await CallbackQuery.edit_message_media(
        InputMediaPhoto(
            media=thumb,
            caption=_["play_10"].format(title.title(), duration_min),
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
    )