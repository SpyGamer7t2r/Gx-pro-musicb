import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from EsproMusic import LOGGER, app, userbot
from EsproMusic.core.call import Loy
from EsproMusic.misc import sudo
from EsproMusic.plugins import ALL_MODULES
from EsproMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("❌ Assistant client variables not defined, exiting...")
        exit()

    await sudo()

    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)

        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except Exception as e:
        LOGGER(__name__).warning(f"Couldn't fetch banned users: {e}")

    await app.start()

    # ✅ FIXED: Correct plugin import
    for all_module in ALL_MODULES:
        try:
            importlib.import_module(f"EsproMusic.plugins.{all_module}")
            LOGGER("EsproMusic.plugins").info(f"✅ Loaded module: {all_module}")
        except Exception as e:
            LOGGER("EsproMusic.plugins").error(f"❌ Failed to load module {all_module}: {e}")

    LOGGER("EsproMusic.plugins").info("✅ Successfully imported all modules.")

    await userbot.start()
    await Loy.start()

    try:
        await Loy.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("EsproMusic").error(
            "❌ No active group call. Please start a videochat in your log group/channel.\nStopping bot..."
        )
        exit()
    except Exception as e:
        LOGGER("EsproMusic").warning(f"Stream call error: {e}")

    await Loy.decorators()
    LOGGER("EsproMusic").info(
        "🎶 Espro Music Bot Started Successfully.\n\nFor help, contact @EsproSupport"
    )

    await idle()

    await app.stop()
    await userbot.stop()
    LOGGER("EsproMusic").info("🛑 Stopping Espro Music Bot...")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())