DONE:
# Improve strategy dispatching (make waits non blocking)
# Log unhandled exceptions
# Email notifications

BACKLOG:

# Customize wait times (ASAP or delta e.g. 1 day)
# Retry on `web3.exceptions.TimeExhausted` exception (TransactionHandler)
```
 File "/root/PolyCompounder/PolyCompounder/cli.py", line 85, in run
    pounder.run()
  File "/root/PolyCompounder/PolyCompounder/core.py", line 23, in run
    task.compound()
  File "/root/PolyCompounder/PolyCompounder/strategy.py", line 56, in compound
    self.add_liquidity()
  File "/root/PolyCompounder/PolyCompounder/strategy.py", line 94, in add_liquidity
    self._transact(
  File "/root/PolyCompounder/PolyCompounder/strategy.py", line 30, in _transact
    res = self.blockchain.transact(func, args)
  File "/root/PolyCompounder/PolyCompounder/blockchain.py", line 57, in transact
    return self.txn_handler.transact(func, args)
  File "/root/PolyCompounder/PolyCompounder/transaction.py", line 34, in transact
    rcpt = self.w3.eth.wait_for_transaction_receipt(sent)
  File "/root/PolyCompounder/venv/lib/python3.9/site-packages/web3/eth.py", line 436, in wait_for_transaction_receipt
    raise TimeExhausted(
web3.exceptions.TimeExhausted: Transaction 0x78c12e33a0ea169f6ef2f468a90470ee3675cf775a3067e068c90649a441a812 is not in the chain, after 120 seconds
```
