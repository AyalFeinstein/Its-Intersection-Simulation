from fractions import Fraction
from math import sqrt, sin, cos, radians, pow
from constants import ROUNDING, PI


def cal_distance(z):
    """ Calculate the distance between two points. takes a tuple of x1, y1, x2, y2. """
    x0, y0, x1, y1 = z
    a = x0 - x1
    b = y0 - y1
    return sqrt(a * a + b * b)

def cos_degrees(d: float) -> float:
    return round(cos(radians(d)), ROUNDING)

def sin_degrees(d: float) -> float:
    return round(sin(radians(d)), ROUNDING)


def quadratic_equation(a, b, c) -> set:
    """ Help solve quadratic equations. """
    bsm4ac = b * b - 4 * (a*c)
    if bsm4ac < 0:
        return set()
    elif a == 0 and b == 0:
        return set()
    elif a == 0:
        return {-c / b}
    else:
        sl1 = (-b + bsm4ac) / (2 * a)
        sl2 = (-b - sqrt(b * b - 4 * (a*c))) / (2 * a)
        return {sl1, sl2}


def split_vector(magnitude, angle) -> tuple[float, float]:
    x = cos_degrees(angle)*magnitude
    y = sin_degrees(angle)*magnitude
    return x, y


def dot(x0, y0, x1, y1) -> float:
    """ dot finds the component of (x0, y0) in the direction of (x1, y1) """
    if sqrt(x1*x1 + y1*y1) == 0:
        return 0
    return (x0 * x1 + y0 * y1)/sqrt(x1*x1 + y1*y1)


def pythagorian_thereom(a, b):
    return sqrt(a*a + b*b)


def calc_vol_sphere(r):
    return (4/3)*PI*pow(r, 3)

def cal_length_compared_to_screen(ratio: tuple[float, float], length):
    return length*ratio[0]/ratio[1]
