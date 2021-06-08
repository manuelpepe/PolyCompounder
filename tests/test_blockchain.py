import web3

def test_w3_connection(blockchain):
    assert isinstance(blockchain.w3, web3.Web3)
    assert blockchain.wallet is None and blockchain.owner is None

def test_load_wallet(blockchain):
    pass