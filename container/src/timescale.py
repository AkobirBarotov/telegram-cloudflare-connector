import env
import psycopg2
import logging
import json
from typing import List, Dict
from psycopg2.extras import execute_values


class TimescaleClient:
    def __init__(self, url: str):
        self.connection_url = url
        self.connection = None
        self._connect()

    def _connect(self):
        try:
            self.connection = psycopg2.connect(self.connection_url)
            self.connection.autocommit = True
        except Exception as e:
            logging.error(f"Unable to connect to TimescaleDB: {e}")
            raise

    def insert_messages_batch(self, messages: List[Dict]):
        sql_insert_unique_messages = """
        INSERT INTO unique_messages (content, embedding)
        VALUES %s
        ON CONFLICT (content) DO NOTHING;
        """

        sql_fetch_message_ids = """
        SELECT content, id FROM unique_messages
        WHERE content IN %s;
        """

        sql_insert_message_feed = """
        INSERT INTO message_feed (
            timestamp, platform_name, platform_user_id, platform_user_name,
            platform_message_id, platform_message_url, source_account_id, source_channel_name,
            source_channel_id, platform_specific, message_id
        )
        VALUES %s
        ON CONFLICT (timestamp, platform_name, platform_message_id) DO NOTHING;
        """

        with self.connection.cursor() as cursor:
            try:
                unique_message_values = [
                    (msg["message"]["text"], None) for msg in messages
                ]

                # Insert unique messages
                execute_values(cursor, sql_insert_unique_messages, unique_message_values)

                # Fetch message IDs for unique messages
                unique_message_contents = tuple(
                    [msg["message"]["text"] for msg in messages]
                )
                cursor.execute(sql_fetch_message_ids, (unique_message_contents,))
                unique_message_map = dict(cursor.fetchall())

                message_feed_values = []
                failed_rows = [] # List to store any rows that fail

                for msg in messages:
                    try:
                        message_text = msg["message"]["text"]
                        unique_message_id = unique_message_map[message_text]

                        message_feed_data = (
                            msg["timestamp"],
                            msg["source"]["platform"],
                            msg["user"]["id"],
                            msg["user"]["name"],
                            msg["message"]["id"],
                            msg["message"].get("url", None),
                            msg["source"].get("account_id"),
                            msg["source"]["channel"].get("name", None),
                            msg["source"]["channel"].get("id", None),
                            json.dumps(msg.get("platform_specific", {})),
                            unique_message_id,
                        )
                        message_feed_values.append(message_feed_data)

                    except Exception as row_error:
                        failed_rows.append((msg, str(row_error)))
                        logging.error(
                            f"Failed to process row for message {msg['message']['id']}: {row_error}"
                        )

                if message_feed_values:
                    execute_values(cursor, sql_insert_message_feed, message_feed_values)

                self.connection.commit()
                logging.info("Batch inserted unique messages and message feed.")

                if failed_rows:
                    logging.warning(
                        f"Failed to process {len(failed_rows)} rows. Details: {failed_rows}"
                    )

            except Exception as e:
                self.connection.rollback()
                logging.error(f"Failed to batch insert messages: {e}")
                
            finally:
                self.close()

    def close(self):
        if self.connection:
            self.connection.close()


def get_timescale_client():
    timescale_connection_url = env.TIMESCALE_CONNECTION
    return TimescaleClient(timescale_connection_url)
