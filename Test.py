from multiprocessing import Process
from binance_listing import BinanceListing
from supertrend import SuperTrend

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

if __name__ == "__main__":
    run_in_parallel(binance.run, supertrend.run)