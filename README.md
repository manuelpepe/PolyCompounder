# PolyCompounder

Pool Auto Compounder for the Polygon (MATIC) network.

This project implemented used [PyAutoBlockchain (pab)](https://github.com/manuelpepe/PyAutoBlockchain).

The strategy implemented will:

* Check if pool rewards can be harvested
* Harvest rewards
* Swap half available balance of one token for another
* Create LP tokens using both coins
* Stake the new LP tokens