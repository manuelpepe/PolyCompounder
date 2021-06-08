"""
Pool Auto Compounder for the Polygon (MATIC) network.
Currently works for PZAP only.
"""
import time, sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from strategy import StrategyLoader
from blockchain import Blockchain
from core import Compounder
from config import ENDPOINT, MY_ADDRESS, RESOURCES

POOL_ID = 11


def parser():
    p = ArgumentParser("PolyCompounder", description=__doc__, formatter_class=RawDescriptionHelpFormatter)
    p.add_argument("-k", "--keyfile", action="store", help="Wallet Encrypted Private Key. If not used will load from resources/key.file as default.", default=None)
    return p


def main():
    args = parser().parse_args()
    blockchain = Blockchain(ENDPOINT, 137, "POLYGON")
    blockchain.load_wallet(MY_ADDRESS, args.keyfile)
    stratloader = StrategyLoader(blockchain)
    starts = stratloader.load_from_file(RESOURCES / "strategies.json")
    pounder = Compounder(starts)
    while True:
        pounder.run()
        print()
        sys.stdout.flush()
        time.sleep(60*10)


if __name__ == "__main__":
    main()