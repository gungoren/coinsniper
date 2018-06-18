from telethon import TelegramClient
from telethon.tl.types import PeerChannel
import local
from collections import defaultdict
import re
from decimal import Decimal

client = TelegramClient('session_name', local.api_id, local.api_hash)
client.start()

# send messages related binance listing
channel = PeerChannel(channel_id=1317438882)
messages = client.get_messages(channel, limit=10000)

def extractValue(text, reg, group):
    try:
        return re.search(reg, text).group(group)
    except AttributeError:
        return ''

def contains(arr, param, value):
    for key in arr:
        if param in key and value in key[param]:
            return True
    return False

dd = defaultdict(list)
messages.reverse()
for m in messages:
    if m.message is not None and m.message != '' and 'MA-' not in m.message:
        parity = extractValue(m.message, 'Signal Parity( +):( +)#(.*)?\n', 3)
        code = extractValue(m.message, 'Signal Code( +):( +)#(.*)?\n', 3)
        enter_price = extractValue(m.message, 'Enter Price( +):( +)(.*)\n', 3)
        if code is '':
            continue
        if 'new trading signal' in m.message.lower():
            stop_loss = extractValue(m.message, 'Stop Loss( +):( +)(.*)\n', 3)
            profit_1 = extractValue(m.message, 'Take Profit-1( +):( +)(.*)\n', 3)
            profit_2 = extractValue(m.message, 'Take Profit-2( +):( +)(.*)\n', 3)
            profit_3 = extractValue(m.message, 'Take Profit-3( +):( +)(.*)\n', 3)
            dd[code].append({
                'token': parity,
                'code': code,
                'action' : 'enter',
                'enter_price': enter_price,
                'stop_loss' : stop_loss,
                'profit_1' : profit_1,
                'profit_2' : profit_2,
                'profit_3' : profit_3
            })
        elif 'stop loss alert' in m.message.lower():
            loss_rate = extractValue(m.message, 'Loss Rate( +):( +)(.*)( +)\n', 3).replace(' %', '')
            dd[code].append({
                'token' : parity,
                'code' : code,
                'action' : 'stop_loss',
                'profit_rate' : loss_rate
            })
        elif 'exit position' in m.message.lower():
            profit_rate = extractValue(m.message, 'Profit Rate( +):( +)(.*)( +)\n', 3).replace(' %', '')
            dd[code].append({
                'token' : parity,
                'code' : code,
                'action' : 'exit',
                'profit_rate' : profit_rate
            })
        elif 'profit alert' in m.message.lower():
            if 'take profit-3' not in m.message.lower() and not contains(dd[code], 'profit', '3'):
                profit_rate = extractValue(m.message, 'Profit Rate( +):( +)(.*)( +)\n', 3).replace(' %', '')
                dd[code].append({
                    'token' : parity,
                    'code' : code,
                    'action' : 'profit_3',
                    'profit' : '3',
                    'sell_quantity' : Decimal(0.2),
                    'profit_rate' : profit_rate
                })
            elif 'take profit-2' not in m.message.lower() and not contains(dd[code], 'profit', '2'):
                profit_rate = extractValue(m.message, 'Profit Rate( +):( +)(.*)( +)\n', 3).replace(' %', '')
                dd[code].append({
                    'token' : parity,
                    'code' : code,
                    'action' : 'profit_2',
                    'profit' : '2',
                    'sell_quantity' : Decimal(0.3),
                    'profit_rate' : profit_rate
                })
            elif 'take profit-1' not in m.message.lower() and not contains(dd[code], 'profit', '1'):
                profit_rate = extractValue(m.message, 'Profit Rate( +):( +)(.*)( +)\n', 3).replace(' %', '')
                dd[code].append({
                    'token' : parity,
                    'code' : code,
                    'action' : 'profit_1',
                    'profit' : '1',
                    'sell_quantity' : Decimal(0.5),
                    'profit_rate' : profit_rate
                })
total = 1000
for key in dd:
    #dd[key].reverse()
    if (len(dd[key]) == 1 and dd[key][0]['action'] == 'enter') or not contains(dd[key], 'action', 'enter'):
        continue
    if not contains(dd[key], 'action', 'exit') and not contains(dd[key], 'action', 'stop_loss'):
        continue
    print(key + ' -> '+ ', '.join([x['action'] if 'enter' in x['action'] else ('{' + x['action'] + ' ' + x['profit_rate'] + '}') for x in dd[key]]))
    profit_r = 0
    remaining = 1
    for v in dd[key]:
        if 'enter' in v['action']:
            continue
        elif 'stop_loss' in v['action']:
            total += total * Decimal(v['profit_rate']) / 100
        elif 'profit_1' in v['action']:
            profit_r = v['sell_quantity'] * Decimal(v['profit_rate'])
            remaining -= v['sell_quantity']
        elif 'profit_2' in v['action']:
            profit_r += v['sell_quantity'] * Decimal(v['profit_rate'])
            remaining -= v['sell_quantity']
        elif 'profit_3' in v['action']:
            profit_r += v['sell_quantity'] * Decimal(v['profit_rate'])
            remaining -= v['sell_quantity']
        elif 'exit' in v['action']:
            profit_r += remaining * Decimal(v['profit_rate'])
            total += total * profit_r / 100
        print(str(total))
print(str(total) + ' -> ' + str(len(dd)))