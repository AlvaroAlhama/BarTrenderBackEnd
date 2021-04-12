import math

def truncate(number, decimals=0):

    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return math.trunc(number)

    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor


def get_commission(cost, scanned_num):

    percentage = 0.0
    if 0.5 <= cost < 2.0:
        percentage = 0.025
    elif 2 <= cost < 7.0:
        percentage = 0.03
    elif cost >= 7.0:
        percentage = 0.05

    return truncate(cost * scanned_num * percentage, 3)
