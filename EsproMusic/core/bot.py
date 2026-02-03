from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus, ParseMode

import config
from ..logging import LOGGER


class Loy(Client):
    def __init__(self):
        LOGGER(__name__).info("Starting Bot...")
        super().__init__(
            name="EsproMusic",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            parse_mode=ParseMode.HTML,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        await super().start()

        # ─── SAFE ME DATA ───
        me = await self.get_me()
        self.id = me.id
        self.name = f"{me.first_name} {me.last_name or ''}".strip()
        self.username = me.username
        self.mention = me.mention

        # ─── LOG GROUP MESSAGE ───
        try:
            await self.send_message(
                chat_id=config.LOGGER_ID,
                text=(
                    f"<u><b>» {self.mention} Bot Started :</b></u>\n\n"
                    f"ID : <code>{self.id}</code>\n"
                    f"Name : {self.name}\n"
                    f"Username : @{self.username}"
                ),
            )
        except (errors.ChannelInvalid, errors.PeerIdInvalid):
            LOGGER(__name__).error(
                "Bot can't access LOGGER_ID. Add bot to log group/channel."
            )
            raise SystemExit
        except Exception as ex:
            LOGGER(__name__).error(
                f"Failed to access LOGGER_ID | Reason: {type(ex).__name__}"
            )
            raise SystemExit

        # ─── ADMIN CHECK (ONLY FOR GROUPS) ───
        try:
            member = await self.get_chat_member(config.LOGGER_ID, self.id)
            if member.status not in (
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER,
            ):
                LOGGER(__name__).error(
                    "Bot is not admin in LOGGER_ID group."
                )
                raise SystemExit
        except errors.ChatAdminRequired:
            pass  # channel case, ignore
        except errors.ChatNotModified:
            pass
        except Exception:
            pass

        LOGGER(__name__).info(f"Music Bot Started Successfully as {self.name}")

    async def stop(self):
        LOGGER(__name__).info("Stopping Bot...")
        await super().stop()