import json

from pathlib import Path

from web3 import Web3

from PolyCompounder.config import ABIS_DIR, CONTRACTS_FILE


class ContractManager:
    """
    Stores contract definitions (address and location of the abi file).
    Reads and returns contracts from the network.
    """

    def __init__(self, w3: Web3, parent: Path = ABIS_DIR):
        self.w3 = w3
        self.parent = parent
        self.contracts = self.load_contracts()
    
    def load_contracts(self):
        with open(Path.cwd() / CONTRACTS_FILE, "r") as fp:
            self.contracts = json.load(fp)
        return self.contracts

    def read_contract(self, name: str):
        if not name in self.contracts.keys():
            raise ValueError("Contract not found.")
        contract = self.contracts[name] 
        with open(self.parent / contract["abifile"], "r") as fp:
            return self.w3.eth.contract(
                address=Web3.toChecksumAddress(contract["address"]), 
                abi=fp.read()
            )

