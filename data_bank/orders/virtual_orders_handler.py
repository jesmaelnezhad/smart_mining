import enum
import json
from time import sleep
from clock.clock import calculate_tick_duration_from_sleep_duration
from clock.tick_performer import TickPerformer
from configuration import EXECUTION_CONFIGS
from utility.log import logger
from clock import get_clock
from utility.persistent_object import PersistentObject
from utility.thread_safe_containers import ThreadSafeDictionary


def get_container_key_for_virtual_order_request(virtual_order_id, order_id):
    return "{0}-{1}".format(virtual_order_id, order_id)


class VirtualOrderRequest(PersistentObject):
    class Status(enum.Enum):
        OK = "ok"
        ORDER_NOT_FOUND = "order_not_found"

    POWER_LIMIT_REQUEST_KEY = "power_limit_request"
    REQUEST_CREATION_TIMESTAMP_KEY = "power_limit_request"
    REQUEST_EXPIRATION_TIMESTAMP_KEY = "power_limit_request"
    STATUS_KEY = "status"

    def __init__(self, virtual_order_id, order_id, power_limit_request,
                 request_creation_timestamp,
                 request_expiration_timestamp):
        super(VirtualOrderRequest, self).__init__(virtual_order_id, order_id)
        self[self.POWER_LIMIT_REQUEST_KEY] = float(power_limit_request)
        self[self.REQUEST_CREATION_TIMESTAMP_KEY] = int(request_creation_timestamp)
        self[self.REQUEST_EXPIRATION_TIMESTAMP_KEY] = int(request_expiration_timestamp)
        self[self.STATUS_KEY] = VirtualOrderRequest.Status.OK

    def recast_attr_types_after_load(self):
        self[self.POWER_LIMIT_REQUEST_KEY] = float(self[self.POWER_LIMIT_REQUEST_KEY])
        self[self.REQUEST_CREATION_TIMESTAMP_KEY] = int(self[self.REQUEST_CREATION_TIMESTAMP_KEY])
        self[self.REQUEST_EXPIRATION_TIMESTAMP_KEY] = int(self[self.REQUEST_EXPIRATION_TIMESTAMP_KEY])
        self[self.STATUS_KEY] = VirtualOrderRequest.Status(self[self.STATUS_KEY])

    def get_virtual_order_id(self):
        return self.owner

    def get_order_id(self):
        return self.strategy_execution_id

    def get_power_limit_request(self):
        return self[self.POWER_LIMIT_REQUEST_KEY]

    def get_request_creation_timestamp(self):
        return self[self.REQUEST_CREATION_TIMESTAMP_KEY]

    def get_request_expiration_timestamp(self):
        return self[self.REQUEST_EXPIRATION_TIMESTAMP_KEY]

    def is_valid_at(self, up_to_timestamp=None):
        if up_to_timestamp is None:
            up_to_timestamp = get_clock().read_timestamp_of_now()
        return self.get_request_expiration_timestamp() < up_to_timestamp

    def set_status(self, status):
        self[self.STATUS_KEY] = status

    def get_status(self):
        return self[self.STATUS_KEY]


class VirtualOrderThreadSafePersistentContainer(ThreadSafeDictionary):
    VIRTUAL_ORDERS_CONTAINER_OWNER = "virtual_orders_container"
    VIRTUAL_ORDERS_CONTAINER_DATA_KEY = "data"

    def __init__(self, orders_db_handler):
        super(VirtualOrderThreadSafePersistentContainer, self).__init__()
        self.orders_db = orders_db_handler

    def load_last_order_data_from_database(self):
        json_str = self.orders_db.key_value_get(self.VIRTUAL_ORDERS_CONTAINER_OWNER,
                                                self.VIRTUAL_ORDERS_CONTAINER_DATA_KEY)
        if json_str is None:
            # First time working with this database. Set an empty dictionary.
            value = json.dumps(dict())
            self.orders_db.key_value_put(self.VIRTUAL_ORDERS_CONTAINER_OWNER,
                                         self.VIRTUAL_ORDERS_CONTAINER_DATA_KEY,
                                         value)
            return
        # Load the json from the json_str
        virtual_orders = json.loads(json_str)
        self.bulk_insert(virtual_orders)

    def save_order_data_in_database(self):
        data = self.snapshot()
        data_json = json.dumps(data)
        self.orders_db.key_value_put(self.VIRTUAL_ORDERS_CONTAINER_OWNER,
                                     self.VIRTUAL_ORDERS_CONTAINER_DATA_KEY,
                                     data_json)

    def remove_expired_orders(self, up_to_timestamp=None):
        self.clear_by_predicate(VirtualOrderRequest.is_valid_at, {'up_to_timestamp': up_to_timestamp})

    def set_virtual_order_request(self, virtual_order_id, order_id, power_limit_request,
                                  creation_timestamp,
                                  expiration_timestamp):
        virtual_order_obj = VirtualOrderRequest(virtual_order_id=virtual_order_id, order_id=order_id,
                                                power_limit_request=power_limit_request,
                                                request_creation_timestamp=creation_timestamp,
                                                request_expiration_timestamp=expiration_timestamp)
        self.set(get_container_key_for_virtual_order_request(virtual_order_id=virtual_order_id, order_id=order_id),
                 virtual_order_obj)

    def set_virtual_order_request_status(self, virtual_order_id, order_id, status):
        self.set(get_container_key_for_virtual_order_request(virtual_order_id=virtual_order_id, order_id=order_id),
                 VirtualOrderRequest.set_status, {'status': status})

    def delete_virtual_order_request(self, virtual_order_id, order_id):
        self.unset(get_container_key_for_virtual_order_request(virtual_order_id=virtual_order_id, order_id=order_id))

    def get_virtual_order_request(self, virtual_order_id, order_id):
        """

        :param virtual_order_id:
        :param order_id:
        :return: Tuple (power limit request, creation ts, expiration ts)
        """
        virtual_order_obj = self.get(
            get_container_key_for_virtual_order_request(virtual_order_id=virtual_order_id, order_id=order_id))
        if virtual_order_obj is None:
            return None
        return (virtual_order_obj.get_power_limit_request(),
                virtual_order_obj.get_request_creation_timestamp(),
                virtual_order_obj.get_request_expiration_timestamp(),)

    def get_overall_requests(self, up_to_timestamp=None):
        """
        Returns the sums grouped by order_id
        :return: a dictionary from order_id to tuple of (list of power limits, list of virtual order ids)
        """
        data = self.snapshot()
        order_buckets_limits = dict()
        order_buckets_virtual_order_ids = dict()
        for container_virtual_order_key, virtual_order_request in data.items():
            is_valid = virtual_order_request.is_valid_at(up_to_timestamp=up_to_timestamp)
            if not is_valid:
                continue
            power_limit_request = virtual_order_request.get_power_limit_request()
            virtual_order_id = virtual_order_request.get_virtual_order_id()
            order_id = virtual_order_request.get_order_id()
            if order_id not in order_buckets_limits.keys():
                order_buckets_limits[order_id] = list()
                order_buckets_virtual_order_ids[order_id] = list()
            order_buckets_limits[order_id].append(power_limit_request)
            order_buckets_virtual_order_ids[order_id].append(virtual_order_id)
        return {order_id: (order_buckets_limits[order_id], order_buckets_virtual_order_ids[order_id]) for order_id in
                order_buckets_limits.keys()}


class VirtualOrdersUpdater(TickPerformer):
    def __init__(self, orders_db_handler):
        """
        A singleton class that is the driver of nicehash
        """
        super().__init__()
        self.tick_duration = calculate_tick_duration_from_sleep_duration(
            EXECUTION_CONFIGS.virtual_order_updater_sleep_duration)
        self.virtual_orders = VirtualOrderThreadSafePersistentContainer(orders_db_handler=orders_db_handler)

    def run(self, should_stop):
        self.virtual_orders.load_last_order_data_from_database()
        while True:
            if should_stop():
                break
            sleep(self.tick_duration)
            current_timestamp = get_clock().read_timestamp_of_now()
            # remove expired orders
            self.virtual_orders.remove_expired_orders(up_to_timestamp=current_timestamp)
            # save virtual orders in database
            self.virtual_orders.save_order_data_in_database()

    def post_run(self):
        logger('virtual order/updater').info("Updater is terminating.")

    def is_a_daemon(self):
        return True
