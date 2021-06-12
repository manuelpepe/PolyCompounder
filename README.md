# PolyAutoCompounder


[![Tests](https://github.com/manuelpepe/PolyCompounder/actions/workflows/python-app.yml/badge.svg)](https://github.com/manuelpepe/PolyCompounder/actions/workflows/python-app.yml) 
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)

Pool Auto Compounder for the Polygon (MATIC) network.
Currently works for PZAP only.


## DISCLAIMER

This is a side-project, for personal use and learning purposes, and it may fall unmainteined in the future.

Even now I cannot assure completely correct handling of your tokens.

I'm not assosiated with any of the farms/pools/blockchains mentioned in the project or any other crypto project.

Don't use this with money you're afraid to lose. Maybe don't use it at all.

Read the code, use at your own discretion and always DYOR.


## Installation

Clone the repo and install dependencies.

```bash
$ git clone https://github.com/manuelpepe/PolyAutoCompounder
$ cd PolyCompounder
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ pip install -e .
```


## Usage

```bash
(venv) $ polycompound create-keyfile [-o keyfile]  # Create keyfile
(venv) $ polycompound edit-config  # Edit config file
(venv) $ polycompound list-strategies -v  # List available strategies and parameters
(venv) $ polycompound run  # Run compounding
```

## Configuration

### Configure wallet and RPC 

Create project config and keyfile:

```bash
(venv) $ polycompound edit-config
(venv) $ polycompound create-keyfile
```

You can get register at [MaticVigil](https://rpc.maticvigil.com/) for a free RPC account.

### Adding extra contracts

To use contracts in the strategies you first need to add the abi file to `resources/abis` and 
modify the `resources/contracts.json` file to load it.

For example, given the contract for `MYTOKEN` at `0x12345` create the abifile at `resources/abis/mytoken.abi` and add
to `resources/contracts.json` the following:

```json
{
    "MYTOKEN": {
        "address": "0x12345",
        "abifile": "mytoken.abi"
    }
}
```

### Adding extra strategies

You can add strategies to execute at `resources/strategies.json`.
For example, the following example defines 1 estrategy to execute, using the strategy `PZAPPoolCompoundStrategy` 
and the contracts `PZAP`, `WBTC`, `PAIR`, `MASTERCHEF` and `ROUTER`.

```json
[
    {
        "strategy": "PZAPPoolCompoundStrategy",
        "name": "PZAP-WBTC",
        "params": {
            "swap_path": ["PZAP", "WBTC"],
            "pair": "PAIR",
            "masterchef": "MASTERCHEF",
            "router": "ROUTER",
            "pool_id": 11
        }
    }
]
```

Strategies are dictionaries with:

* `strategy`: Class name of strategy (must be subclass of `PolyCompounder.strategy.CompoundStrategy`, see `polycompound list-strategies`)
* `name`: Name, just for logging.
* `params`: Dictionary with strategy parameters. (see `polycompound list-strategies -v`)

Run `polycompound list-strategies -v' to see available strategies and parameters.

### Email alerts

You can setup email alerts for when something goes wrong.
Add the following to your `resources/config.json`:

```json
{
    "emails": {
        "enabled": true,
        "host": "smtp.host.com",
        "port": 465,
        "address": "email@host.com",
        "password": "password",
        "recipient": "me@host.com"
    }   
}
```


## Developing

For details see [ARCHITECTURE.md](ARCHITECTURE.md)


### Running tests

Using pytest:

```bash
(venv) $ pip install -e requirements-dev.txt
(venv) $ ./tests.sh
```