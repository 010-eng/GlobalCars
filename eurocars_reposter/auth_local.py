"""Run only on your computer; paste the result into Railway's TG_SESSION secret."""
import asyncio
import getpass
import os
from telethon import TelegramClient
from telethon.sessions import StringSession


async def main():
    api_id = os.getenv("TG_API_ID") or input("Telegram api_id: ").strip()
    api_hash = os.getenv("TG_API_HASH") or getpass.getpass("Telegram api_hash: ").strip()
    async with TelegramClient(StringSession(), int(api_id), api_hash) as client:
        print("\nCopy this session only into Railway variable TG_SESSION. Keep it private:\n")
        print(client.session.save())


if __name__ == "__main__":
    asyncio.run(main())
