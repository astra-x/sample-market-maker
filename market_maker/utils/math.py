from decimal import Decimal
from market_maker import settings

def toNearest(num, tickSize):
    """Given a number, round it to the nearest tick. Very useful for sussing float error
       out of numbers: e.g. toNearest(401.46, 0.01) -> 401.46, whereas processing is
       normally with floats would give you 401.46000000000004.
       Use this after adding/subtracting/multiplying numbers."""
    tickDec = Decimal(str(tickSize))
    return float((Decimal(round(num / tickSize, 0)) * tickDec))


def toNearest2(start_position,index):
    start_position=round(float(start_position)/settings.PRICE_MINIFICATION,1)
    if index < 0:
        price = start_position + settings.PRICE_INTERVAL * (index + 1)
    else:
        price = start_position + settings.PRICE_INTERVAL * index
    return price



