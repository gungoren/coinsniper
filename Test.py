from multiprocessing import Process
from binance_listing import BinanceListing
from coinsniper import CoinSniper
from paratica import Paratica


def run_in_parallel(*fns):
    proc = []
    for fn in fns:
        p = Process(target=fn)
        p.start()
        proc.append(p)
    for p in proc:
        p.join()

binance = BinanceListing()
sniper = CoinSniper()
paratica = Paratica()

if __name__ == "__main__":
    run_in_parallel(binance.run, sniper.run, paratica.run)