import asyncio
import nest_asyncio

from os import system, name
import getpass
import json

from telethon.sync import TelegramClient
from telethon.sessions import StringSession

nest_asyncio.apply()

api_id = getpass.getpass("Enter your api_id: ")
api_hash = getpass.getpass("Enter your api_hash: ")


def clear_screen():
    if name == "nt":
        _ = system("cls")
    else:
        _ = system("clear")


async def main():
    async with TelegramClient(StringSession(), api_id, api_hash) as client:
        clear_screen()

        session_str = client.session.save()

        account_details = {
            "api_id": int(api_id),
            "api_hash": api_hash,
            "session_str": session_str
        }

        json_str = json.dumps(account_details, indent=4)
        print("###### Add this to the Telegram account array: ######\n")
        print(json_str)


asyncio.run(main())
