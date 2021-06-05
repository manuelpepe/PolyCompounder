"""
Pool Auto Compounder for the Polygon (MATIC) network.
Currently works for PZAP only.
"""
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from task import PZAPCompoundTask
from core import Compounder, load_wallet, get_w3_connection
from config import ENDPOINT, MY_ADDRESS
from contract import ContractManager
from config import ENDPOINT, MY_ADDRESS, RESOURCES

POOL_ID = 11


def parser():
    p = ArgumentParser("PolyCompounder", description=__doc__, formatter_class=RawDescriptionHelpFormatter)
    p.add_argument("-k", "--keyfile", action="store", help="Wallet Encrypted Private Key. If not used will load from resources/key.file as default.", default=None)
    return p


def main():
    args = parser().parse_args()
    w3 = get_w3_connection(ENDPOINT)
    wallet = load_wallet(w3, args.keyfile)
    manager = ContractManager(w3, RESOURCES)
    pair = PZAPCompoundTask(w3, manager, MY_ADDRESS, POOL_ID, wallet)
    pounder = Compounder(manager, [pair])
    pounder.run()


if __name__ == "__main__":
    main()