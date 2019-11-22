from telethon.sync import TelegramClient
from multiprocessing import Process
from binance_listing import BinanceListing
from supertrend import SuperTrend
import local


def run_in_parallel(*fns):
    proc = []
    for fn in fns:
        p = Process(target=fn)
        p.start()
        proc.append(p)
    for p in proc:
        p.join()


binance = BinanceListing()
supertrend = SuperTrend()

# send messages related binance listing
client = TelegramClient('session_name', local.api_id, local.api_hash)
client.start()

if __name__ == "__main__":
    run_in_parallel(binance.run(client), supertrend.run(client))
