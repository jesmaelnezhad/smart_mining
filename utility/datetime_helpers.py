import datetime
from datetime import timedelta

from dateutil.relativedelta import relativedelta
import pytz


def datetime_string_to_timestamp(datetime_string, datetime_format="%m/%d/%Y-%H:%M:%S"):
    """
    Returns the timestamp of the given datetime string
    :param datetime_format: the format used to parse the given string
    :param datetime_string: a datetime string in the given format. If None is passed, the current timestamp is returned
    :return: the timestamp
    """
    if datetime_string is None:
        return datetime.datetime.now(tz=pytz.UTC).timestamp()

    date = datetime.datetime.strptime(datetime_string, datetime_format)
    return datetime.datetime.timestamp(date)


def calculate_delta_time_ago_timestamp(timestamp=datetime.now(tz=pytz.UTC).timestamp(), years=0, months=0, days=0,
                                       hours=0, minutes=0, seconds=0,
                                       calculate_time_ahead=False):
    """
    Calculates the timestamp of the datetime that has the given distance to
    the given timestamp (by default to its past).
    :param timestamp: the origin to calculate the result from. Default to timestamp of now
    :param years:
    :param months:
    :param days:
    :param hours:
    :param minutes:
    :param seconds:
    :param calculate_time_ahead: return this much time ahead instead. Defaults to False.
    :return: return the timestamp of the resulting time
    """
    t = datetime.datetime.fromtimestamp(timestamp, tz=pytz.UTC)
    if calculate_time_ahead:
        return t + relativedelta(years=years, months=months, days=days, hours=hours, minutes=minutes, seconds=seconds)
    else:
        return t - relativedelta(years=years, months=months, days=days, hours=hours, minutes=minutes, seconds=seconds)


def size_in_seconds(days, hours=0, minutes=0, seconds=0):
    """
    Returns the number of seconds in a window with the given characteristics
    :param days:
    :param hours:
    :param minutes:
    :param seconds:
    :return: Number of seconds
    """
    delta = datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    return int(delta.total_seconds())
