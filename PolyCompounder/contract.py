from pathlib import Path

from web3 import Web3

from config import RESOURCES

class ContractManager:
    """
    Stores contract definitions (address and location of the abi file).
    Reads and returns contracts from the network.
    """

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

    def __init__(self, w3: Web3, parent: Path = RESOURCES):
        self.w3 = w3
        self.parent = parent

    def read_contract(self, name: str):
        if not name in self.CONTRACTS.keys():
            raise ValueError("Contract not found.")
        contract = self.CONTRACTS[name] 
        with open(self.parent / contract["abifile"], "r") as fp:
            return self.w3.eth.contract(
                address=Web3.toChecksumAddress(contract["address"]), 
                abi=fp.read()
            )

