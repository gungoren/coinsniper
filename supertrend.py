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
        channel = PeerChannel(channel_id=1482575365)[0]

        last_message = client.get_messages(channel, limit=1)

        last_id = last_message.message.split(':')[0]

        cursor = database.query("select id, currency, enter_price from orders_new where id > " + str(last_id))
        for row in cursor:
            client.send_message(channel, row[0] + ":" + row[1] + " enter at " + row[2])


if __name__ == "__main__":
    superTrend = SuperTrend()
    superTrend.run()