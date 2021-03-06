from telethon import TelegramClient
from telethon.tl.types import PeerChannel
import local
import re
from db import Database


class Paratica:

    add_notification = ("INSERT INTO paratica_notification (id, token, code, state, enter_price, stop_loss, take_profit_1, take_profit_2, take_profit_3, message, date) "
                        "VALUES (%(notification_id)s, %(notification_token)s, %(notification_code)s, %(notification_state)s, %(notification_enter_price)s, %(notification_stop_loss)s, "
                        "%(notification_take_profit_1)s, %(notification_take_profit_2)s, %(notification_take_profit_3)s, "
                        "%(notification_message)s, %(notification_date)s)")
    stop_notification = ("UPDATE paratica_notification SET "
                         "id = %(notification_id)s, "
                         "state = %(notification_state)s, "
                         "status = 0, "
                         "stop_rate = %(stop_rate)s "
                         "WHERE code = %(notification_code)s AND state NOT IN('exit', 'stop_loss')")
    exit_notification = ("UPDATE paratica_notification SET "
                         "id = %(notification_id)s, "
                         "state = %(notification_state)s, "
                         "status = 0, "
                         "stop_loss = %(current_price)s, "
                         "exit_rate = %(exit_rate)s "
                         "WHERE code = %(notification_code)s AND state NOT IN('exit', 'stop_loss')")
    profit_1_notification = ("UPDATE paratica_notification SET "
                             "id = %(notification_id)s, "
                             "state = %(notification_state)s, "
                             "status = 0, "
                             "stop_loss = %(notification_stop_loss)s, "
                             "profit_1_rate = %(profit_1_rate)s "
                             "WHERE code = %(notification_code)s AND (profit_1_rate = 0 OR stop_loss != %(notification_stop_loss)s) AND state NOT IN('exit', 'stop_loss')")
    profit_2_notification = ("UPDATE paratica_notification SET "
                             "id = %(notification_id)s, "
                             "state = %(notification_state)s, "
                             "status = 0, "
                             "stop_loss = %(notification_stop_loss)s, "
                             "profit_2_rate = %(profit_2_rate)s "
                             "WHERE code = %(notification_code)s AND (profit_2_rate = 0 OR stop_loss != %(notification_stop_loss)s) AND state NOT IN('exit', 'stop_loss')")
    profit_3_notification = ("UPDATE paratica_notification SET "
                             "id = %(notification_id)s, "
                             "state = %(notification_state)s, "
                             "status = 0, "
                             "stop_loss = %(notification_stop_loss)s, "
                             "profit_3_rate = %(profit_3_rate)s "
                             "WHERE code = %(notification_code)s AND (profit_3_rate = 0 OR stop_loss != %(notification_stop_loss)s) AND state NOT IN('exit', 'stop_loss')")
    regex = r'[^a-zA-Z0-9.()%/#]+'

    def extractValue(self, text, reg, group):
        try:
            return re.search(reg, text).group(group)
        except AttributeError:
            return ''

    def contains(self, arr, param, value):
        for key in arr:
            if param in key and value in key[param]:
                return True
        return False

    def getValue(self, arr, param, value):
        for key in arr:
            if param in key and value in key[param]:
                return key
        return None

    def run(self):
        database = Database()
        client = TelegramClient('session_name', local.api_id, local.api_hash)
        client.start()

        cursor = database.query("select max(id) as mx from paratica_notification")
        last_db_id = cursor.fetchone()[0]

        # paratica channel listener
        channel = PeerChannel(channel_id=1317438882)
        messages = client.get_messages(channel, min_id=last_db_id, limit=10000)

        messages.reverse()
        for m in messages:
            if m.message is not None and m.message != '' and 'MA-' not in m.message:
                parity = self.extractValue(m.message, 'Signal Parity( +):( +)#(.*)?\n', 3)
                code = self.extractValue(m.message, 'Signal Code( +):( +)#(.*)?\n', 3)
                enter_price = self.extractValue(m.message, 'Enter Price( +):( +)(.*)\n', 3)
                if code is '' or not parity.endswith('BTC'):
                    continue
                if 'new trading signal' in m.message.lower():
                    stop_loss = self.extractValue(m.message, 'Stop Loss( +):( +)(.*)\n', 3)
                    profit_1 = self.extractValue(m.message, 'Take Profit-1( +):( +)(.*)\n', 3)
                    profit_2 = self.extractValue(m.message, 'Take Profit-2( +):( +)(.*)\n', 3)
                    profit_3 = self.extractValue(m.message, 'Take Profit-3( +):( +)(.*)\n', 3)
                    interval = self.extractValue(m.message, 'Chart Interval( +):( +)#(.*)\n', 3)
                    if not(interval == '15MINS' or code in 'B16PU B16U0'):
                        continue
                    m.message = re.sub(self.regex, ' ', m.message)
                    notification = {
                        'notification_id' : m.id,
                        'notification_token': parity,
                        'notification_code': code,
                        'notification_state': 'enter',
                        'notification_enter_price': enter_price,
                        'notification_stop_loss' : stop_loss,
                        'notification_take_profit_1' : profit_1,
                        'notification_take_profit_2' : profit_2,
                        'notification_take_profit_3' : profit_3,
                        'notification_message' : m.message.encode('utf8'),
                        'notification_date' : m.date,
                        'interval': interval
                    }
                    database.execute(self.add_notification, notification)
                elif 'stop loss alert' in m.message.lower():
                    loss_rate = self.extractValue(m.message, 'Loss Rate( +):( +)(.*)( +)\n', 3).replace(' %', '')
                    notification ={
                        'notification_id' : m.id,
                        'notification_code' : code,
                        'notification_state' : 'stop_loss',
                        'stop_rate' : loss_rate
                    }
                    database.execute(self.stop_notification, notification)
                elif 'exit position' in m.message.lower():
                    profit_rate = self.extractValue(m.message, 'Profit Rate( +):( +)(.*)( +)\n', 3).replace(' %', '')
                    current_price = self.extractValue(m.message, 'Current Price( +):( +)(.*)\n', 3)
                    notification ={
                        'notification_id' : m.id,
                        'notification_code' : code,
                        'notification_state' : 'exit',
                        'exit_rate' : profit_rate,
                        'current_price' : current_price
                    }
                    database.execute(self.exit_notification, notification)
                elif 'profit alert' in m.message.lower():
                    if 'take profit-3' not in m.message.lower():
                        profit_rate = self.extractValue(m.message, 'Profit Rate( +):( +)(.*)( +)\n', 3).replace(' %', '')
                        stop_loss = self.extractValue(m.message, 'Stop Loss( +):( +)(.*)\n', 3)
                        notification ={
                            'notification_id' : m.id,
                            'notification_code' : code,
                            'notification_state' : 'profit_3',
                            'notification_stop_loss' : stop_loss,
                            'profit_3_rate' : profit_rate
                        }
                        database.execute(self.profit_3_notification, notification)
                    elif 'take profit-2' not in m.message.lower():
                        profit_rate = self.extractValue(m.message, 'Profit Rate( +):( +)(.*)( +)\n', 3).replace(' %', '')
                        stop_loss = self.extractValue(m.message, 'Stop Loss( +):( +)(.*)\n', 3)
                        notification ={
                            'notification_id' : m.id,
                            'notification_code' : code,
                            'notification_state' : 'profit_2',
                            'notification_stop_loss' : stop_loss,
                            'profit_2_rate' : profit_rate
                        }
                        database.execute(self.profit_2_notification, notification)
                    elif 'take profit-1' not in m.message.lower():
                        profit_rate = self.extractValue(m.message, 'Profit Rate( +):( +)(.*)( +)\n', 3).replace(' %', '')
                        stop_loss = self.extractValue(m.message, 'Stop Loss( +):( +)(.*)\n', 3)
                        notification ={
                            'notification_id' : m.id,
                            'notification_code' : code,
                            'notification_state' : 'profit_1',
                            'notification_stop_loss' : stop_loss,
                            'profit_1_rate' : profit_rate
                        }
                        database.execute(self.profit_1_notification, notification)

        database.close()

if __name__ == "__main__":
    paratica = Paratica()
    paratica.run()