"""Run only on your computer; paste the result into Railway's TG_SESSION secret."""
import asyncio
import getpass
import os
import platform
import subprocess
from telethon import TelegramClient
from telethon.sessions import StringSession


async def main():
    api_id = os.getenv("TG_API_ID") or input("Telegram api_id: ").strip()
    api_hash = os.getenv("TG_API_HASH") or getpass.getpass("Telegram api_hash: ").strip()
    async with TelegramClient(StringSession(), int(api_id), api_hash) as client:
        session = client.session.save()
        if platform.system() == "Darwin":
            subprocess.run(["pbcopy"], input=session, text=True, check=True)
            print("Session copied to clipboard. Paste into Railway variable TG_SESSION; do not paste into chat.")
        else:
            print("\nCopy this session only into Railway variable TG_SESSION. Keep it private:\n")
            print(session)


if __name__ == "__main__":
    asyncio.run(main())
