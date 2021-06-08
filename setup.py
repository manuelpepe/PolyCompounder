#!/usr/bin/env python

from distutils.core import setup

setup(
    name='PolyCompounder',
    version='1.0',
    description='Pool Auto Compounder for the Polygon (MATIC) network',
    author='Manuel Pepe',
    author_email='manuelpepe-dev@outlook.com.ar',
    entry_points={
        'console_scripts': [
            'polycompound = PolyCompounder.cli:main',
        ],
    },
    packages=[
        'PolyCompounder',
        'PolyCompounder.resources',
    ],
    install_requires=[
        "web3",
        "hexbytes"
    ]
)