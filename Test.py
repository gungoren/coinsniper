from telethon import TelegramClient
from telethon.tl.types import PeerChannel
import local
import re
from db import Database
import requests
from bs4 import BeautifulSoup

database = Database()
client = TelegramClient('session_name', local.api_id, local.api_hash)
client.start()

"""
dialogs = client.get_dialogs()
for d in dialogs:
    if d.name == 'CoinSniper':
        messages = client.get_messages(d, min_id=last_id, limit=500)
        for m in messages:
            print("***************************")
            print(m.id)
            print(m.message)
            print(m)
"""

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
        database.insert(add_notification, notification)

database.close()

# send messages related binance listing
channel = PeerChannel(channel_id=1347367599)

last_message = client.get_messages(channel, limit=1)[0]

resp = requests.get(local.listing_page)

soup = BeautifulSoup(resp.text, "html5lib")
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