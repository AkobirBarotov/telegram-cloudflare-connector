import logging
from http import HTTPStatus

from connector import TelegramConnector
from telegram import get_telegram_client
from flask import Flask, request, jsonify

logging.getLogger().setLevel(logging.INFO)

app = Flask(__name__)

@app.route("/")
def run_connector():
    data = request.get_json()
    lastMessageIds = data.get("lastMessageIds")

    if not lastMessageIds:
        return jsonify({"error": "Missing required parameters"}), HTTPStatus.BAD_REQUEST

    telegram = get_telegram_client()

    try:
        connector = TelegramConnector(telegram, lastMessageIds)
        connector.start()
    except Exception as e:
        logging.error(e)
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

    return jsonify({"status": "ok"}), HTTPStatus.OK

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
