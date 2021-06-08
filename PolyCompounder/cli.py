"""
Pool Auto Compounder for the Polygon (MATIC) network.
Currently works for PZAP only.
"""
import os
import sys
import time
import inspect
import getpass

from pathlib import Path
from contextlib import contextmanager
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from PolyCompounder.strategy import StrategyLoader
from PolyCompounder.blockchain import Blockchain
from PolyCompounder.core import Compounder
from PolyCompounder.config import ENDPOINT, MY_ADDRESS, RESOURCES
from PolyCompounder.utils import create_keyfile, KeyfileOverrideException


def _create_keyfile(args):
    private_key = getpass.getpass("Enter private key: ")
    password = getpass.getpass("Enter keyfile password: ")
    pass_repeat = getpass.getpass("Repeat keyfile password: ")
    if password != pass_repeat:
        print("Passwords don't match")
        sys.exit(1)
    try:
        out = Path(args.output)
        create_keyfile(out, private_key, pass_repeat)
    except KeyfileOverrideException as err:
        print(err)
        sys.exit(1)
    print(f"Keyfile written to '{out}'")


def print_strats(args):
    NOSHOW = ["blockchain", "name"]
    print("Available strategies:")
    for strat in StrategyLoader.list_strats():
        print(f"* {strat.__name__}{':' if args.verbose else ''}")
        if args.verbose:
            params = inspect.signature(strat).parameters
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
    pounder.run()


def parser():
    p = ArgumentParser("PolyCompounder", description=__doc__, formatter_class=RawDescriptionHelpFormatter)
    subparsers = p.add_subparsers(help="subcommands for compounder")

    p_create = subparsers.add_parser("list-strategies", help="List strategies and parameters")
    p_create.add_argument("-v", "--verbose", action="store_true", help="Print strategy parameters")
    p_create.set_defaults(func=print_strats)

    p_run = subparsers.add_parser("run", help="Run compounding process")
    p_run.add_argument("-k", "--keyfile", action="store", help="Wallet Encrypted Private Key. If not used will load from resources/key.file as default.", default=None)
    p_run.set_defaults(func=run)

    p_run = subparsers.add_parser("create-keyfile", help="Create keyfile for compounder. You'll need your private key and a new password for the keyfile.")
    p_run.add_argument("-o", "--output", action="store", help="Output location for keyfile.", required=True)
    p_run.set_defaults(func=_create_keyfile)
    return p

@contextmanager
def _catch_ctrlc():
    try:
        yield
    except KeyboardInterrupt:
        print("Ctrl+C")
        try:
            sys.exit(1)
        except SystemExit:
            os._exit(1)

def main():
    args = parser().parse_args()
    if hasattr(args, 'func'):
        with _catch_ctrlc():
            args.func(args)
    else:
        parser().print_help()


if __name__ == "__main__":
    main()
