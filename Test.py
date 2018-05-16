from telethon import TelegramClient

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.
from telethon.tl.types import PeerChannel
import re
import local

last_id = 14655-500

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
channel = PeerChannel(1131948783)
messages = client.get_messages(channel, min_id= last_id, limit=10)
for m in messages:
    token_reg = re.search('#(.+?) ➡', m.message)
    reg = re.search('Vol: (.+?) BTC', m.message)
    if reg and token_reg:
        volume = reg.group(1)
        token = token_reg.group(1)
        if float(volume) > 100:
            print("***************************")
            print(volume + " " + token)