import logging
import asyncio
from http import HTTPStatus
from flask import Flask, jsonify

# Local imports
from connector import TelegramConnector
from telegram import get_telegram_client
from timescale import get_timescale_client

logging.getLogger().setLevel(logging.INFO)
# Configure logging - for better visibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables (to cache clients and reuse them)
telegram_client = None
timescale_client = None

def get_clients():
    """Initializes clients only when needed (Lazy Loading)"""
    global telegram_client, timescale_client
    if not telegram_client:
        telegram_client = get_telegram_client()
        logger.info("Telegram Client initialized")
    if not timescale_client:
        timescale_client = get_timescale_client()
        logger.info("Timescale Client initialized")
    return telegram_client, timescale_client

async def run_sync_logic():
    """Async function performing the main logic"""
    tg, ts = get_clients()

    # Check Telegram connection (reconnect if disconnected)
    if not tg.is_connected():
        await tg.connect()
        logger.info("Connected to Telegram")

    # Initialize the connector
    connector = TelegramConnector(ts, tg)
    logger.info("Starting TelegramConnector sync...")

    # Works whether Connector.start() is async or synchronous
    if asyncio.iscoroutinefunction(connector.start):
        await connector.start()
    else:
        connector.start()

    logger.info("Sync finished successfully")
    return {"status": "success", "message": "All messages synced"}

@app.route("/")
def run_connector():
    """Endpoint triggered by Cloudflare Worker"""
    logger.info("Trigger received from Cloudflare Worker")

    try:
        # Flask is synchronous, but the Telegram library is Async.
        # Therefore, we create a new "Loop" to run the async code there.
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
    # Local port for testing
    app.run(host="0.0.0.0", port=8080)
