from contextlib import contextmanager

# To transform between the 'amount' unit and PZAP you need this UNIT_MULTIPLIER
#   AMOUNT = PZAP * UNIT_MULTIPLIER
#   20000000000000000 = 0.02 * 1000000000000000000
UNIT_MULTIPLIER = 1000000000000000000


def amountToPZAP(amount: int) -> str:
    return f"{amount / UNIT_MULTIPLIER:.8f}"


def PZAPToAmount(pzap: str) -> int:
    return int(float(pzap) * UNIT_MULTIPLIER)
