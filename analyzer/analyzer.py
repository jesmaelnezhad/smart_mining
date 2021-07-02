from statistics import mean
from threading import Lock
from time import sleep

from clock import get_clock
from clock.clock import calculate_tick_duration_from_sleep_duration
from clock.tick_performer import TickPerformer
from configuration import EXECUTION_CONFIGS
from data_bank.blocks import MineDatabaseHandler
from utility.datetime_helpers import size_in_seconds
from utility.log import logger
from configuration import constants


class AverageWindowMetric:
    """
    Any metric that is calculated in a short window, and is averaged over
    all instances of such window over a larger time window in the past
    """

    def __init__(self, short_window_length_seconds, large_window_length_seconds):
        self.short_window_length = short_window_length_seconds
        self.large_window_length = large_window_length_seconds
        self.latest_timestamp = None
        self.window_values = None
        self.window_values_mutex = Lock()

    def set_latest_timestamp(self, latest_timestamp):
        """
        Sets the ending point of the large window. Setting this property invalidates the window_values
        :param latest_timestamp:
        :return:
        """
        self.window_values_mutex.acquire()
        try:
            self.latest_timestamp = latest_timestamp
            self.window_values = None
        finally:
            self.window_values_mutex.release()

    def get_short_window_boundaries(self, latest_timestamp=None):
        """
        Calculates the boundaries of the short windows that exist in the larger interval
        :param latest_timestamp: the larger window is defined by its length and its end point which is this argument
        :return: the list of window boundaries from latest to oldest
        """

        # check if input latest timestamp parameter is not null, then add it as latest timestamp variable of the object
        if latest_timestamp is not None:
            self.set_latest_timestamp(latest_timestamp)
        # if object has not latest timestamp value yet, short window boundaries cannot be set
        if self.latest_timestamp is None:
            return None
        # set short window boundaries if object has latest timestamp value
        self.window_values_mutex.acquire()
        try:
            window_boundaries = []
            next_boundary = self.latest_timestamp
            while ((self.latest_timestamp - next_boundary) + self.short_window_length) <= self.large_window_length:
                window_boundaries.append(next_boundary)
                next_boundary -= self.short_window_length
            return window_boundaries
        finally:
            self.window_values_mutex.release()

    def update_window_values(self):
        """
        Updates the window values
        :return: None
        """
        window_boundaries, window_values = self.calculate_new_window_values_and_boundaries()
        new_window_info = []
        new_boundaries = self.get_short_window_boundaries()
        if self.latest_timestamp is None:
            new_window_info = None
        elif window_boundaries != new_boundaries or len(window_values) != len(window_boundaries):
            new_window_info = None
        else:
            for i in range(0, len(window_boundaries)):
                new_window_info.append((window_boundaries[i], window_values[i],))
        self.window_values_mutex.acquire()
        try:
            self.window_values = new_window_info
        finally:
            self.window_values_mutex.release()

    def get_window_values(self):
        """
        Returns a list of all values where, the latest window's info is in the first element
        :return: A list of tuples like (window_ending_boundary, value)
        """
        self.window_values_mutex.acquire()
        try:
            if self.window_values is None:
                return None
            return self.window_values.copy()
        finally:
            self.window_values_mutex.release()

    def get_average_on_all_values(self):
        return mean([v[1] for v in self.get_window_values()])

    def calculate_new_window_values_and_boundaries(self):
        """
        When called, the object should return a tuple of two lists like (new_boundaries, new_values)
        :return:
        """
        pass

    def get_identifier_key(self):
        """
        returns a string to specify the type of this metric
        :return: name of the identifier
        """
        pass


class AveragePoolBlockCount(AverageWindowMetric):
    def calculate_new_window_values_and_boundaries(self):
        """
        When called, calculates block count of a pool on window boundaries
        :return: a tuple of two lists in this order (boundaries, values)
        """
        # get boundary values
        boundaries = self.get_short_window_boundaries()
        # get data from database to fill data
        values = []
        mine_db_handler = MineDatabaseHandler(EXECUTION_CONFIGS.db_user, EXECUTION_CONFIGS.db_password)
        for i in range(0, len(boundaries)):
            end_timestamp = boundaries[i]
            begin_timestamp = end_timestamp - self.short_window_length
            values.append(len(mine_db_handler.get_blocks_between(begin_timestamp, end_timestamp)))
        return boundaries, values

    def get_identifier_key(self):
        return constants.METRIC_POOL_BLOCK_COUNT_IDENTIFIER


class AveragePoolHashPower(AverageWindowMetric):
    def calculate_new_window_values_and_boundaries(self):
        """
        When called, calculates average pool hash power on window boundaries
        :return: a tuple of two list in this order (boundaries, values)
        """
        # get boundary values
        boundaries = self.get_short_window_boundaries()
        # get data from database to fill data
        values = []
        mine_db_handler = MineDatabaseHandler(EXECUTION_CONFIGS.db_user, EXECUTION_CONFIGS.db_password)
        for i in range(0, len(boundaries)):
            end_timestamp = boundaries[i]
            begin_timestamp = end_timestamp - self.short_window_length
            data = mine_db_handler.get_slushpool_info(begin_timestamp, end_timestamp,
                                                      True, ['hash_rate'])
            raw_data = []
            for record in data:
                raw_data.append((record[0], record[1][0]))
            values.append(get_weighted_average(begin_timestamp, end_timestamp, raw_data))
        return boundaries, values

    def get_identifier_key(self):
        return constants.METRIC_POOL_HASH_POWER_IDENTIFIER


class AveragePoolActiveWorkers(AverageWindowMetric):
    def calculate_new_window_values_and_boundaries(self):
        """
        When called, calculates average pool active workers on window boundaries
        :return: a tuple of two list in this order (boundaries, values)
        """
        # get boundary values
        boundaries = self.get_short_window_boundaries()
        # get data from database to fill data
        values = []
        mine_db_handler = MineDatabaseHandler(EXECUTION_CONFIGS.db_user, EXECUTION_CONFIGS.db_password)
        for i in range(0, len(boundaries)):
            end_timestamp = boundaries[i]
            begin_timestamp = end_timestamp - self.short_window_length
            data = mine_db_handler.get_slushpool_info(begin_timestamp, end_timestamp,
                                                      True, ['active_workers'])
            raw_data = []
            for record in data:
                raw_data.append((record[0], record[1][0]))
            values.append(get_weighted_average(begin_timestamp, end_timestamp, raw_data))
        return boundaries, values

    def get_identifier_key(self):
        return constants.METRIC_POOL_ACTIVE_WORKERS_IDENTIFIER


class AveragePoolActiveUsers(AverageWindowMetric):
    def calculate_new_window_values_and_boundaries(self):
        """
        When called, calculates average pool active users on window boundaries
        :return: a tuple of two list in this order (boundaries, values)
        """
        # get boundary values
        boundaries = self.get_short_window_boundaries()
        # get data from database to fill data
        values = []
        mine_db_handler = MineDatabaseHandler(EXECUTION_CONFIGS.db_user, EXECUTION_CONFIGS.db_password)
        for i in range(0, len(boundaries)):
            end_timestamp = boundaries[i]
            begin_timestamp = end_timestamp - self.short_window_length
            data = mine_db_handler.get_slushpool_info(begin_timestamp, end_timestamp,
                                                      True, ['active_users'])
            raw_data = []
            for record in data:
                raw_data.append((record[0], record[1][0]))
            values.append(get_weighted_average(begin_timestamp, end_timestamp, raw_data))
        return boundaries, values

    def get_identifier_key(self):
        return constants.METRIC_POOL_ACTIVE_USERS_IDENTIFIER
    

class AveragePoolScoringHashPower(AverageWindowMetric):
    def calculate_new_window_values_and_boundaries(self):
        """
        When called, calculates average pool scoring hash power on window boundaries
        :return: a tuple of two list in this order (boundaries, values)
        """
        # get boundary values
        boundaries = self.get_short_window_boundaries()
        # get data from database to fill data
        values = []
        mine_db_handler = MineDatabaseHandler(EXECUTION_CONFIGS.db_user, EXECUTION_CONFIGS.db_password)
        for i in range(0, len(boundaries)):
            end_timestamp = boundaries[i]
            begin_timestamp = end_timestamp - self.short_window_length
            data = mine_db_handler.get_slushpool_info(begin_timestamp, end_timestamp,
                                                      True, ['scoring_hash_rate'])
            raw_data = []
            for record in data:
                raw_data.append((record[0], record[1][0]))
            values.append(get_weighted_average(begin_timestamp, end_timestamp, raw_data))
        return boundaries, values

    def get_identifier_key(self):
        return constants.METRIC_POOL_SCORING_HASH_POWER_IDENTIFIER


class AverageNetworkHashPower(AverageWindowMetric):
    def calculate_new_window_values_and_boundaries(self):
        """
        When called, calculates average network hash power on window boundaries
        :return: a tuple of two list in this order (boundaries, values)
        """
        # get boundary values
        boundaries = self.get_short_window_boundaries()
        # TODO get data from database
        values = []
        return boundaries, values

    def get_identifier_key(self):
        return constants.METRIC_NETWORK_HASH_POWER_IDENTIFIER


class AverageNetworkBlockCount(AverageWindowMetric):
    def calculate_new_window_values_and_boundaries(self):
        """
        When called, calculates block counts of network on window boundaries
        :return: a tuple of two list in this order (boundaries, values)
        """
        # get boundary values
        boundaries = self.get_short_window_boundaries()
        # TODO get data from database
        values = []
        return boundaries, values

    def get_identifier_key(self):
        return constants.METRIC_NETWORK_BLOCK_COUNT_IDENTIFIER


class RecentHistoryStatistics:
    def __init__(self):
        # Each member is a tuple window average window metric container
        self.average_window_metric_containers = [
            AveragePoolBlockCount(short_window_length_seconds=size_in_seconds(days=1),
                                  large_window_length_seconds=size_in_seconds(days=10)),
            AveragePoolBlockCount(short_window_length_seconds=size_in_seconds(days=1),
                                  large_window_length_seconds=size_in_seconds(days=50)),
            AveragePoolBlockCount(short_window_length_seconds=size_in_seconds(days=1),
                                  large_window_length_seconds=size_in_seconds(days=250)),
            AveragePoolHashPower(short_window_length_seconds=size_in_seconds(days=1),
                                 large_window_length_seconds=size_in_seconds(days=10)),
            AveragePoolHashPower(short_window_length_seconds=size_in_seconds(days=1),
                                 large_window_length_seconds=size_in_seconds(days=50)),
            AveragePoolHashPower(short_window_length_seconds=size_in_seconds(days=1),
                                 large_window_length_seconds=size_in_seconds(days=250)),
            AverageNetworkHashPower(short_window_length_seconds=size_in_seconds(days=1),
                                    large_window_length_seconds=size_in_seconds(days=10)),
            AverageNetworkHashPower(short_window_length_seconds=size_in_seconds(days=1),
                                    large_window_length_seconds=size_in_seconds(days=50)),
            AverageNetworkHashPower(short_window_length_seconds=size_in_seconds(days=1),
                                    large_window_length_seconds=size_in_seconds(days=250))
        ]

    def get_identifier(self):
        identifier_list = []
        for metric in self.average_window_metric_containers:
            identifier_list.append("{0}-{1}-{2}".format(metric.get_identifier_key(),
                                                        metric.short_window_length,
                                                        metric.large_window_length))
        return identifier_list


class Analyzer(TickPerformer):
    def __init__(self):
        """
        A singleton class that is the analyzer
        """
        super().__init__()
        self.tick_duration = calculate_tick_duration_from_sleep_duration\
            (EXECUTION_CONFIGS.analyzer_sleep_duration)
        self.statistics = RecentHistoryStatistics()

    def run(self, should_stop):
        while True:
            if should_stop():
                break
            messages = dict()
            try:
                self.message_box_changed.acquire()
                self.message_box_changed.wait(self.tick_duration)
                messages = self.message_box.snapshot(should_clear=True)
            finally:
                self.message_box_changed.release()
            current_timestamp = get_clock().read_timestamp_of_now()
            self.update_stats(current_timestamp, messages)
            logger('analyzer').debug("Updating analytics at timestamp {0}.".format(current_timestamp))

    def post_run(self):
        logger('analyzer').info("Analyzer is terminating.")

    def is_a_daemon(self):
        return False

    def update_stats(self, current_timestamp, messages):
        metric_container = self.statistics.average_window_metric_containers
        for stat in metric_container:
            stat.set_latest_timestamp(current_timestamp)
            stat.update_window_values()


def get_weighted_average(begin_timestamp, end_timestamp, raw_data):
    """
    returns weighted average of a parameter on a time span
    :parameter begin_timestamp: start timestamp of time span
    :parameter end_timestamp: end timestamp of time span
    :parameter raw_data: list of tuples of the format (moment, value)
    :return: averaged value of the parameter on specified time span
    """
    # first check for order of timestamp values
    if end_timestamp < begin_timestamp:
        begin_timestamp, end_timestamp = end_timestamp, begin_timestamp

    # sort list from oldest to newest values
    # TODO sort list

    # calculate average value
    value = 0
    time_span = end_timestamp - begin_timestamp
    for i in range(0, len(raw_data)):
        if i == 0:
            lower_timestamp = begin_timestamp - (raw_data[i][0] - begin_timestamp)
        else:
            lower_timestamp = raw_data[i - 1][0]
        if i == len(raw_data) - 1:
            higher_timestamp = end_timestamp + (end_timestamp - raw_data[i][0])
        else:
            higher_timestamp = raw_data[i + 1][0]
        value += (higher_timestamp - lower_timestamp) / 2 / time_span * raw_data[i][1]

    return value
