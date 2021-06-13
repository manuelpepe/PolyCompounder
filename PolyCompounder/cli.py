"""
Pool Auto Compounder for the Polygon (MATIC) network.
Currently works for PZAP only.
"""
import os
import sys
import time
import inspect
import getpass
import logging
import subprocess

from pathlib import Path
from contextlib import contextmanager
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from PolyCompounder.blockchain import Blockchain
from PolyCompounder.core import Compounder
from PolyCompounder.config import ENDPOINT, MY_ADDRESS, DATETIME_FORMAT, CONFIG_FILE, SAMPLE_CONFIG_FILE, KEY_FILE
from PolyCompounder.utils import create_keyfile, KeyfileOverrideException
from PolyCompounder.alert import alert_exception
from PolyCompounder.queue import QueueLoader


def _create_logger():
    fhandler = logging.FileHandler("polycompound.log", "a", "utf-8")
    fhandler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s - %(message)s", datefmt=DATETIME_FORMAT))

    shandler = logging.StreamHandler(sys.stdout)
    shandler.setFormatter(logging.Formatter("%(message)s"))

    logger = logging.getLogger()
    logger.addHandler(shandler)
    logger.addHandler(fhandler)
    logger.setLevel(logging.INFO)
    return logger


def _create_keyfile(args, logger):
    private_key = getpass.getpass("Enter private key: ")
    password = getpass.getpass("Enter keyfile password: ")
    pass_repeat = getpass.getpass("Repeat keyfile password: ")
    if password != pass_repeat:
        logger.error("Passwords don't match")
        sys.exit(1)
    try:
        out = Path(args.output)
        create_keyfile(out, private_key, pass_repeat)
    except KeyfileOverrideException as err:
        logger.error(err)
        sys.exit(1)
    logger.info(f"Keyfile written to '{out}'")


def edit_config(args, logger):
    data = None
    if not CONFIG_FILE.is_file():
        with CONFIG_FILE.open("w") as fp:
            data = SAMPLE_CONFIG_FILE.open("r").read()
            fp.write(data)
    editor = os.environ.get("EDITOR", "vim")
    subprocess.call([editor, CONFIG_FILE])


def print_strats(args, logger):
    NOSHOW = ["blockchain", "name"]
    logger.info("Available strategies:")
    for strat in QueueLoader.list_strats():
        logger.info(f"* {strat.__name__}{':' if args.verbose else ''}")
        if args.verbose:
            params = inspect.signature(strat).parameters
            for name, param in params.items():
                if name in NOSHOW:
                    continue
                logger.info(f"\t- {param}")
    if not args.verbose:
        logger.info("use -v to see strategy parameters")


def run(args, logger):
    blockchain = Blockchain(ENDPOINT, 137, "POLYGON")
    blockchain.load_wallet(MY_ADDRESS, args.keyfile)
    queue = QueueLoader(blockchain).load()
    pounder = Compounder(queue)
    pounder.start()


def parser():
    p = ArgumentParser("PolyCompounder", description=__doc__, formatter_class=RawDescriptionHelpFormatter)
    subparsers = p.add_subparsers(help="subcommands for compounder")

    p_create = subparsers.add_parser("list-strategies", help="List strategies and parameters")
    p_create.add_argument("-v", "--verbose", action="store_true", help="Print strategy parameters")
    p_create.set_defaults(func=print_strats)

    p_run = subparsers.add_parser("run", help="Run compounding process")
    p_run.add_argument("-k", "--keyfile", action="store", help="Wallet Encrypted Private Key. If not used will load from resources/key.file as default.", default=None)
    p_run.set_defaults(func=run)

    p_createkf = subparsers.add_parser("create-keyfile", help="Create keyfile for compounder. You'll need your private key and a new password for the keyfile.")
    p_createkf.add_argument("-o", "--output", action="store", help="Output location for keyfile.", default=str(KEY_FILE))
    p_createkf.set_defaults(func=_create_keyfile)

    p_edit = subparsers.add_parser("edit-config", help="Create or edit config file.")
    p_edit.set_defaults(func=edit_config)
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


def exception_handler(logger):
    def _handle_exceptions(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        alert_exception(exc_value)
    return _handle_exceptions


def main():
    logger = _create_logger()
    args = parser().parse_args()
    sys.excepthook = exception_handler(logger)
    if hasattr(args, 'func'):
        with _catch_ctrlc():
            args.func(args, logger)
    else:
        parser().print_help()


if __name__ == "__main__":
    main()
