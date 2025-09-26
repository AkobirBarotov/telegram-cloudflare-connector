import env

from telethon import TelegramClient
from telethon.sessions import StringSession


def get_telegram_client():
    string_session = StringSession(env.TELEGRAM_SESSION_STR)
    return TelegramClient(
        session=string_session, api_id=int(env.TELEGRAM_API_ID), api_hash=env.TELEGRAM_API_HASH
    )
