from telethon import TelegramClient

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.
from telethon.tl.types import PeerChannel
import local
from db import Database

last_id = 14655-500

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

last_id = 0
for mx in cursor:
    last_id = mx[0]

channel = PeerChannel(channel_id=1131948783)

while True:
    messages = client.get_messages(channel, min_id= last_id, limit=10)
    if len(messages) == 0:
        break
    for m in messages:
        if m.id > last_id:
            last_id = m.id
        notification = {
            'notification_id' : m.id,
            'notification_message' : m.message,
            'notification_date' : m.date
        }
        database.insert(add_notification, notification)

database.close()