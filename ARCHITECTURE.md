# Project structure

The project structure is as follows:

![PolyCompounder entities structure](docs/Entities.png)

The `Blockchain` exposes the auth, transaction and contract interfaces, allowing strategies to interact with the
network and compound pools (or anything else).

You can inherit from `PolyCompounder.strategy.CompundStrategy` to create your own compounding strategies.
