"""
Pool Auto Compounder for the Polygon (MATIC) network.
Currently works for PZAP only.
"""
import sys
import time
import inspect
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from strategy import StrategyLoader
from blockchain import Blockchain
from core import Compounder
from config import ENDPOINT, MY_ADDRESS, RESOURCES


def print_strats(args):
    NOSHOW = ["blockchain", "name"]
    print("Available strategies:")
    for strat in StrategyLoader.list_strats():
        print(f"* {strat.__name__}{':' if args.verbose else ''}")
        if args.verbose:
            params = inspect.signature(StrategyLoader.list_strats()[0]).parameters
            for name, param in params.items():
                if name in NOSHOW:
                    continue
                print(f"\t- {param}")
    if not args.verbose:
        print("use -v to see strategy parameters")
                

def run(args):
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


def parser():
    p = ArgumentParser("PolyCompounder", description=__doc__, formatter_class=RawDescriptionHelpFormatter)
    subparsers = p.add_subparsers(help="subcommands for compounder")

    p_create = subparsers.add_parser("list-strategies")
    p_create.add_argument("-v", "--verbose", action="store_true", help="Print strategy parameters")
    p_create.set_defaults(func=print_strats)

    p_run = subparsers.add_parser("run")
    p_run.add_argument("-k", "--keyfile", action="store", help="Wallet Encrypted Private Key. If not used will load from resources/key.file as default.", default=None)
    p_run.set_defaults(func=run)
    return p


def main():
    args = parser().parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser().print_help()


if __name__ == "__main__":
    main()