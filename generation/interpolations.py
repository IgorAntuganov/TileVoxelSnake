import math


def interpolate_linear(a: float, b: float, p: float) -> float:
    return a + p * (b - a)


def interpolate_cos(a: float, b: float, p: float) -> float:
    p = (1 - math.cos(p * math.pi / 2)) ** .5
    return a * (1 - p) + b * p


def interpolate_sigmoid(a: float, b: float, p: float, level: int = 2):
    """0 <= level <= 3"""
    p = sigmoid_levels[level](p)
    return interpolate_linear(a, b, p)


sigmoid_levels = [
        lambda a: a,
        lambda a: -2 * a ** 3 + 3 * a ** 2,
        lambda a: 6 * a ** 5 - 15 * a ** 4 + 10 * a ** 3,
        lambda a: -20 * a ** 7 + 70 * a ** 6 - 84 * a ** 5 + 35 * a ** 4
    ]
