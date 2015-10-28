
import math


def convert_distance_to_meters(distance, units):
    """"Returns distance in meters

    units passed through using radio buttons.

    convert kilometers to meters
    >>> convert_distance_to_meters(5, "kilometers")
    5000

    convert miles to meters
    >>> convert_distance_to_meters(1, "miles")
    1609.34

    should leave meters alone
    >>> convert_distance_to_meters(10000, "meters")
    10000

    """
    if units == "kilometers":
        meters = distance * 1000

    elif units == "miles":
        meters = distance * 1609.34

    else:
        meters = distance

    return meters

# TODO, looking at MapMyRun to see how to deal with passing in and limiting input
def convert_to_minutes():
    """Converts time to minutes as a decimal

    test for hours to minutes

    test for seconds to decimal
    test for

    """
    pass
    # minutes = 0
    # multiply minutes by 60 ==> seconds
    # use modlus (%) to get seconds
    # return minutes


def velocity(distance, time):
    """Returns velocity

    >>> velocity(1000, 5)
    200

    >>> velocity(0, 5)
    0

    >>> velocity(1000, 0)
    Traceback (most recent call last):
        ...
    ZeroDivisionError: integer division or modulo by zero

    """
    # don't want this to ever be negative.
    # >>> velocity(3000, -10)
    # -300
    # >>> velocity(-3000, 10)
    # -300

    velocity = distance/time
    return velocity


def get_velocity_from_VO2(VO2):
    """Returns velocity given VO2

    >>> get_velocity_from_VO2(60)
    302.41418000000004

    """
    vel = 29.54 + 5.000663 * VO2 - 0.007546 * VO2**2
    return vel


def get_VO2_from_velocity(velocity):
    """Returns VO2 give velocity

    >>> get_VO2_from_velocity(303)
    60.172309999999996

    """
    VO2 = -4.60 + 0.182258 * velocity + 0.000104 * velocity**2
    return VO2

# todo velocity --> pace min/mile

def get_percent_VO2max(time):
    """Returns perctenage of VO2max


    >>> get_percent_VO2max(9)
    1.0213666896324893

    """
    exponent1 = math.exp(-0.012778 * time)
    exponent2 = math.exp(-0.1932605 * time)
    percent_VO2max = 0.8 + 0.1894393 * exponent1 + 0.2989558 * exponent2
    return percent_VO2max


def user_VO2max():
    """Returns user VO2max



    """


if __name__ == "__main__":
    import doctest
    doctest.testmod()
