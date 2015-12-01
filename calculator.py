
import math


def convert_distance_to_meters(distance, units):
    """Return distance in meters

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


def meters_to_miles(meters):
    """Convert meters to miles

    >>> meters_to_miles(5000)
    3.106863683249034

    """
    miles = meters / 1609.34
    return miles


def miles_to_meters(miles):
    """Convert miles to meters

    >>> miles_to_meters(3.1)
    4988.954

    """
    meters = miles * 1609.34
    return meters


def hours_to_minutes(hours):
    """Return hours given minutes

    >>> hours_to_minutes(2)
    120

    """
    minutes = hours * 60
    return minutes


def seconds_to_minutes(seconds):
    """Return minutes given seconds

    >>> seconds_to_minutes(60)
    1.0

    >>> seconds_to_minutes(50)
    0.8333333333333334

    >>> seconds_to_minutes(90)
    1.5

    """
    minutes = seconds / 60.0
    return minutes
    # minutes = 0
    # multiply minutes by 60 ==> seconds
    # use modlus (%) to get seconds
    # return minutes


def velocity(distance, time):
    """Return velocity

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
    """Return velocity given VO2

    >>> get_velocity_from_VO2(60)
    302.41418000000004

    """
    vel = 29.54 + 5.000663 * VO2 - 0.007546 * VO2**2
    return vel


def get_VO2_from_velocity(velocity):
    """Return VO2 give velocity

    >>> get_VO2_from_velocity(303)
    60.172309999999996

    """
    VO2 = -4.60 + 0.182258 * velocity + 0.000104 * velocity**2
    return VO2


def velocity_to_min_per_mile(velocity):
    """Return minutes per mile"""
    pace = 1609.34 / velocity
    # pace is in min/mile; min is a decimal
    # seconds = int((pace * 60) % 60)
    # # returns the seconds rounded down = faster time
    # if seconds > 10:
    #     seconds = "0{}".format(seconds)
    # pace = str(pace).split(".")
    # pace = "{}:{}".format(pace[0], seconds)
    return pace


def get_percent_VO2max(time):
    """Returns perctenage of VO2max


    >>> get_percent_VO2max(9)
    1.0213666896324893

    """
    exponent1 = math.exp(-0.012778 * time)
    exponent2 = math.exp(-0.1932605 * time)
    percent_VO2max = 0.8 + 0.1894393 * exponent1 + 0.2989558 * exponent2
    return percent_VO2max


def user_VDOT(distance, units, time):
    """Returns user VO2max

    >>> user_VDOT(10, "kilometers", 35)
    60.54544105206188


    >>> user_VDOT(5000, "meters", 17)
    60.160686884379935

    >>> user_VDOT(2, "miles", 10.5)
    60.741639616661146

    """
    percent_VO2 = get_percent_VO2max(time)
    # may need more calc for time, assuming all min for now
    meters = convert_distance_to_meters(distance, units)
    vel = velocity(meters, time)
    race_VO2 = get_VO2_from_velocity(vel)

    VDOT = race_VO2 / percent_VO2
    return VDOT


# examples of how to use datetime.timedelta
# >>> hr = 1
# >>> mm = 60
# >>> ss = 3600
# >>>
# >>> minutes = datetime.timedelta(hours=hr, minutes=mm, seconds=ss)
# >>> print minutes
# 3:00:00
# >>> race_time = 65.25
# >>> datetime.timedelta(minutes=race_time)
# datetime.timedelta(0, 3915)
# >>> race_time = datetime.timedelta(minutes=race_time)
# >>> print race_time
# 1:05:15

if __name__ == "__main__":
    import doctest
    doctest.testmod()
