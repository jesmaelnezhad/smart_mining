import datetime

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