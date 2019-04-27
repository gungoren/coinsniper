from telethon import TelegramClient
from telethon.tl.types import PeerChannel
import local
import re
from db import Database


class SuperTrend:

    def run(self):
        database = Database()
        # send messages related super trend
        client = TelegramClient('session_name', local.api_id, local.api_hash)
        client.start()
        channel = PeerChannel(channel_id=1482575365)

        last_message = client.get_messages(channel, limit=1)[0]

        last_id = last_message.message.split(':')[0]

        cursor = database.query("select id, order_id, action, currency, enter_price, exit_price from orders_new_log where id > %s" % last_id)
        for row in cursor:
            if row[2] == 'I':
                message = "%d:%d %s enter at %d" % (row[0], row[1], row[3], row[4])
                client.send_message(channel, message)

            if row[2] == 'U':
                message = "%d:%d %s close at %d profit %.2f" % (row[0], row[1], row[3], row[4], ((row[5] - row[4]) / row[4] * 100))
                client.send_message(channel, message)

if __name__ == "__main__":
    superTrend = SuperTrend()
    superTrend.run()