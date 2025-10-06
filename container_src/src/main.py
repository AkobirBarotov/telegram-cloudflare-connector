import logging
from http import HTTPStatus

from connector import TelegramConnector
from telegram import get_telegram_client
from timescale import get_timescale_client
from flask import Flask, request, jsonify

logging.getLogger().setLevel(logging.INFO)

app = Flask(__name__)

telegram = get_telegram_client()
timescale = get_timescale_client()

@app.route("/")
def run_connector():
    logging.info("Container initialized")

    try:
        connector = TelegramConnector(timescale, telegram)
        logging.info("TelegramConnector instance created")
        connector.start()
        return jsonify({"status": "Connector finished"}), HTTPStatus.OK
    except Exception as e:
        logging.error(f"Error in run_connector: {e}")
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
