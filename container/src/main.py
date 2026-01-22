import logging
import asyncio
from http import HTTPStatus
from flask import Flask, jsonify

# Mahalliy modullar (Local imports)
from connector import TelegramConnector
from telegram import get_telegram_client
from timescale import get_timescale_client

# Loglarni sozlash - aniqroq ko'rinishi uchun
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global o'zgaruvchilar (Mijozlarni xotirada saqlab, qayta ishlatish uchun)
telegram_client = None
timescale_client = None

def get_clients():
    """Mijozlarni faqat kerak bo'lganda yaratadi (Lazy Loading)"""
    global telegram_client, timescale_client
    if not telegram_client:
        telegram_client = get_telegram_client()
        logger.info("Telegram Client initialized")
    if not timescale_client:
        timescale_client = get_timescale_client()
        logger.info("Timescale Client initialized")
    return telegram_client, timescale_client

async def run_sync_logic():
    """Asosiy ishni bajaruvchi Asinxron funksiya"""
    tg, ts = get_clients()
    
    # Telegramga ulanishni tekshiramiz (uzilib qolgan bo'lsa ulaymiz)
    if not tg.is_connected():
        await tg.connect()
        logger.info("Connected to Telegram")
    
    # Ulagichni ishga tushiramiz
    connector = TelegramConnector(ts, tg)
    logger.info("Starting TelegramConnector sync...")
    
    # Connector.start() funksiyasi async bo'lsa ham, oddiy bo'lsa ham ishlayveradi
    if asyncio.iscoroutinefunction(connector.start):
        await connector.start()
    else:
        connector.start()
        
    logger.info("Sync finished successfully")
    return {"status": "success", "message": "All messages synced"}

@app.route("/")
def run_connector():
    """Cloudflare Worker murojaat qiladigan endpoint"""
    logger.info("Trigger received from Cloudflare Worker")

    try:
        # Flask sinxron (ketma-ket) ishlaydi, lekin Telegram kutubxonasi Asinxron.
        # Shuning uchun biz yangi "Loop" ochib, async kodni o'sha yerda aylantiramiz.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(run_sync_logic())
        loop.close()

        return jsonify(result), HTTPStatus.OK

    except Exception as e:
        logger.error(f"CRITICAL ERROR: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

if __name__ == "__main__":
    # Test uchun local port
    app.run(host="0.0.0.0", port=8080)