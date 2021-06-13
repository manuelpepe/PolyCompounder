# PolyCompounder

Pool Auto Compounder for PZAP-WBTC in PolyZap.

This project implemented used [PyAutoBlockchain](https://github.com/manuelpepe/PyAutoBlockchain).

The strategy implemented will:

* Check if pool rewards can be harvested for PZAP-WBTC
* Harvest PZAP rewards
* Swap half available PZAP for WBTC
* Create PZAP-WBTC LP tokens
* Stake the new LP tokens

## DISCLAIMER

This is implementation serves as an example only.

I'm not assosiated with any of the farms/pools/blockchains mentioned in the project or any other crypto project.

Read the code, use at your own risk and always DYOR.


## Usage

Clone and setup virtualenv:
```
$ git clone https://github.com/manuelpepe/PolyCompounder
$ cd PolyCompounder/
$ python3.9 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

Create configs:
```
(venv) $ pab edit-config
(venv) $ pab create-keyfile
```

Run:
```
(venv) $ pab run
```