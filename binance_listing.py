from telethon import TelegramClient
from telethon.tl.types import PeerChannel
import local
import requests
from bs4 import BeautifulSoup
from db import Database


class BinanceListing:
    database = Database()

    def get_last_message(self, filename):
        param = {
            'name': filename,
        }
        query = "SELECT value FROM properties WHERE name = %(name)s"
        cursor = self.database.query(query, param)
        return cursor.fetchone()[0]

    def write_message(self, filename, message):
        param = {
            'value': message,
            'name': filename,
        }
        query = "UPDATE properties SET value = %(value)s WHERE name =  %(name)s"
        self.database.execute(query, param)

    def run(self, client):
        channel = PeerChannel(channel_id=1347367599)

        resp = requests.get(local.listing_page)

        soup = BeautifulSoup(resp.text, "html.parser")
        sections = soup.select('ul.article-list')
        files = ["listing", "announce"]

        for (i, section) in enumerate(sections):
            my_list = list()
            for item in section.select('li.article-list-item a'):
                if self.get_last_message(files[i]) != item.text.strip():
                    _message = item.text.strip()
                    if item.has_attr('href'):
                        _message = '<a href="{}">{}</a>'.format(item['href'], _message)
                    my_list.append(_message)
                else:
                    break
            my_list.reverse()
            for k in my_list:
                client.send_message(channel, k)
            if len(my_list) > 0:
                self.write_message(files[i], my_list[len(my_list) - 1])


if __name__ == "__main__":
    # send messages related binance listing
    _client = TelegramClient('session_name', local.api_id, local.api_hash)
    _client.start()
    binance = BinanceListing()
    binance.run(_client)
