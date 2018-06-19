from telethon import TelegramClient
from telethon.tl.types import PeerChannel
import local
import requests
from bs4 import BeautifulSoup

class BinanceListing:

    def run(self):
        # send messages related binance listing
        client = TelegramClient('session_name', local.api_id, local.api_hash)
        client.start()
        channel = PeerChannel(channel_id=1347367599)

        last_message = client.get_messages(channel, limit=1)[0]

        resp = requests.get(local.listing_page)

        soup = BeautifulSoup(resp.text, "html.parser")
        links = soup.find_all('li', class_='article-list-item')

        my_list = list()
        for link in links:
            if last_message.message != link.text.strip():
                my_list.append(link.text.strip())
            else:
                break
        my_list.reverse()
        for l in my_list:
            client.send_message(channel, l)

if __name__ == "__main__":
    binance = BinanceListing()
    binance.run()