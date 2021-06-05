# PolyAutoCompounder

Pool Auto Compounder for the Polygon (MATIC) network.
Currently works for PZAP only.

## DISCLAIMER

This is a side-project, for personal use and learning purposes, and it may fall unmainteined in the future.
Even now I cannot assure completely correct handling of your tokens.
Don't use this with money you're afraid to lose. Maybe don't use it at all.
Read the code, use at your own discretion and always DYOR.

## Installation

Clone the repo and install dependencies.

```bash
	$ git clone https://github.com/manuelpepe/PolyAutoCompounder
	$ cd PolyAutoCompounder
 	$ python3.7 -m venv venv
	$ source venv/bin/activate
	$ pip install -r requirements.txt
```

## Configuration

### Configure wallet address and RPC 

Copy and edit the project config:

```bash
	$ cp PolyCompounder/resources/config.sample.json PolyCompounder/resources/config.json
    $ vim PolyCompounder/resources/config.json
```

You'll also need to create the file 
```
PolyCompounder/resources/key.file
```
with your encrypted private key.

To create one see [here](https://web3py.readthedocs.io/en/stable/troubleshooting.html#how-do-i-use-my-metamask-accounts-from-web3-py)

(TODO: `create-keyfile` script)


### Configure manager and compound tasks (WIP)

WIP

## Running

```bash
	$ python PolyCompounder/core.py
    Enter wallet password: 
```

## Extending

### Adding extra PZAP pairs

The easiest pairs to add are PZAP pairs.

1. Add the secondary token .abi file into resources and create a new entry for the ContractManager.
2. Extend `PZAPCompoundTask` and redefine class attributes.
3. Instanciate new task and pass to `Compounder`. 

In the future you should be able to add the abu file, configure the manager with a json file
and configure pairs to compond in a different json file. 