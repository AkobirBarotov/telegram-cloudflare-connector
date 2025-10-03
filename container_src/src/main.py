import logging
from http import HTTPStatus

from connector import TelegramConnector
from telegram import get_telegram_client
from flask import Flask, request, jsonify

logging.getLogger().setLevel(logging.INFO)

app = Flask(__name__)

@app.route("/")
def run_connector():
    logging.info("Received request at '/' endpoint")
    lastMessageIds = request.args.get("lastMessageIds") or {}
    logging.debug(f"lastMessageIds received: {lastMessageIds}")

    telegram = get_telegram_client()
    logging.info("Telegram client initialized")

    try:
        connector = TelegramConnector(telegram, lastMessageIds)
        logging.info("TelegramConnector instance created")
        messages = connector.start()
        logging.info("Connector started and messages retrieved")
        return jsonify(messages), HTTPStatus.OK
    except Exception as e:
        logging.error(f"Error in run_connector: {e}")
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
