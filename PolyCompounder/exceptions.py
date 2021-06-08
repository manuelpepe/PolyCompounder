class UnkownStrategyError(Exception): pass

class CompoundError(Exception):
    """ Base class for errors while compounding """
    pass

class HarvestNotAvailable(CompoundError): pass

class NoLiquidity(CompoundError): pass

