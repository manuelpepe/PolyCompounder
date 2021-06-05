import json
import getpass

from pathlib import Path
from datetime import datetime, timedelta

from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from web3.contract import Contract

from utils import *


ENDPOINT = "https://rpc-mainnet.maticvigil.com/v1/APIKEY"
MY_ADDRESS = "0xADDRESS"

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

TOKENS = { 
    "PZAP": Web3.toChecksumAddress("0xeb2778f74e5ee038e67aa6c77f0f0451abd748fd"), 
    "WBTC": Web3.toChecksumAddress("0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6"),
}
SWAP_PATH = [ TOKENS["PZAP"], TOKENS["WBTC"] ]
STAKED_POOL_ID = 11

_PARENT = Path(__file__).parent
KEYFILE = _PARENT / "key.file"

CONTRACTS = {
    "PZAP": {
        "address": "0xeb2778f74e5ee038e67aa6c77f0f0451abd748fd",
        "abifile": "pzap.abi",
    },
    "WBTC": {
        "address": "0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6",
        "abifile": "wbtc.abi",
    },
    "MASTERCHEF": {
        "address": "0xB93C082bCfCCf5BAeA0E0f0c556668E25A41B896",
        "abifile": "masterchef.abi",
    },
    "ROUTER": {
        "address": "0x4aAEC1FA8247F85Dc3Df20F4e03FEAFdCB087Ae9",
        "abifile": "router.abi",
    },
    "PAIR": {
        "address": "0x9876157578B9F53A244632693B69938353915d5C",
        "abifile": "IPoliZapPair.abi"
    }
}


def read_contract(address: str, abifile: str):
    if not all((address, abifile)):
        raise ValueError("Need both address and abifile to read contract.")
    with open(_PARENT / abifile, "r") as fp:
        return w3.eth.contract(address=Web3.toChecksumAddress(address), abi=fp.read())


def transaction(func: callable, args: tuple):
    txn = func(*args).buildTransaction(TXNS_DETAILS)
    stxn = w3.eth.account.sign_transaction(txn, private_key=wallet)
    sent = w3.eth.send_raw_transaction(stxn.rawTransaction)
    return sent, w3.eth.wait_for_transaction_receipt(sent)


with log_task("Connecting to Web3"):
    w3 = Web3(Web3.HTTPProvider(ENDPOINT))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

TXNS_DETAILS = {
    "chainId" : 137,
    "gas" : 239185,
    "gasPrice" : w3.toWei('1', 'gwei'),
    "nonce" : w3.eth.getTransactionCount(MY_ADDRESS),
}


with log_task("Reading contracts"):
    masterchef = read_contract(**CONTRACTS["MASTERCHEF"])
    router = read_contract(**CONTRACTS["ROUTER"])
    pzap = read_contract(**CONTRACTS["PZAP"])
    pair = read_contract(**CONTRACTS["PAIR"])


with log_task("Opening wallet"):
    with open(KEYFILE) as fp:
        wallet_pass = getpass.getpass("Enter wallet password: ")
        wallet = w3.eth.account.decrypt(fp.read(), wallet_pass)


with log_task("Getting pool data"):
    pending_amount = masterchef.functions.pendingPZap(STAKED_POOL_ID, MY_ADDRESS).call()
    print(f"PZAP-BTC - Pending PZap: {amountToPZAP(pending_amount)}", end=" ")


with log_task("Checking harvest time"):
    canHarvest = masterchef.functions.canHarvest(STAKED_POOL_ID, MY_ADDRESS).call()
if not canHarvest:
    remaining = masterchef.functions.getHarvestUntil(11, MY_ADDRESS).call()
    dt = datetime.fromtimestamp(remaining)
    print(f"\nCan't harvest yet.\nHarvest unlocks at: {dt.strftime(DATETIME_FORMAT)}")
    exit(1)


with log_task("Harvesting"):
    txn, rcpt = transaction(
        masterchef.functions.deposit, 
        (STAKED_POOL_ID, 0)
    )
    print(f"\nTransaction: {txn}")
    print(f"Block Hash: {rcpt.blockHash.hex()}")
    print(f"Gas Used: {rcpt.gasUsed}")


with log_task("Buying WBTC with half of harvest"):
    amountIn = int(pzap.functions.balanceOf(MY_ADDRESS).call() / 1.99)
    amountOutMin = router.functions.getAmountsOut(amountIn, SWAP_PATH).call()[-1]
    if amountOutMin <= 0:
        print("No liquidity")
        exit(1)
    deadline = (datetime.now() + timedelta(minutes=5)).timestamp()
    txn, rcpt = transaction(
        router.functions.swapExactTokensForTokens, 
        (amountIn, amountOutMin, SWAP_PATH, MY_ADDRESS, int(deadline))
    )
    print(f"\nTransaction: {txn}")
    print(f"Block Hash: {rcpt.blockHash.hex()}")
    print(f"Gas Used: {rcpt.gasUsed}")


with log_task("Adding liquidity"):
    amountADesired = amountAMin = pzap.functions.balanceOf(MY_ADDRESS).call()
    amountBDesired = amountBMin = router.functions.getAmountsOut(amountADesired, SWAP_PATH).call()[1]
    deadline = (datetime.now() + timedelta(minutes=5)).timestamp()
    txn, rcpt = transaction(
        router.functions.addLiquidity, 
        (SWAP_PATH[0], SWAP_PATH[1], amountADesired, amountAMin, amountBDesired, amountBMin, MY_ADDRESS, int(deadline))
    )
    print(f"\nTransaction: {txn}")
    print(f"Block Hash: {rcpt.blockHash.hex()}")
    print(f"Gas Used: {rcpt.gasUsed}")


with log_task("Staking LPs"):
    lps_to_stake = pair.functions.balanceOf(MY_ADDRESS).call()
    txn, rcpt = transaction(
        router.functions.deposit, 
        (STAKED_POOL_ID, lps_to_stake)
    )
    print(f"\nTransaction: {txn}")
    print(f"Block Hash: {rcpt.blockHash.hex()}")
    print(f"Gas Used: {rcpt.gasUsed}")

print("Finished compounding")