from telethon import TelegramClient
from telethon.tl.types import PeerChannel
import local
import re
from db import Database


class CoinSniper:

    def run(self):
        database = Database()
        client = TelegramClient('session_name', local.api_id, local.api_hash)
        client.start()

        add_notification = ("INSERT INTO coin_notification (id, message, date) VALUES (%(notification_id)s, %(notification_message)s, %(notification_date)s)")

        cursor = database.query("select max(id) as mx from coin_notification")

        last_db_id = 0
        for mx in cursor:
            last_db_id = mx[0]

        regex = r'[^a-zA-Z0-9.()%/#]+'
        channel = PeerChannel(channel_id=1131948783)

        while True:
            messages = client.get_messages(channel, min_id=last_db_id, limit=1000)
            if len(messages) == 0:
                break

            for m in messages:
                m.message = re.sub(regex, ' ', m.message)
                notification = {
                    'notification_id' : m.id,
                    'notification_message' : m.message.encode('utf8'),
                    'notification_date' : m.date
                }
                database.execute(add_notification, notification)

        database.close()

if __name__ == "__main__":
    sniper = CoinSniper()
    sniper.run()