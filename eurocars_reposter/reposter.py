"""Repost new Eurocar channel messages using a user Telegram session."""

import asyncio
import logging
import os
import re
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

from telethon import TelegramClient, events
from telethon.sessions import StringSession


SOURCE = os.getenv("SOURCE_CHANNEL", "eurocar_group")
DESTINATION = os.getenv("DESTINATION_CHANNEL", "Euro_Cars_Official")
DESTINATIONS = list(dict.fromkeys(
    item.strip() for item in os.getenv("DESTINATION_CHANNELS", DESTINATION).split(",")
    if item.strip()
))
CONTACT = os.getenv("CONTACT", "@Boris_GlobalAuto")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() != "false"
DB_PATH = os.getenv("DB_PATH", "./private/reposted.sqlite3")
REPOST_SINCE = datetime.fromisoformat(
    os.getenv("REPOST_SINCE", "2026-09-23T15:49:00+00:00")
).astimezone(timezone.utc)
NEW_DESTINATIONS_SINCE = datetime.fromisoformat(
    os.getenv("NEW_DESTINATIONS_SINCE", REPOST_SINCE.isoformat())
).astimezone(timezone.utc)

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
    connection.execute(
        "CREATE TABLE IF NOT EXISTS delivered_destinations "
        "(source_id INTEGER, destination TEXT, PRIMARY KEY(source_id, destination))"
    )
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
    destinations = []
    for name in DESTINATIONS:
        try:
            entity = await client.get_entity(name)
            since = REPOST_SINCE if name == DESTINATION else NEW_DESTINATIONS_SINCE
            destinations.append((name, entity, since))
        except Exception:
            logging.exception("Cannot access destination %s", name)
    if not destinations:
        raise RuntimeError("No reachable destinations")
    me = await client.get_me()
    for name, entity, _ in destinations:
        try:
            permissions = await client.get_permissions(entity, me)
            broadcast = bool(getattr(entity, "broadcast", False))
            defaults = getattr(entity, "default_banned_rights", None)
            group_restricted = bool(getattr(defaults, "send_messages", False))
            can_post = (
                not permissions.has_left and not permissions.is_banned
                and (permissions.post_messages if broadcast
                     else permissions.is_admin or not group_restricted)
            )
            logging.info(
                "Posting rights destination=%s type=%s allowed=%s admin=%s",
                name, "channel" if broadcast else "chat",
                can_post, permissions.is_admin,
            )
            if not can_post:
                logging.warning("Account cannot publish to %s with current rights", name)
        except Exception:
            logging.exception("Could not verify posting rights for %s", name)
    lock = asyncio.Lock()

    def delivered(ids, name):
        return any(connection.execute(
            "SELECT 1 FROM delivered_destinations WHERE source_id=? AND destination=?",
            (mid, name),
        ).fetchone() for mid in ids)

    def mark_delivered(ids, name):
        connection.executemany(
            "INSERT OR IGNORE INTO delivered_destinations VALUES (?, ?)",
            [(mid, name) for mid in ids],
        )
        connection.commit()

    async def publish(messages, name, destination):
        ids = [message.id for message in messages]
        async with lock:
            if delivered(ids, name):
                return
            caption = rewrite(next((m.raw_text for m in messages if m.raw_text), ""))
            media = [m.media for m in messages if m.media]
            if DRY_RUN:
                logging.info("PREVIEW destination=%s ids=%s media=%s text=%r",
                             name, ids, len(media), caption)
                return
            if media:
                await client.send_file(destination, media[0] if len(media) == 1 else media,
                                       caption=caption)
            elif caption:
                await client.send_message(destination, caption)
            else:
                return
            mark_delivered(ids, name)
            logging.info("Published source ids=%s destination=%s", ids, name)

    async def publish_all(messages):
        for name, destination, since in destinations:
            if all(m.date and m.date < since for m in messages):
                continue
            try:
                await publish(messages, name, destination)
            except Exception:
                logging.exception("Failed publishing source ids=%s destination=%s",
                                  [m.id for m in messages], name)

    @client.on(events.Album(chats=source))
    async def on_album(event):
        await publish_all(event.messages)

    @client.on(events.NewMessage(chats=source))
    async def on_message(event):
        if event.message.grouped_id:
            return  # Album handler sends grouped media in one publication.
        await publish_all([event.message])

    async def reconcile():
        """Recover posts missed during restarts or when live updates do not arrive."""
        while True:
            try:
                recent = await client.get_messages(source, limit=50)
                eligible = sorted(
                    (m for m in recent if m.date and m.date >=
                     min(since for _, _, since in destinations)),
                    key=lambda m: m.id,
                )
                groups = {}
                for message in eligible:
                    groups.setdefault(message.grouped_id or message.id, []).append(message)
                for name, destination, since in destinations:
                    try:
                        sent = await client.get_messages(destination, limit=100)
                        destination_texts = {m.raw_text for m in sent if m.raw_text}
                        for messages in sorted(groups.values(), key=lambda group: group[0].id):
                            if all(m.date < since for m in messages):
                                continue
                            ids = [m.id for m in messages]
                            if delivered(ids, name):
                                continue
                            caption = rewrite(next(
                                (m.raw_text for m in messages if m.raw_text), ""
                            ))
                            if caption in destination_texts:
                                mark_delivered(ids, name)
                                logging.info("Already in destination=%s: source ids=%s",
                                             name, ids)
                                continue
                            logging.info("Recovering source ids=%s destination=%s",
                                         ids, name)
                            await publish(messages, name, destination)
                            destination_texts.add(caption)
                    except Exception:
                        logging.exception("Failed checking destination %s", name)
                logging.info("Checked %d recent source messages, %d destinations",
                             len(eligible), len(destinations))
            except Exception:
                logging.exception("Failed to reconcile source; retrying in 60 seconds")
            await asyncio.sleep(60)

    logging.info("Listening to @%s -> %s; dry_run=%s", SOURCE,
                 ", ".join(name for name, _, _ in destinations), DRY_RUN)
    task = asyncio.create_task(reconcile())
    try:
        await client.run_until_disconnected()
    finally:
        task.cancel()
        connection.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    asyncio.run(main())
