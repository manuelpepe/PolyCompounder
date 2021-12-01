# PolyCompounder

Automatic liquidity pool compounder for the Polygon Network.

| :exclamation:  THIS IMPLEMENTATION IS NOT MEANT TO BE USED. It has not been properly tested. This only serves as a [PAB](https://github.com/manuelpepe/PyAutoBlockchain) project example. |
|-----------------------------------------|

This project is implemented with [PyAutoBlockchain](https://github.com/manuelpepe/PyAutoBlockchain).

The `PZAPPoolCompoundStrategy` strategy will:

* Check if pool rewards can be harvested for PZAP-WBTC
* Harvest PZAP rewards
* Swap half available PZAP for WBTC
* Create PZAP-WBTC LP tokens
* Stake the new LP tokens


## Usage

This is not meant to be used, only serves as an example.

For info on how to run a PAB project see [PAB's README](https://github.com/manuelpepe/PyAutoBlockchain/blob/master/README.md)