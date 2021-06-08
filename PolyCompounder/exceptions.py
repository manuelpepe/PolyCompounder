class UnkownStrategyError(Exception): pass

class CompoundError(Exception):
    """ Base class for errors while compounding """
    pass

class HarvestNotAvailable(CompoundError): 
    def __init__(self, message, next_at = None):
        super().__init__(message)
        self.next_at = next_at

class NoLiquidity(CompoundError): pass

