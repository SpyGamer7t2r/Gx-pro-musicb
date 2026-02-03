from pyrogram import Client, errors

import config
from ..logging import LOGGER

assistants = []
assistantids = []


class Userbot:
    def __init__(self):
        self.clients = []

        strings = [
            config.STRING1,
            config.STRING2,
            config.STRING3,
            config.STRING4,
            config.STRING5,
        ]

        for i, session in enumerate(strings, start=1):
            if session:
                self.clients.append(
                    Client(
                        name=f"EsproAss{i}",
                        api_id=config.API_ID,
                        api_hash=config.API_HASH,
                        session_string=str(session),
                        no_updates=True,
                    )
                )

    async def start(self):
        LOGGER(__name__).info("Starting Assistants...")

        for index, client in enumerate(self.clients, start=1):
            try:
                await client.start()
            except Exception as ex:
                LOGGER(__name__).error(
                    f"Assistant {index} failed to start | {type(ex).__name__}"
                )
                continue

            # join support channels (optional)
            for chat in ("EsproSupport", "EsproUpdate"):
                try:
                    await client.join_chat(chat)
                except:
                    pass

            try:
                await client.send_message(config.LOGGER_ID, "Assistant Started")
            except errors.PeerIdInvalid:
                LOGGER(__name__).error(
                    f"Assistant {index} can't access LOGGER_ID. Add & promote assistant."
                )
                raise SystemExit
            except Exception:
                raise SystemExit

            me = await client.get_me()
            client.id = me.id
            client.name = me.mention
            client.username = me.username

            assistants.append(index)
            assistantids.append(client.id)

            LOGGER(__name__).info(
                f"Assistant {index} Started as {client.name}"
            )

    async def stop(self):
        LOGGER(__name__).info("Stopping Assistants...")
        for client in self.clients:
            try:
                await client.stop()
            except:
                pass