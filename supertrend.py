from telethon import TelegramClient
from telethon.tl.types import PeerChannel
import local
import time
from db import Database


class SuperTrend:

    def run(self, client):
        database = Database()
        channel = PeerChannel(channel_id=1482575365)

        last_message = client.get_messages(channel, limit=1)[0]

        last_id = last_message.message.split(':')[0]

        cursor = database.query("select id, order_id, action, currency, enter_price, exit_price, enter_time, exit_time from orders_new_log where id > %s" % last_id)
        for row in cursor:
            if row[2] == 'I' and row[4] > 0:
                t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[6]))
                message = "%d:%d %s enter at %.6f %s" % (row[0], row[1], row[3], row[4], t)
                client.send_message(channel, message)

            if row[2] == 'U' and not row[7] is None:
                t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(row[7]))
                message = "%d:%d %s close at %.6f profit %.2f%% %s" % (row[0], row[1], row[3], row[5], ((row[5] - row[4]) / row[4] * 100), t)
                client.send_message(channel, message)

if __name__ == "__main__":
    _client = TelegramClient('session_name', local.api_id, local.api_hash)
    _client.start()
    superTrend = SuperTrend()
    superTrend.run(_client)