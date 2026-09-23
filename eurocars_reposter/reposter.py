"""Repost new Eurocar channel messages using a user Telegram session."""

import asyncio
import logging
import os
import re
import sqlite3
from pathlib import Path

from telethon import TelegramClient, events
from telethon.sessions import StringSession


SOURCE = os.getenv("SOURCE_CHANNEL", "eurocar_group")
DESTINATION = os.getenv("DESTINATION_CHANNEL", "Euro_Cars_Official")
CONTACT = os.getenv("CONTACT", "@Boris_GlobalAuto")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() != "false"
DB_PATH = os.getenv("DB_PATH", "./private/reposted.sqlite3")

# Telegram usernames, Telegram/WhatsApp links, emails, and international/local
# phone numbers are treated as contact details. Vehicle specifications remain.
CONTACT_TOKEN = re.compile(
    r"(?i)(?<!\w)https?://(?:t\.me|telegram\.me|wa\.me|api\.whatsapp\.com)/[^\s)\]>]+"
    r"|(?<!\w)(?:t\.me|telegram\.me|wa\.me)/[^\s)\]>]+"
    r"|(?<![\w@])@[A-Za-z][A-Za-z0-9_]{4,31}\b"
    r"|\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"
    r"|(?<!\w)(?:\+?7|8)[\s\-()]*(?:\d[\s\-()]*){10}(?!\w)"
)


def rewrite(text: str) -> str:
    """Replace recognizable old contact tokens; retain description and price."""
    text = text or ""
    replacement_found = bool(CONTACT_TOKEN.search(text))
    text = CONTACT_TOKEN.sub(CONTACT, text)
    # Repeated old contacts in a footer become one clear contact line.
    lines = []
    for line in text.splitlines():
        if line.strip() == CONTACT and lines and lines[-1].strip() == CONTACT:
            continue
        lines.append(line)
    text = "\n".join(lines).strip()
    if not replacement_found and CONTACT.lower() not in text.lower():
        text = f"{text}\n\n📩 Связаться: {CONTACT}" if text else f"📩 Связаться: {CONTACT}"
    return text


def db_connect():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.execute("CREATE TABLE IF NOT EXISTS delivered (source_id INTEGER PRIMARY KEY)")
    connection.commit()
    return connection


async def main():
    required = ("TG_API_ID", "TG_API_HASH", "TG_SESSION")
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        logging.warning("Waiting for Railway variables: %s. Set them and redeploy.", ", ".join(missing))
        await asyncio.Event().wait()
        return
    api_id = int(os.environ["TG_API_ID"])
    api_hash = os.environ["TG_API_HASH"]
    connection = db_connect()
    client = TelegramClient(StringSession(os.environ["TG_SESSION"]), api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        raise RuntimeError("Telegram session expired; create a new TG_SESSION locally")
    source = await client.get_entity(SOURCE)
    destination = await client.get_entity(DESTINATION)
    lock = asyncio.Lock()

    async def publish(messages):
        ids = [message.id for message in messages]
        async with lock:
            if any(connection.execute("SELECT 1 FROM delivered WHERE source_id=?", (mid,)).fetchone() for mid in ids):
                return
            caption = rewrite(next((m.raw_text for m in messages if m.raw_text), ""))
            media = [m.media for m in messages if m.media]
            if DRY_RUN:
                logging.info("PREVIEW ids=%s media=%s text=%r", ids, len(media), caption)
                return
            if media:
                if len(media) == 1:
                    await client.send_file(destination, media[0], caption=caption)
                else:
                    await client.send_file(destination, media, caption=caption)
            elif caption:
                await client.send_message(destination, caption)
            else:
                return
            connection.executemany("INSERT OR IGNORE INTO delivered VALUES (?)", [(mid,) for mid in ids])
            connection.commit()
            logging.info("Published source ids=%s", ids)

    @client.on(events.Album(chats=source))
    async def on_album(event):
        await publish(event.messages)

    @client.on(events.NewMessage(chats=source))
    async def on_message(event):
        if event.message.grouped_id:
            return  # Album handler sends grouped media in one publication.
        await publish([event.message])

    logging.info("Listening to @%s -> @%s; dry_run=%s", SOURCE, DESTINATION, DRY_RUN)
    await client.run_until_disconnected()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    asyncio.run(main())
