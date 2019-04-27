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

        cursor = database.query("select id, order_id, action, currency, enter_price, exit_price from orders_new_log where id > " + str(last_id))
        for row in cursor:
            if row[2] == 'I':
                client.send_message(channel, str(row[0]) + ":" + str(row[1]) + " " + row[3] + " enter at " + str(row[4]))

            if row[2] == 'U':
                client.send_message(channel, str(row[0]) + ":" + str(row[1]) + " " + row[3] + " close at " + str(row[5]) + " profit " + str((row[5] - row[4]) / row[4] * 100))

if __name__ == "__main__":
    superTrend = SuperTrend()
    superTrend.run()