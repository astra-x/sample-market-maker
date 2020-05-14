from decimal import Decimal
from market_maker.settings import settings

def toNearest(num, tickSize):
    """Given a number, round it to the nearest tick. Very useful for sussing float error
       out of numbers: e.g. toNearest(401.46, 0.01) -> 401.46, whereas processing is
       normally with floats would give you 401.46000000000004.
       Use this after adding/subtracting/multiplying numbers."""
    tickDec = Decimal(str(tickSize))
    return float((Decimal(round(num / tickSize, 0)) * tickDec))


def toNearest2(start_position_price,index):
    start_position_price=round(float(start_position_price)/settings.PRICE_MINIFICATION,1)
    if index < 0:
        price = start_position_price + settings.PRICE_INTERVAL * (index + 1)
    else:
        price = start_position_price + settings.PRICE_INTERVAL * index
    return price




def range_price_verifier(start_position_price):


    if start_position_price>=settings.MaxSetPrice:
        s=start_position_price-settings.MaxSetPrice
        start_position_price=settings.MaxSetPrice-s

    if start_position_price<=settings.MinSetPrice:
        s=settings.MinSetPrice-start_position_price
        start_position_price=settings.MinSetPrice+s

    if not settings.MinSetPrice<start_position_price <settings.MaxSetPrice:
        start_position_price=range_price_verifier(start_position_price)

    return start_position_price
