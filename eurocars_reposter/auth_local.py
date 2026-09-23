"""Run only on your computer; paste the result into Railway's TG_SESSION secret."""
import asyncio
import os
from telethon import TelegramClient
from telethon.sessions import StringSession


async def main():
    async with TelegramClient(StringSession(), int(os.environ["TG_API_ID"]), os.environ["TG_API_HASH"]) as client:
        print("\nCopy this session only into Railway variable TG_SESSION. Keep it private:\n")
        print(client.session.save())


if __name__ == "__main__":
    asyncio.run(main())
